"""
Model management and loading system for MLX-GUI.
Handles model lifecycle, queue management, and MLX-LM integration.
"""

import asyncio
import logging
import os
import threading
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, Optional, Any, List, Callable, AsyncGenerator, Tuple
from concurrent.futures import ThreadPoolExecutor
import threading

import mlx.core as mx
from sqlalchemy.orm import Session

from mlx_gui.database import get_database_manager, get_db_session
from mlx_gui.models import Model, ModelStatus, InferenceRequest, RequestQueue, QueueStatus
from mlx_gui.system_monitor import get_system_monitor
from mlx_gui.mlx_integration import get_inference_engine, MLXModelWrapper, GenerationConfig, GenerationResult

logger = logging.getLogger(__name__)


# Remove the broken custom executor - we'll use simple threading


class LoadingStatus(Enum):
    """Model loading status."""
    IDLE = "idle"
    LOADING = "loading"
    LOADED = "loaded"
    UNLOADING = "unloading"
    FAILED = "failed"


@dataclass
class LoadedModel:
    """Container for a loaded MLX model."""
    model_id: str
    mlx_wrapper: MLXModelWrapper  # The MLX model wrapper
    loaded_at: datetime
    last_used_at: datetime
    memory_usage_gb: float

    def update_last_used(self):
        """Update the last used timestamp."""
        self.last_used_at = datetime.utcnow()

    @property
    def config(self) -> Dict[str, Any]:
        """Get model configuration."""
        return self.mlx_wrapper.config


@dataclass
class LoadRequest:
    """Model loading request."""
    model_name: str
    model_path: str
    priority: int = 0
    requester_id: str = "system"
    callback: Optional[Callable] = None
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()


class ModelLoadingQueue:
    """Thread-safe queue for model loading requests."""

    def __init__(self):
        self._queue: List[LoadRequest] = []
        self._lock = threading.Lock()
        self._event = threading.Event()

    def add_request(self, request: LoadRequest) -> int:
        """Add a loading request to the queue."""
        with self._lock:
            self._queue.append(request)
            # Sort by priority (higher first), then by creation time
            self._queue.sort(key=lambda x: (-x.priority, x.created_at))
            position = self._queue.index(request)
            self._event.set()
            return position

    def get_next_request(self, timeout: Optional[float] = None) -> Optional[LoadRequest]:
        """Get the next request from the queue."""
        if timeout:
            self._event.wait(timeout)

        with self._lock:
            if self._queue:
                request = self._queue.pop(0)
                if not self._queue:
                    self._event.clear()
                return request
            return None

    def remove_request(self, model_name: str) -> bool:
        """Remove a request from the queue."""
        with self._lock:
            for i, request in enumerate(self._queue):
                if request.model_name == model_name:
                    self._queue.pop(i)
                    return True
            return False

    def get_queue_status(self) -> List[Dict[str, Any]]:
        """Get current queue status."""
        with self._lock:
            return [
                {
                    "model_name": req.model_name,
                    "priority": req.priority,
                    "requester_id": req.requester_id,
                    "created_at": req.created_at.isoformat(),
                    "position": i
                }
                for i, req in enumerate(self._queue)
            ]

    def size(self) -> int:
        """Get queue size."""
        with self._lock:
            return len(self._queue)


