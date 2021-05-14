import pandas as pd

from proc.read.collect import VF
from proc.read.parse_valuation import analyze


def read_valuation(path: VF) -> dict:
    data = pd.read_excel(path.absolute, skiprows=3)
    data = analyze(data)
    return data

