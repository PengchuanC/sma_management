import pandas as pd

from datetime import date
from pathlib import Path

from ...models import AssetWeight as AW
from django.forms.models import model_to_dict


# 最高仓位限制
MAX_LIMIT = .5


class Config(object):
    """MVO参数"""
    window = 3
    start = date(2007, 1, 1)
    end = date(2020, 9, 30)
    # 优化目标(波动率限制, 权益仓位限制)
    risks = [(0.02, 0), (0.05, 0.25), (0.10, 0.50), (0.15, 0.70), (0.18, 0.80)]
    # 现金型约束
    bounds = [(0, .1e10), (0, .5), (0, .5), (0, 1.0), (0, .1e10), (0, 0.1), (0, .1e10), (0, .1e10)]
    # 固收型以上权益资产bound上限约束
    max_limit = 0.5
    # 固收型以上的约束
    output_dir = 'output'

    @classmethod
    def output(cls, filename=None):
        """设置配置比例输出路径"""
        if not filename:
            filename = f'weight_rolling_{cls.window}years'
        output_dir = Path(__file__).parent / cls.output_dir
        if not output_dir.exists():
            output_dir.mkdir()
        path = output_dir / filename
        file = path.with_suffix('.xlsx')
        return file

    @classmethod
    @property
    def bounds2(cls):
        return [
            (0, cls.max_limit), (0, .3), (0, .3), (.05, .15), (0, cls.max_limit), (0, .1), (0, .3), (0, cls.max_limit)
        ]


class BTConfig(object):
    """回测参数"""
    start = date(2017, 1, 1)
    end = date(2020, 10, 31)
    init_money = 1
    # 是否对配置比例进行平滑
    smooth = True
    # 平滑窗口
    window = 3
    # 是否调仓
    change = True
    equity = ["166005", "163402", "519712", "000979", "110011", "100038"]
    bond = ["485111", "519669", "000286", "000191", "110007"]
    alter = ["000216"]
    cash = ["482002"]

    @classmethod
    def set_weight_data(cls):
        data = AW.objects.all()
        data = [model_to_dict(x) for x in data]
        data = pd.DataFrame(data)
        return data
