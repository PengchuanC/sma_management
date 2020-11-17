
from pathlib import Path


file_dir = Path(__file__).parent.parent.parent / 'download'

if not file_dir.exists():
    file_dir.mkdir()


__all__ = ('file_dir', )
