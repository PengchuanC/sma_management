"""
parse_configs
~~~~~~~~~~~~~~~~~~~~~~~
@author: chuanchao.peng
@date: 2020-09-08
@desc:
"""

import yaml

from pathlib import Path


yaml.warnings({'YAMLLoadWarning': False})


def load_configs(file='configs.yaml'):
    base = Path(__file__).resolve(strict=True).parent.joinpath(file)
    with open(base, 'r', encoding='utf-8') as f:
        data = yaml.load(f)
    return data


configs = load_configs()
