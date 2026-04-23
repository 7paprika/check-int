from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class AppConfig:
    base_dir: Path
    artifacts_dir: Path
    models_dir: Path

    @classmethod
    def from_base_dir(cls, base_dir: str | Path) -> "AppConfig":
        root = Path(base_dir)
        return cls(
            base_dir=root,
            artifacts_dir=root / "artifacts",
            models_dir=root / "models",
        )