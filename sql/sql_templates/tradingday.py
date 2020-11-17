

tradingday = """
    select tradingdate as "date" from jydb.qt_tradingdaynew where secumarket = 83 and iftradingday=1
    and tradingdate > to_date('<date/>', 'yyyy-MM-dd')
"""