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
        k.ratioinnv AS ratio,
        '季报' AS publish
    FROM
        jydb.secumain s
    JOIN jydb.MF_KeyStockPortfolio k ON
        s.innercode = k.innercode
    JOIN jydb.secumain s2 ON
        k.stockinnercode = s2.innercode
    WHERE
        k.InfoPublDate > TO_DATE('<date>', 'YYYY-MM-DD')
    UNION ALL
    SELECT
        s.secucode,
        k.reportdate AS "date",
        s2.secucode AS stockcode,
        s2.secuabbr AS stockname,
        k.serialnumber AS "serial",
        k.ratioinnv AS ratio,
        '季报' AS publish
    FROM
        jydb.secumain s
    JOIN jydb.MF_KeyStockPortfolio k ON
        s.innercode = k.innercode
    JOIN jydb.hk_secumain s2 ON
        k.stockinnercode = s2.innercode
    WHERE
        k.InfoPublDate > TO_DATE('<date>', 'YYYY-MM-DD')
"""

fund_top_ten_stock_date = """SELECT max(InfoPublDate) as "date" FROM JYDB.MF_KEYSTOCKPORTFOLIO"""


# 基金年报、中报完整持仓
fund_holding_stock_detail = """
 SELECT
    a.secucode,
    s2.SECUCODE AS stockcode,
    s2.SECUABBR AS stockname,
    a.serialnumber AS serial,
    a.ratioinnv AS ratio,
    '年报' AS publish,
    a.reportdate AS "date"
FROM
    (
    SELECT
        s.SECUCODE,
        ms.REPORTDATE,
        ms.SERIALNUMBER,
        ms.STOCKINNERCODE,
        ms.RATIOINNV
    FROM
        JYDB.MF_STOCKPORTFOLIODETAIL ms
    JOIN JYDB.SECUMAIN s ON
        ms.INNERCODE = s.INNERCODE) a
JOIN Jydb.SECUMAIN s2 ON
    a.stockinnercode = s2.INNERCODE
WHERE
    reportdate > TO_DATE('<date>', 'YYYY-MM-DD') 
UNION ALL
 SELECT
    a.secucode,
    s2.SECUCODE AS stockcode,
    s2.SECUABBR AS stockname,
    a.serialnumber AS serial,
    a.ratioinnv AS ratio,
    '年报' AS publish,
    a.reportdate AS "date"
FROM
    (
    SELECT
        s.SECUCODE,
        ms.REPORTDATE,
        ms.SERIALNUMBER,
        ms.STOCKINNERCODE,
        ms.RATIOINNV
    FROM
        JYDB.MF_STOCKPORTFOLIODETAIL ms
    JOIN JYDB.SECUMAIN s ON
        ms.INNERCODE = s.INNERCODE) a
JOIN Jydb.HK_SECUMAIN s2 ON
    a.stockinnercode = s2.INNERCODE
WHERE
    reportdate > TO_DATE('<date>', 'YYYY-MM-DD')
"""

fund_holding_stock_detail_date = """SELECT max(REPORTDATE) as "date" FROM JYDB.MF_STOCKPORTFOLIODETAIL"""

# 基金代码关联
fund_associate = """
    SELECT
        a.secucode,
        s2.secucode AS relate
    FROM
        (
        SELECT
            s.SECUCODE,
            mc.RELATEDINNERCODE
        FROM
            JYDB.MF_CodeRelationshipNew mc
        JOIN JYDB.SECUMAIN s ON
            mc.INNERCODE = s.INNERCODE
        WHERE
            CODEDEFINE = 24) a
    JOIN JYDB.SECUMAIN s2 ON
        a.RELATEDINNERCODE = s2.INNERCODE
"""


# 基金资产配置
fund_allocate = """
    SELECT
        SECUCODE,
        REPORTDATE    as "date",
        RINOFSTOCK    as stock,
        RINOFBOND     as bond,
        RINOFFUND     as fund,
        RINOFMETALS   as metals,
        RINOfMonetary as monetary
    FROM
        (
        SELECT
            SECUCODE,
            ma.REPORTDATE,
            ma.RINOFSTOCK,
            ma.RINOFBOND,
            ma.RINOFFUND,
            ma.RINOFMETALS,
            ma.RINOfMonetary,
            ROW_NUMBER() OVER(PARTITION BY secucode ORDER BY ma.REPORTDATE DESC) rn
        FROM
            JYDB.MF_AssetAllocationNew ma
        JOIN JYDB.SECUMAIN s ON
            ma.INNERCODE = s.INNERCODE ) a
    WHERE
        rn = 1
"""


# 基金公告
fund_announcement = """
    SELECT
        s.SECUCODE,
        s.SECUABBR,
        INFOPUBLDATE AS "date",
        INFOTITLE AS title,
        CONTENT
    FROM
        JYDB.MF_Announcement ma
    JOIN JYDB.SECUMAIN s ON
        ma.INNERCODE = s.INNERCODE
    WHERE
        ma.INFOPUBLDATE > TO_DATE('<date>', 'YYYY-MM-DD')
    UNION ALL
    SELECT
        s.SECUCODE,
        s.SECUABBR,
        ma.BULLETINDATE AS "date",
        INFOTITLE AS title,
        DETAIL AS content
    FROM
        JYDB.MF_InterimBulletin ma
    JOIN JYDB.MF_INTERIMBULLETIN_SE mis ON
        ma.id = mis.id
    JOIN JYDB.SECUMAIN s ON
        mis.CODE = s.INNERCODE
    WHERE
        ma.BULLETINDATE > TO_DATE('<date>', 'YYYY-MM-DD')
    ORDER BY
        "date"
"""


# 基金管理人
fund_advisor = """
    SELECT
        s.SECUCODE,
        mi.INVESTADVISORCODE AS advisorcode,
        mi.INVESTADVISORABBRNAME AS advisorname
    FROM
        JYDB.MF_FUNDARCHIVES mf
    JOIN JYDB.SECUMAIN s ON
        mf.INNERCODE = s.INNERCODE
    JOIN JYDB.MF_INVESTADVISOROUTLINE mi ON
        mf.INVESTADVISORCODE = mi.INVESTADVISORCODE
"""