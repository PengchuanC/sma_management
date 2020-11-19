"""
configs
~~~~~~~~~~~~~~~~~~~~~~~
@author: chuanchao.peng
@date: 2020-09-08
@desc:
"""
from shu import models
from pathlib import Path


# 文件存放地址
target = str(Path(__file__).parent / 'sma_export' / 'data')

# 待导入表单的信息
tables = {
    '组合信息表': 'sma_portfolio', '组合资产负债表': 'sma_balance',
    '组合应收应付表': 'sma_balance_expanded', '组合损益表': 'sma_income_portfolio',
    '资产损益表': 'sma_income_asset', '组合持仓表': 'sma_holding_fund',
    '组合流水表': 'sma_transactions', '组合费用表': 'sma_detail_fee',
    '基准净值表': 'sma_evaluate_benchmark'
}

mapping = {
    'sma_portfolio': models.Portfolio, 'sma_balance': models.Balance,
    'sma_balance_expanded': models.BalanceExpanded, 'sma_income_portfolio': models.Income,
    'sma_income_asset': models.IncomeAsset, 'sma_holding_fund': models.Holding,
    'sma_transactions': models.Transactions, 'sma_detail_fee': models.DetailFee,
    'sma_evaluate_benchmark': models.ValuationBenchmark
}
