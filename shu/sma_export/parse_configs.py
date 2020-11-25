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
special_table = ['组合信息表', '基金风格表']
special_table_en = ['sma_portfolio', 'sma_fund_style']