class ModelManager:
    """
    Central model management system.
    Handles loading, unloading, and lifecycle management of MLX models.
    """

    def __init__(self, max_concurrent_models: int = 3, max_memory_usage: float = 0.8):
        self.max_memory_usage = max_memory_usage  # Max % of system memory to use

        # Read max_concurrent_models from database settings
        self.max_concurrent_models = self._get_max_concurrent_models(max_concurrent_models)

        # Model storage
        self._loaded_models: Dict[str, LoadedModel] = {}
        self._loading_status: Dict[str, LoadingStatus] = {}
        self._lock = threading.RLock()

        # Queue system
        self._loading_queue = ModelLoadingQueue()
        self._queue_worker_thread = None
        self._cleanup_worker_thread = None
        self._queue_worker_running = False
        self._shutdown_requested = False

        # Register cleanup on exit
        import atexit
        atexit.register(self._force_cleanup)

        # Auto-unload settings - read from database with 5 minute default
        self._auto_unload_enabled = True
        self._inactivity_timeout = self._get_inactivity_timeout()
        self._cleanup_interval = 60  # seconds

        # Don't start background workers immediately - start them lazily

    def _get_max_concurrent_models(self, default_value: int) -> int:
        """Get the max concurrent models from database settings."""
        try:
            db_manager = get_database_manager()
            return db_manager.get_setting("max_concurrent_models", default_value)
        except Exception as e:
            logger.warning(f"Failed to read max concurrent models from database: {e}")
            return default_value

    def _get_inactivity_timeout(self) -> timedelta:
        """Get the inactivity timeout from database settings, defaulting to 5 minutes."""
        try:
            db_manager = get_database_manager()
            timeout_minutes = db_manager.get_setting("model_inactivity_timeout_minutes", 5)
            return timedelta(minutes=timeout_minutes)
        except Exception as e:
            logger.warning(f"Failed to read inactivity timeout from database: {e}")
            return timedelta(minutes=5)  # Default to 5 minutes

    def _start_queue_worker(self):
        """Start the queue processing worker."""
        if not self._queue_worker_running:
            self._queue_worker_running = True
            # Create daemon thread that won't prevent shutdown
            self._queue_worker_thread = threading.Thread(
                target=self._queue_worker,
                name="model_loader_queue",
                daemon=True
            )
            self._queue_worker_thread.start()

    def _start_cleanup_worker(self):
        """Start the cleanup worker for auto-unloading."""
        if self._cleanup_worker_thread is None or not self._cleanup_worker_thread.is_alive():
            # Create daemon thread that won't prevent shutdown
            self._cleanup_worker_thread = threading.Thread(
                target=self._cleanup_worker,
                name="model_cleanup",
                daemon=True
            )
            self._cleanup_worker_thread.start()

    def _queue_worker(self):
        """Background worker that processes the loading queue."""
        logger.info("Model loading queue worker started")

        while self._queue_worker_running:
            try:
                request = self._loading_queue.get_next_request(timeout=5.0)
                if request:
                    logger.info(f"Processing load request for {request.model_name}")
                    try:
                        self._load_model_sync(request)
                    except Exception as e:
                        logger.error(f"Error loading model {request.model_name}: {e}")
                        self._set_loading_status(request.model_name, LoadingStatus.FAILED)
            except Exception as e:
                logger.error(f"Queue worker error: {e}")
                time.sleep(1)

    def _cleanup_worker(self):
        """Background worker for auto-unloading inactive models."""
        logger.info("Model cleanup worker started")

        while not self._shutdown_requested:
            try:
                if self._auto_unload_enabled:
                    self._cleanup_inactive_models()

                # Sleep in smaller intervals to be more responsive to shutdown
                for _ in range(self._cleanup_interval):
                    if self._shutdown_requested:
                        break
                    time.sleep(1)
            except Exception as e:
                logger.error(f"Cleanup worker error: {e}")
                time.sleep(1)

        logger.info("Model cleanup worker stopped")

    def shutdown(self):
        """Shutdown the model manager and all background workers."""
        self._force_cleanup()

    def _force_cleanup(self):
        """Force cleanup - called on exit."""
        self._shutdown_requested = True
        self._queue_worker_running = False

        # Daemon threads will automatically be killed when main process exits
        # No need to explicitly wait for or kill them
        logger.info("Model manager cleanup completed")

    def _cleanup_inactive_models(self):
        """Unload models that have been inactive for too long."""
        cutoff_time = datetime.utcnow() - self._inactivity_timeout
        models_to_unload = []

        with self._lock:
            for model_name, loaded_model in self._loaded_models.items():
                if loaded_model.last_used_at < cutoff_time:
                    models_to_unload.append(model_name)

        for model_name in models_to_unload:
            logger.info(f"Auto-unloading inactive model: {model_name}")
            self.unload_model(model_name)

    def _set_loading_status(self, model_name: str, status: LoadingStatus):
        """Update model loading status."""
        with self._lock:
            self._loading_status[model_name] = status

        # Update database
        try:
            db_manager = get_database_manager()
            with db_manager.get_session() as session:
                model = session.query(Model).filter(Model.name == model_name).first()
                if model:
                    if status == LoadingStatus.LOADING:
                        model.status = ModelStatus.LOADING.value
                    elif status == LoadingStatus.LOADED:
                        model.status = ModelStatus.LOADED.value
                        model.last_used_at = datetime.utcnow()
                    elif status == LoadingStatus.FAILED:
                        model.status = ModelStatus.FAILED.value
                    else:
                        model.status = ModelStatus.UNLOADED.value
                    session.commit()
        except Exception as e:
            logger.error(f"Error updating model status in database: {e}")

    def _calculate_actual_memory_usage(self, model_path: str) -> float:
        """Calculate the actual memory usage based on file sizes + overhead."""
        total_size_bytes = 0

        try:
            # Handle both local paths and HuggingFace model IDs
            actual_path = self._resolve_model_path(model_path)

            # Walk through all files in the model directory
            for root, dirs, files in os.walk(actual_path):
                for file in files:
                    # Count all model-related files
                    if file.endswith(('.safetensors', '.bin', '.pth', '.pt', '.gguf', '.npz')):
                        file_path = os.path.join(root, file)
                        if os.path.exists(file_path):
                            total_size_bytes += os.path.getsize(file_path)

            # Convert to GB
            file_size_gb = total_size_bytes / (1024**3)

            # Add MLX overhead (25% for inference, activations, etc.)
            # Audio models might need less overhead, text models might need more
            if "whisper" in model_path.lower() or "parakeet" in model_path.lower():
                overhead_multiplier = 1.15  # 15% overhead for audio models
            else:
                overhead_multiplier = 1.25  # 25% overhead for text models

            actual_memory_gb = file_size_gb * overhead_multiplier

            # Round to one decimal place
            actual_memory_gb = round(actual_memory_gb, 1)

            logger.info(f"Model {model_path} -> {actual_path} file size: {file_size_gb:.1f}GB, "
                       f"with overhead: {actual_memory_gb:.1f}GB "
                       f"(multiplier: {overhead_multiplier})")

            return max(actual_memory_gb, 0.1)  # Minimum 0.1GB

        except Exception as e:
            logger.warning(f"Could not calculate actual memory usage for {model_path}: {e}")
            # Fallback to a reasonable default
            return 2.0

    def _resolve_model_path(self, model_path: str) -> str:
        """Resolve model path to actual filesystem location."""
        # If it's already a local path that exists, use it
        if os.path.exists(model_path):
            return model_path

        # If it looks like a HuggingFace model ID, find it in cache
        if "/" in model_path and not os.path.exists(model_path):
            # Convert HF model ID to cache path
            cache_dir = os.path.join(os.path.expanduser("~"), ".cache", "mlx-gui")

            # Convert model ID to cache directory name
            # "lmstudio-community/DeepSeek-R1-0528-Qwen3-8B-MLX-4bit" -> "models--lmstudio-community--DeepSeek-R1-0528-Qwen3-8B-MLX-4bit"
            cache_name = "models--" + model_path.replace("/", "--")
            cache_path = os.path.join(cache_dir, cache_name)

            if os.path.exists(cache_path):
                # Find the actual model files in snapshots subdirectory
                snapshots_dir = os.path.join(cache_path, "snapshots")
                if os.path.exists(snapshots_dir):
                    # Get the first (and usually only) snapshot directory
                    snapshot_dirs = [d for d in os.listdir(snapshots_dir) if os.path.isdir(os.path.join(snapshots_dir, d))]
                    if snapshot_dirs:
                        actual_path = os.path.join(snapshots_dir, snapshot_dirs[0])
                        logger.debug(f"Resolved HF model {model_path} to {actual_path}")
                        return actual_path

        # Fallback: return original path
        return model_path

    def _check_memory_constraints(self, required_memory_gb: float) -> Tuple[bool, str]:
        """Check if we can load a model with the required memory. Returns (can_load, warning_message)."""
        # First check concurrent model count limit - this is still a hard limit
        if len(self._loaded_models) >= self.max_concurrent_models:
            return False, f"Maximum concurrent models ({self.max_concurrent_models}) already loaded"

        system_monitor = get_system_monitor()
        memory_info = system_monitor.get_memory_info()

        # Calculate current usage by loaded models
        current_model_memory = sum(m.memory_usage_gb for m in self._loaded_models.values())

        # Check if we have enough total memory (80% of system RAM)
        max_allowed_memory = memory_info.total_gb * 0.8
        if current_model_memory + required_memory_gb > max_allowed_memory:
            warning_msg = f"⚠️ Memory warning: Loading this model ({required_memory_gb:.1f}GB) with current models ({current_model_memory:.1f}GB) may exceed recommended memory ({max_allowed_memory:.1f}GB of {memory_info.total_gb:.1f}GB total)"
            return True, warning_msg  # Allow but warn

        return True, ""

    def _load_model_sync(self, request: LoadRequest):
        """Synchronously load a model (runs in background thread)."""
        model_name = request.model_name
        model_path = request.model_path

        try:
            self._set_loading_status(model_name, LoadingStatus.LOADING)

            # Check if already loaded
            with self._lock:
                if model_name in self._loaded_models:
                    logger.info(f"Model {model_name} already loaded")
                    self._loaded_models[model_name].update_last_used()
                    return

            # Get model info from database
            db_manager = get_database_manager()
            with db_manager.get_session() as session:
                model_record = session.query(Model).filter(Model.name == model_name).first()
                if not model_record:
                    raise ValueError(f"Model {model_name} not found in database")

                # First, free up space if needed (this handles concurrent model limits)
                self._ensure_capacity_for_model(model_record.memory_required_gb)

                # Check memory constraints after freeing space
                can_load, memory_warning = self._check_memory_constraints(model_record.memory_required_gb)
                if not can_load:
                    # If we still can't load after freeing space, this is a hard limit
                    raise RuntimeError(memory_warning)
                elif memory_warning:
                    # Log warning but proceed
                    logger.warning(f"Loading model {model_name} with memory warning: {memory_warning}")

                # Also check system compatibility for hardware requirements
                system_monitor = get_system_monitor()
                hardware_compatible, hardware_message = system_monitor.check_model_compatibility(model_record.memory_required_gb)
                if not hardware_compatible:
                    # Hardware compatibility is still a hard requirement
                    raise RuntimeError(hardware_message)
                elif "warning" in hardware_message.lower():
                    # Log system memory warning
                    logger.warning(f"Loading model {model_name} with system warning: {hardware_message}")

            # Load the model using MLX-LM with retry logic for memory errors
            logger.info(f"Loading MLX model from {model_path}")

            inference_engine = get_inference_engine()
            mlx_wrapper = self._load_model_with_retry(inference_engine, model_name, model_path, model_record.memory_required_gb)

            # Calculate actual file size + overhead for this model
            actual_memory = self._calculate_actual_memory_usage(model_path)

            # Update database with actual memory usage
            db_manager = get_database_manager()
            with db_manager.get_session() as session:
                model_record = session.query(Model).filter(Model.name == model_name).first()
                if model_record:
                    model_record.memory_required_gb = actual_memory
                    session.commit()
                    logger.info(f"Updated {model_name} memory requirement in DB: {actual_memory:.1f}GB")

            loaded_model = LoadedModel(
                model_id=model_name,
                mlx_wrapper=mlx_wrapper,
                loaded_at=datetime.utcnow(),
                last_used_at=datetime.utcnow(),
                memory_usage_gb=actual_memory
            )

            with self._lock:
                self._loaded_models[model_name] = loaded_model

            self._set_loading_status(model_name, LoadingStatus.LOADED)
            logger.info(f"Successfully loaded model {model_name}")

            # Call callback if provided
            if request.callback:
                request.callback(model_name, True, None)

        except Exception as e:
            error_msg = f"Failed to load model {model_name}: {e}"
            logger.error(error_msg)
            self._set_loading_status(model_name, LoadingStatus.FAILED)

            # Update database with error
            try:
                db_manager = get_database_manager()
                with db_manager.get_session() as session:
                    model_record = session.query(Model).filter(Model.name == model_name).first()
                    if model_record:
                        model_record.error_message = str(e)
                        session.commit()
            except Exception as db_error:
                logger.error(f"Error updating database with error message: {db_error}")

            # Call callback with error
            if request.callback:
                request.callback(model_name, False, str(e))

    def _ensure_capacity_for_model(self, required_memory_gb: float):
        """Free up capacity for a new model if needed."""
        # Check if we need to unload models due to hard limits (not memory warnings)
        can_load, message = self._check_memory_constraints(required_memory_gb)
        while not can_load and "Maximum concurrent models" in message:
            # Find least recently used model to unload
            if not self._loaded_models:
                break

            lru_model_name = min(
                self._loaded_models.keys(),
                key=lambda x: self._loaded_models[x].last_used_at
            )

            logger.info(f"Unloading LRU model {lru_model_name} to make space for new model")
            self.unload_model(lru_model_name)

            # Check again
            can_load, message = self._check_memory_constraints(required_memory_gb)

            if len(self._loaded_models) == 0:
                break

    def _free_memory_for_model(self, required_memory_gb: float) -> bool:
        """Free up memory by unloading the oldest model. Returns True if a model was unloaded."""
        if not self._loaded_models:
            return False

        # Find least recently used model to unload
        lru_model_name = min(
            self._loaded_models.keys(),
            key=lambda x: self._loaded_models[x].last_used_at
        )

        logger.info(f"🔄 Freeing memory: Unloading LRU model '{lru_model_name}' to make space for new model ({required_memory_gb:.1f}GB required)")
        success = self.unload_model(lru_model_name)

        if success:
            # Force garbage collection and clear MLX cache
            import gc
            gc.collect()
            mx.metal.clear_cache()
            logger.info(f"✅ Memory freed by unloading '{lru_model_name}'")

        return success

    def _is_memory_error(self, error: Exception) -> bool:
        """Check if an exception is a memory-related error."""
        error_str = str(error).lower()
        error_type = type(error).__name__

        # Check for common memory error patterns
        memory_indicators = [
            "out of memory",
            "memory allocation",
            "insufficient memory",
            "memory error",
            "cuda out of memory",
            "device out of memory",
            "metal out of memory",
            "failed to allocate",
            "allocation failed",
            "not enough memory",
            "memory limit exceeded"
        ]

        # Check error message
        if any(indicator in error_str for indicator in memory_indicators):
            return True

        # Check error type
        if error_type in ["OutOfMemoryError", "MemoryError"]:
            return True

        # Check for RuntimeError with memory keywords
        if error_type == "RuntimeError" and any(indicator in error_str for indicator in memory_indicators):
            return True

        return False

    def _load_model_with_retry(self, inference_engine, model_name: str, model_path: str, required_memory_gb: float):
        """Load a model with automatic retry and memory management."""
        max_retries = 3
        attempt = 0

        while attempt < max_retries:
            try:
                # Attempt to load the model
                mlx_wrapper = inference_engine.load_model(model_name, model_path)

                if attempt > 0:
                    logger.info(f"✅ Successfully loaded model '{model_name}' on attempt {attempt + 1}")

                return mlx_wrapper

            except Exception as e:
                attempt += 1

                # Check if this is a memory-related error
                if self._is_memory_error(e):
                    logger.warning(f"⚠️ Memory error loading '{model_name}' (attempt {attempt}/{max_retries}): {e}")

                    # If we have more retries left, try to free memory
                    if attempt < max_retries:
                        freed = self._free_memory_for_model(required_memory_gb)

                        if freed:
                            logger.info(f"🔄 Retrying model load after freeing memory (attempt {attempt + 1}/{max_retries})")
                            continue
                        else:
                            logger.error(f"❌ No models available to unload, cannot retry loading '{model_name}'")
                            break
                    else:
                        logger.error(f"❌ Failed to load '{model_name}' after {max_retries} attempts due to memory constraints")
                        raise RuntimeError(f"Failed to load model '{model_name}' after {max_retries} attempts due to insufficient memory. Consider unloading other models manually.")
                else:
                    # Non-memory error, don't retry
                    logger.error(f"❌ Non-memory error loading '{model_name}': {e}")
                    raise

        # If we get here, we've exhausted retries
        raise RuntimeError(f"Failed to load model '{model_name}' after {max_retries} attempts")

    async def load_model_async(self, model_name: str, model_path: str, priority: int = 0) -> bool:
        """Asynchronously request model loading."""
        # Check if model is already loaded or loading
        with self._lock:
            if model_name in self._loaded_models:
                self._loaded_models[model_name].update_last_used()
                return True

            if self._loading_status.get(model_name) == LoadingStatus.LOADING:
                # Wait for existing load to complete
                while self._loading_status.get(model_name) == LoadingStatus.LOADING:
                    await asyncio.sleep(0.1)
                return model_name in self._loaded_models

        # Start background workers if not already running
        if not self._queue_worker_running:
            self._start_queue_worker()
            self._start_cleanup_worker()

        # Add to queue
        request = LoadRequest(
            model_name=model_name,
            model_path=model_path,
            priority=priority
        )

        position = self._loading_queue.add_request(request)
        logger.info(f"Added {model_name} to loading queue at position {position}")

        # Wait for loading to complete
        while True:
            await asyncio.sleep(0.5)
            status = self._loading_status.get(model_name, LoadingStatus.IDLE)

            if status == LoadingStatus.LOADED:
                return True
            elif status == LoadingStatus.FAILED:
                return False
            elif status == LoadingStatus.IDLE:
                # Check if still in queue
                if not any(req.model_name == model_name for req in self._loading_queue._queue):
                    return False

    def unload_model(self, model_name: str) -> bool:
        """Unload a model from memory."""
        try:
            with self._lock:
                if model_name not in self._loaded_models:
                    logger.warning(f"Model {model_name} not loaded")
                    return False

                self._set_loading_status(model_name, LoadingStatus.UNLOADING)

                # Unload from MLX inference engine
                inference_engine = get_inference_engine()
                inference_engine.unload_model(model_name)

                loaded_model = self._loaded_models.pop(model_name)

                # Clear from status
                self._loading_status.pop(model_name, None)

                logger.info(f"Unloaded model {model_name}")

                # Update database
                self._set_loading_status(model_name, LoadingStatus.IDLE)

                return True

        except Exception as e:
            logger.error(f"Error unloading model {model_name}: {e}")
            return False

    def get_loaded_models(self) -> Dict[str, Dict[str, Any]]:
        """Get information about currently loaded models."""
        with self._lock:
            return {
                name: {
                    "loaded_at": model.loaded_at.isoformat(),
                    "last_used_at": model.last_used_at.isoformat(),
                    "memory_usage_gb": model.memory_usage_gb,
                    "config": model.config
                }
                for name, model in self._loaded_models.items()
            }

    def get_model_status(self, model_name: str) -> Dict[str, Any]:
        """Get detailed status of a specific model."""
        with self._lock:
            status = self._loading_status.get(model_name, LoadingStatus.IDLE)
            loaded_model = self._loaded_models.get(model_name)

            result = {
                "name": model_name,
                "status": status.value,
                "loaded": loaded_model is not None,
                "loaded_at": loaded_model.loaded_at.isoformat() if loaded_model else None,
                "last_used_at": loaded_model.last_used_at.isoformat() if loaded_model else None,
                "memory_usage_gb": loaded_model.memory_usage_gb if loaded_model else 0,
                "queue_position": next(
                    (i for i, req in enumerate(self._loading_queue._queue) if req.model_name == model_name),
                    None
                )
            }

            # Add real download progress if model is being downloaded
            if status == LoadingStatus.LOADING:
                # Get model path from database to find the HuggingFace model ID
                db = next(get_db_session())
                try:
                    model_record = db.query(Model).filter(Model.name == model_name).first()
                    if model_record:
                        # Get download progress from MLX loader
                        inference_engine = get_inference_engine()
                        download_progress = inference_engine.get_download_progress(model_record.path)
                        result.update({
                            "download_progress": download_progress.get("progress", 0),
                            "download_stage": download_progress.get("stage", "Loading..."),
                            "download_status": download_progress.get("status", "unknown"),
                            "downloaded_mb": download_progress.get("downloaded_mb", 0),
                            "total_mb": download_progress.get("total_mb", 0),
                            "download_speed_mbps": download_progress.get("speed_mbps", 0),
                            "download_eta_seconds": download_progress.get("eta_seconds", 0)
                        })
                finally:
                    db.close()

            return result

    def refresh_settings(self):
        """Refresh settings from database (called when settings change)."""
        self.max_concurrent_models = self._get_max_concurrent_models(3)
        self._inactivity_timeout = self._get_inactivity_timeout()

    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status."""
        system_monitor = get_system_monitor()
        memory_info = system_monitor.get_memory_info()

        # Refresh settings from database
        self.refresh_settings()

        with self._lock:
            total_model_memory = sum(m.memory_usage_gb for m in self._loaded_models.values())

            return {
                "loaded_models_count": len(self._loaded_models),
                "max_concurrent_models": self.max_concurrent_models,
                "queue_size": self._loading_queue.size(),
                "total_model_memory_gb": total_model_memory,
                "system_memory_total_gb": memory_info.total_gb,
                "system_memory_available_gb": memory_info.available_gb,
                "memory_usage_percent": (total_model_memory / memory_info.total_gb) * 100,
                "auto_unload_enabled": self._auto_unload_enabled,
                "inactivity_timeout_minutes": self._inactivity_timeout.total_seconds() / 60
            }

    async def generate_text(self, model_name: str, prompt: str, config: GenerationConfig) -> GenerationResult:
        """Generate text using a loaded model."""
        # Ensure model is loaded
        with self._lock:
            if model_name not in self._loaded_models:
                raise ValueError(f"Model {model_name} is not loaded")

            # Update last used time
            self._loaded_models[model_name].update_last_used()

        # Perform inference
        inference_engine = get_inference_engine()
        result = inference_engine.generate(model_name, prompt, config)

        # Update model usage in database
        try:
            db_manager = get_database_manager()
            with db_manager.get_session() as session:
                model_record = session.query(Model).filter(Model.name == model_name).first()
                if model_record:
                    model_record.increment_use_count()
                    session.commit()
        except Exception as e:
            logger.error(f"Error updating model usage: {e}")

        return result

    async def generate_text_stream(self, model_name: str, prompt: str, config: GenerationConfig) -> AsyncGenerator[str, None]:
        """Generate text with streaming."""
        # Ensure model is loaded
        with self._lock:
            if model_name not in self._loaded_models:
                raise ValueError(f"Model {model_name} is not loaded")

            # Update last used time
            self._loaded_models[model_name].update_last_used()

        # Perform streaming inference
        inference_engine = get_inference_engine()
        async for token in inference_engine.generate_stream(model_name, prompt, config):
            yield token

        # Update model usage in database after streaming completes
        try:
            db_manager = get_database_manager()
            with db_manager.get_session() as session:
                model_record = session.query(Model).filter(Model.name == model_name).first()
                if model_record:
                    model_record.increment_use_count()
                    session.commit()
        except Exception as e:
            logger.error(f"Error updating model usage for streaming: {e}")

    def get_model_for_inference(self, model_name: str) -> Optional[LoadedModel]:
        """Get a loaded model for inference (returns None if not loaded)."""
        with self._lock:
            loaded_model = self._loaded_models.get(model_name)
            if loaded_model:
                loaded_model.update_last_used()
            return loaded_model

    def shutdown(self):
        """Gracefully shutdown the model manager."""
        logger.info("Shutting down model manager...")

        self._shutdown_requested = True
        self._queue_worker_running = False

        # Unload all models
        with self._lock:
            model_names = list(self._loaded_models.keys())

        for model_name in model_names:
            self.unload_model(model_name)

        # Daemon threads will be automatically cleaned up
        logger.info("Model manager shutdown complete")


# Global model manager instance
_model_manager: Optional[ModelManager] = None


def get_model_manager() -> ModelManager:
    """Get the global model manager instance."""
    global _model_manager
    if _model_manager is None:
        _model_manager = ModelManager()
    return _model_manager


def shutdown_model_manager():
    """Shutdown the global model manager."""
    global _model_manager
    if _model_manager:
        _model_manager.shutdown()
        _model_manager = None
