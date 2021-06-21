import proc
import pandas as pd

from proc.read.collect import VF
from proc.read.parse_valuation import analyze, analyze_new


def read_valuation(path: VF) -> dict:
    data = pd.read_excel(path.absolute, skiprows=3)
    data = analyze(data)
    return data


def read_valuation_new(path: VF) -> dict:
    data = pd.read_html(str(path.absolute))[0]
    data = analyze_new(data)
    return data
