"""
index
~~~~~~~~~~~~~~~~~~~~~~~
@author: chuanchao.peng
@date: 2020-09-04
@desc: sql语句模板
"""

# 指数基础信息 需要替换 <codelist>
basic_info = """
SELECT a.SECUCODE,
       a.SECUABBR,
       a.CHINAME,
       a.MS   AS CATEGORY,
       cs2.MS AS COMPONENT,
       a.BASEDATE
FROM (
         SELECT s.INNERCODE,
                s.SECUCODE,
                s.SECUABBR,
                s.CHINAME,
                cs.MS,
                li.BASEDATE,
                li.COMPONENTTYPE
         FROM jydb.SECUMAIN s
                  JOIN jydb.LC_INDEXBASICINFO li ON
             s.INNERCODE = li.INDEXCODE
                  JOIN jydb.CT_SYSTEMCONST cs ON
             li.INDEXTYPE = cs.DM
         WHERE cs.LB = 1266
           AND s.SECUCODE in (<codelist>) ) a
         JOIN jydb.CT_SYSTEMCONST cs2 ON a.COMPONENTTYPE = cs2.DM
WHERE LB = 1008
"""

# 指数交易数据, 需要替换<date>和<code>
# 普通
quote = """
SELECT s.SECUCODE,
       qi.PREVCLOSEPRICE AS PRE_CLOSE,
       qi.CLOSEPRICE     AS "CLOSE",
       qi.CHANGEPCT      AS "CHANGE",
       qi.TRADINGDAY     AS "DATE"
FROM jydb.QT_INDEXQUOTE qi
         JOIN jydb.SECUMAIN s ON
    qi.INNERCODE = s.INNERCODE
WHERE s.SECUCODE = '<code>'
  AND qi.TRADINGDAY > TO_DATE('<date>', 'yyyy-MM-dd')
"""

# 中债
quote_cb = """
SELECT s.SECUCODE,
       bc.PREVCLOSEPRICE AS PRE_CLOSE,
       bc.CLOSEPRICE     AS "CLOSE",
       bc.CHANGEPCT      AS "CHANGE",
       bc.TRADINGDAY     AS "DATE"
FROM jydb.BOND_CHINABONDINDEXQUOTE bc
         JOIN jydb.SECUMAIN s ON
    bc.INNERCODE = s.INNERCODE
WHERE s.SECUCODE = '<code>'
  AND bc.TRADINGDAY > TO_DATE('<date>', 'yyyy-MM-dd')
"""

# 境外
quote_os = """
SELECT s.SECUCODE,
       qo.PREVCLOSEPRICE AS "PRE_CLOSE",
       qo.CLOSEPRICE     AS "CLOSE",
       qo.CHANGEPCT      AS "CHANGE",
       qo.TRADINGDAY     AS "DATE"
FROM JYDB.QT_OSINDEXQUOTE qo
         JOIN JYDB.SECUMAIN s ON
    qo.INDEXCODE = s.INNERCODE
WHERE s.SECUCODE = '<code>'
  AND qo.TRADINGDAY > TO_DATE('<date>', 'yyyy-MM-dd')
"""