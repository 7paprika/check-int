from check_int.app.use_cases import IntegrityCheckUseCase, build_default_use_case
from check_int.config import AppConfig


def test_build_default_use_case_constructs_local_pipeline(tmp_path) -> None:
    config = AppConfig.from_base_dir(tmp_path)

    use_case = build_default_use_case(config)

    assert isinstance(use_case, IntegrityCheckUseCase)
