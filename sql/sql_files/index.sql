-- 目标指数
-- H00300 沪深300全收益 | 000300 沪深300 | H00905 中证500全收益 | 000905 中证500
-- Y00001 中债-总指数(wind-中债总财富指数) | Y00052 中债3-5年国债指数
-- Y00045 中债-企业债AA指数
-- H11025 货币基金 | 000832 中证转债
-- HSI 恒生指数 | HSITR 恒生指数全收益
-- AU9999.SGE 黄金 聚源无此数据
-- 巨潮 风格指数 399373 399372 399377 399376


-- 查询指数基本信息
SELECT a.INNERCODE,
       a.SECUCODE,
       a.SECUABBR,
       a.CHINAME,
       a.MS   AS CATEGORY,
       cs2.MS AS "COMPONENT",
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
           AND s.SECUABBR LIKE '%标普500%') a
         JOIN jydb.CT_SYSTEMCONST cs2 ON a.COMPONENTTYPE = cs2.DM
WHERE LB = 1008;

SELECT a.SECUCODE,
       a.SECUABBR,
       a.CHINAME,
       a.MS   AS CATEGORY,
       cs2.MS AS "COMPONENT"
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
           AND s.SECUCODE = '000001') a
         JOIN jydb.CT_SYSTEMCONST cs2 ON a.COMPONENTTYPE = cs2.DM
WHERE LB = 1008;


-- 指数行情 指数行情表
SELECT s.SECUCODE,
       qi.PREVCLOSEPRICE AS PRE_CLOSE,
       qi.CLOSEPRICE     AS "CLOSE",
       qi.CHANGEPCT      AS "CHANGE",
       qi.TRADINGDAY     AS "DATE"
FROM jydb.QT_INDEXQUOTE qi
         JOIN jydb.SECUMAIN s ON
    qi.INNERCODE = s.INNERCODE
WHERE s.SECUCODE = '000001'
  AND qi.TRADINGDAY = TO_DATE('2020-09-03', 'yyyy-MM-dd');

-- 指数行情 中债
SELECT s.SECUCODE,
       bc.PREVCLOSEPRICE AS PRE_CLOSE,
       bc.CLOSEPRICE     AS "CLOSE",
       bc.CHANGEPCT      AS "CHANGE",
       bc.TRADINGDAY     AS "DATE"
FROM jydb.BOND_CHINABONDINDEXQUOTE bc
         JOIN jydb.SECUMAIN s ON
    bc.INNERCODE = s.INNERCODE
WHERE s.SECUCODE = 'Y00045'
  AND bc.TRADINGDAY = TO_DATE('2020-09-03', 'yyyy-MM-dd');

-- 指数行情 境外
SELECT s.SECUCODE,
       qo.PREVCLOSEPRICE AS "PRE_CLOSE",
       qo.CLOSEPRICE     AS "CLOSE",
       qo.CHANGEPCT      AS "CHANGE",
       qo.TRADINGDAY     AS "DATE"
FROM JYDB.QT_OSINDEXQUOTE qo
         JOIN JYDB.SECUMAIN s ON
    qo.INDEXCODE = s.INNERCODE
WHERE s.SECUCODE = 'HSITR'
  AND qo.TRADINGDAY = TO_DATE('2020-09-03', 'yyyy-MM-dd');