

stock = """
    select secucode, secuabbr as secuname from jydb.secumain where secucategory=1 and listedstate = 1 
    order by secucode
"""


# 股票申万行业分类
stock_sw = """
    SELECT
        SecuCode,
        FirstIndustryName,
        SecondIndustryName
    FROM
        jydb.secumain s
    JOIN jydb.LC_ExgIndustry m ON
        s.CompanyCode = m.CompanyCode
    WHERE
        m.Standard = 24
        AND s.SecuCategory = 1
"""


# 股票因子暴露度
stock_expose = """
    SELECT
        TRADE_DATE AS "date",
        TICKER_SYMBOL AS secucode,
        BETA,
        MOMENTUM,
        "SIZE" as "size",
        EARNYILD,
        RESVOL,
        GROWTH,
        BTOP,
        LEVERAGE,
        LIQUIDTY,
        SIZENL
    FROM
        DATAYES."dy1d_exposure" dde
    WHERE
        TRADE_DATE >= '<date>'
"""