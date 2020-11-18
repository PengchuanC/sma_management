"""
shu
~~~~~~~~~~~~~~~~~~~~~~~
@author: chuanchao.peng
@date: 2020-09-08
@desc:
"""

from pathlib import Path
from shu.sma_export.parse_configs import configs
from shu.sma_export.dataset import TABLES


target = configs['target_path']
current = Path(__file__).resolve().parent


def mk_dirs(path=target):
    path = current / path
    if not path.is_dir():
        path.mkdir()
    for name in TABLES:
        node = path / name
        if not node.is_dir():
            node.mkdir()


def show_all_files(director):
    director = current / target / director
    files = director.glob('*')
    return files


def concat_path(*args):
    path = (current / target).joinpath(*args)
    return path
