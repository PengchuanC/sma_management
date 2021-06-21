from collections import namedtuple
from typing import List
from pathlib import Path
from dateutil.parser import parse


VF = namedtuple('ValuationFile', 'name date absolute')


def analyze_path(path: Path) -> VF:
    """分析估值表路径信息"""
    absolute = path.absolute()
    stem = path.stem
    name, date = stem.split('_')
    date = parse(date).date()
    return VF(name=name, date=date, absolute=absolute)


def collect_files(path: str, file_type: str, keywords=None) -> List[VF]:
    files = Path(path).glob(f'*.{file_type}')
    files = sorted(files)
    if keywords:
        files = [analyze_path(x) for x in files if keywords in x.name]
    else:
        files = [analyze_path(x) for x in files]
    return files
