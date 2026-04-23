from pathlib import Path

import pytest

from check_int.config import AppConfig
from check_int.services.runtime_checks import ensure_runtime_ready


def test_app_config_resolves_default_artifact_directories(tmp_path) -> None:
    config = AppConfig.from_base_dir(tmp_path)

    assert config.base_dir == tmp_path
    assert config.artifacts_dir == tmp_path / "artifacts"
    assert config.models_dir == tmp_path / "models"


def test_ensure_runtime_ready_reports_missing_model_files(tmp_path) -> None:
    config = AppConfig.from_base_dir(tmp_path)
    config.models_dir.mkdir(parents=True, exist_ok=True)

    with pytest.raises(FileNotFoundError):
        ensure_runtime_ready(config, required_model_files=["detector.pt"])


def test_ensure_runtime_ready_passes_when_required_models_exist(tmp_path) -> None:
    config = AppConfig.from_base_dir(tmp_path)
    config.models_dir.mkdir(parents=True, exist_ok=True)
    (config.models_dir / "detector.pt").write_text("ok", encoding="utf-8")

    result = ensure_runtime_ready(config, required_model_files=["detector.pt"])

    assert result["status"] == "ready"
    assert Path(result["models_dir"]) == config.models_dir
