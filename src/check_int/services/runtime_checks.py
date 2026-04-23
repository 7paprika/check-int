from pathlib import Path

from check_int.config import AppConfig


def ensure_runtime_ready(config: AppConfig, *, required_model_files: list[str]) -> dict[str, str]:
    missing = [name for name in required_model_files if not (config.models_dir / name).exists()]
    if missing:
        raise FileNotFoundError(f"Missing model files: {', '.join(missing)}")

    return {
        "status": "ready",
        "models_dir": str(Path(config.models_dir)),
    }