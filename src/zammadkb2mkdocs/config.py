from pathlib import Path
from dataclasses import dataclass


@dataclass
class Config:
    # Given via CLI
    db_path: Path
    zammad_fqdn: str

    # Default directories
    dist_dir: Path = Path("dist")
    docs_dir: Path = dist_dir / "docs"
    docs_kb_dir: Path = docs_dir / "kb"
    img_dir: Path = dist_dir / "images"
    json_path: Path = dist_dir / "kb.json"
    json_imgfixed_path: Path = dist_dir / "kb_imgfixed.json"

    # Default log level
    loglevel: str = "INFO"

    def __post_init__(self):
        """Create dist directory and subdirectories if they don't exist"""
        self.dist_dir.mkdir(parents=True, exist_ok=True)