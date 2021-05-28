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

acc_nav_multi = """
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
        s.secucode in ('<code>')
        AND enddate > to_date('<date>', 'yyyy-MM-dd')
"""


# 基金复权净值数据
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

adj_nav_multi = """
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
        s.secucode in ('<code>')
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


fund_holding_stock_hk = """
    SELECT
        s.secucode,
        mq.ENDDATE AS "date",
        mq.SECUTRADECODE AS stockcode,
        mq.SERIALNUMBER AS serial,
        '季报' AS publish,
        mq.RATIOINNV as ratio
    FROM
        JYDB.MF_QDIIPORTFOLIODETAIL mq
    JOIN JYDB.SECUMAIN s ON
        mq.INNERCODE = s.INNERCODE
    JOIN (
        SELECT
            *
        FROM
            (
            SELECT
                INNERCODE,
                ENDDATE,
                ROW_NUMBER() OVER(PARTITION BY INNERCODE ORDER BY mq.ENDDATE DESC) rn
            FROM
                JYDB.MF_QDIIPORTFOLIODETAIL mq) a
        WHERE
            a.rn = 1) b ON
        s.INNERCODE = b.innercode
        AND mq.ENDDATE = b.enddate
    WHERE mq.INVESTTYPE = 1 AND mq.SECUMARKET IN (72, 83, 90)
    ORDER BY s.SECUCODE, mq.SERIALNUMBER
"""

# 基金代码关联
fund_associate = """
    SELECT
        a.secucode,
        s2.secucode AS relate,
        a.CODEDEFINE AS define
    FROM
        (
        SELECT
            s.SECUCODE,
            mc.RELATEDINNERCODE,
            mc.CODEDEFINE
        FROM
            JYDB.MF_CodeRelationshipNew mc
        JOIN JYDB.SECUMAIN s ON
            mc.INNERCODE = s.INNERCODE
        WHERE
            mc.CODEDEFINE IN (21, 24)) a
    JOIN JYDB.SECUMAIN s2 ON
        a.RELATEDINNERCODE = s2.INNERCODE
"""


# 基金资产配置
fund_allocate = """
    SELECT
        SECUCODE,
        REPORTDATE AS "date",
        RINOFSTOCK AS stock,
        RINOFBOND AS bond,
        RINOFFUND AS fund,
        RINOFMETALS AS metals,
        RINOfMonetary AS monetary,
        OTHER AS other
    FROM
        (
        SELECT
            SECUCODE,
            ma.REPORTDATE,
            ma.RINOFSTOCK,
            (nvl(ma.RINOFBOND, 0)+ nvl(ma.RINOfAssetBacked, 0)+ nvl(ma.RINOfReturnSale, 0)) AS RINOFBOND,
            ma.RINOFFUND,
            (nvl(ma.RINOFMETALS, 0)+ nvl(ma.RINOfDeriva, 0)) AS RINOFMETALS,
            nvl(ma.RINOfMonetary, 0) AS RINOfMonetary,
            nvl(ma.RINOfOtherI, 0) AS OTHER,
            ROW_NUMBER() OVER(PARTITION BY secucode ORDER BY ma.REPORTDATE DESC) rn
        FROM
            JYDB.MF_AssetAllocationNew ma
        JOIN JYDB.SECUMAIN s ON
            ma.INNERCODE = s.INNERCODE ) a
    WHERE
        rn = 1
"""

fund_allocate_hk = """
    SELECT
        s.SECUCODE,
        mq.ENDDATE,
        mq.ASSETTYPE,
        mq.ASSETNAME,
        mq.RATIOINNV
    FROM
        JYDB.MF_QDIIASSETALLOCATION mq
    JOIN jydb.SECUMAIN s ON
        mq.INNERCODE = s.INNERCODE
    JOIN (
        SELECT
            *
        FROM
            (
            SELECT
                INNERCODE,
                ENDDATE,
                ROW_NUMBER() OVER(PARTITION BY INNERCODE ORDER BY mq.ENDDATE DESC) rn
            FROM
                JYDB.MF_QDIIASSETALLOCATION mq)
        WHERE
            rn = 1) a ON
        mq.INNERCODE = a.innercode
        AND mq.ENDDATE = a.enddate
    WHERE 
    mq.ASSETTYPE IN (10, 30, 10015, 40, 10075, 10089, 10090)
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

# 场内基金行情数据
fund_quote = """
    SELECT
    	s.SECUCODE,
    	qd.CLOSEPRICE,
    	qd.PREVCLOSEPRICE,
    	qd.TRADINGDAY AS "date"
    FROM
    	JYDB.QT_DAILYQUOTE qd
    JOIN JYDB.SECUMAIN s ON
    	s.INNERCODE = qd.INNERCODE
    WHERE
    	s.SECUCATEGORY IN (8, 13)
    	AND s.LISTEDSECTOR = 1
    	AND qd.TRADINGDAY > (SYSDATE - INTERVAL '14' DAY)
    ORDER BY 
    	secucode, "date"
"""

fund_quote_once = """
    SELECT
    	s.SECUCODE,
    	qd.CLOSEPRICE,
    	qd.PREVCLOSEPRICE,
    	qd.TRADINGDAY AS "date"
    FROM
    	JYDB.QT_DAILYQUOTE qd
    JOIN JYDB.SECUMAIN s ON
    	s.INNERCODE = qd.INNERCODE
    WHERE
    	s.SECUCATEGORY IN (8, 13)
    	AND s.LISTEDSECTOR = 1
    ORDER BY 
    	secucode, "date"
"""
