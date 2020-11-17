"""
从聚源数据库读取基金行情数据
"""


# 基金代码及简称
fund = "select secucode, secuabbr as secuname from jydb.secumain where secucategory=8"

# 基金累计净值数据
acc_nav = """
    SELECT
        s.secucode AS secucode,
        m.enddate AS "date",
        m.nv,
        m.unitnv AS nav,
        m.accumulatedunitnv AS acc_nav,
        m.dailyprofit
    FROM
        jydb.secumain s
    JOIN jydb.mf_netvalue m ON
        s.innercode = m.innercode
    WHERE
        s.secucode = '<code>'
        AND enddate > to_date('<date>', 'yyyy-MM-dd')
"""


# 基金累计净值数据
adj_nav = """
    SELECT
        s.secucode AS secucode,
        m.tradingday AS "date",
        m.unitnv AS nav,
        m.UnitNVRestored AS adj_nav
    FROM
        jydb.secumain s
    JOIN jydb.MF_FundNetValueRe m ON
        s.innercode = m.innercode
    WHERE
        s.secucode = '<code>'
        AND m.tradingday > to_date('<date>', 'yyyy-MM-dd')
"""


# 基金前十大重仓股
fund_top_ten_stock = """
    SELECT
        s.secucode,
        k.reportdate AS "date",
        s2.secucode AS stockcode,
        s2.secuabbr AS stockname,
        k.serialnumber AS "serial",
        k.ratioinnv AS ratio
    FROM
        jydb.secumain s
    JOIN jydb.MF_KeyStockPortfolio k ON
        s.innercode = k.innercode
    JOIN jydb.secumain s2 ON
        k.stockinnercode = s2.innercode
    WHERE
        s.secucode = '<code>'
        AND k.reportdate > to_date('<date>', 'yyyy-MM-dd')
    ORDER BY
        k.reportdate,
        k.serialnumber
"""