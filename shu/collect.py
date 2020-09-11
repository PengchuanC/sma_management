"""
collect
~~~~~~~~~~~~~~~~~~~~~~~
@author: chuanchao.peng
@date: 2020-09-08
@desc:
"""
import os

from typing import Union, Dict, Generator, List
from dateutil.parser import parse
from pandas import read_excel

from shu.configs import target


def table_store_director(name) -> str:
    """excel文件存放位置"""
    path = os.path.join(target, name)
    return path


def whole_files(dir_abs_path) -> Union[List[str], List[bytes]]:
    """文件夹下全部文件"""
    files = os.listdir(dir_abs_path)
    files = [os.path.join(dir_abs_path, x) for x in files]
    return files


def parse_date(file_abs_path):
    file = os.path.split(file_abs_path)[-1]
    date = file.split('-')[-1].rstrip('.xlsx')
    date = parse(date).date()
    return date


def read_table(path):
    yield read_excel(path).to_dict(orient='records')


def dataset(name) -> Dict[str, Generator]:
    """数据集"""
    abs_path = table_store_director(name)
    files = whole_files(abs_path)
    data = {parse_date(file): read_table(file) for file in files}
    return data


def dataset_without_date(name) -> "DataFrame":
    abs_path = table_store_director(name)
    file = whole_files(abs_path)[0]
    data = read_excel(file)
    data = data.to_dict(orient='records')
    return data


def export(name):
    """输出读取的数据"""
    if name == '组合信息表':
        return dataset_without_date(name)
    return dataset(name)
