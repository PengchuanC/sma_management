"""
configs
~~~~~~~~~~~~~~~~~~~~~~~
@author: chuanchao.peng
@date: 2020-09-08
@desc:
"""
from shu import models
from pathlib import Pathd


TEST = False

# 文件存放地址
target = str(Path(__file__).parent / 'sma_export' / 'data')

# 待导入表单的信息
tables = {
    '组合信息表': 'sma_portfolio', '组合资产负债表': 'sma_balance',
    '组合应收应付表': 'sma_balance_expanded', '组合损益表': 'sma_income_portfolio',
    '资产损益表': 'sma_income_asset', '组合持仓表': 'sma_holding_fund',
    '组合流水表': 'sma_transactions', '组合费用表': 'sma_detail_fee',
    '基准净值表': 'sma_evaluate_benchmark', '基金风格表': 'sma_fund_style',
    '基金应付利息税': 'sma_interest_tax'
}

mapping = {
    'sma_portfolio': models.Portfolio, 'sma_balance': models.Balance,
    'sma_balance_expanded': models.BalanceExpanded, 'sma_income_portfolio': models.Income,
    'sma_income_asset': models.IncomeAsset, 'sma_holding_fund': models.Holding,
    'sma_transactions': models.Transactions, 'sma_detail_fee': models.DetailFee,
    'sma_evaluate_benchmark': models.ValuationBenchmark, 'sma_fund_style': models.FundStyle,
    'sma_interest_tax': models.InterestTax
}


if TEST:
    home = Path('p:/code/sma/data')
else:
    home = Path('/home/data')

local_files_path = home / 'management'
