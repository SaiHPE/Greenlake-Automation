from __future__ import annotations

from pathlib import Path


class ArtifactStore:
    def __init__(self, artifact_dir: Path) -> None:
        self.artifact_dir = artifact_dir

    def run_dir(self, run_id: str) -> Path:
        path = self.artifact_dir / run_id
        path.mkdir(parents=True, exist_ok=True)
        return path

    def browser_dir(self, run_id: str) -> Path:
        path = self.run_dir(run_id) / "browser"
        path.mkdir(parents=True, exist_ok=True)
        return path
