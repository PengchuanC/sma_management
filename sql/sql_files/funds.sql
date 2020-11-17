-- 基金数据

-- 基金代码及简称
select secucode, secuabbr as secuname from jydb.secumain where secucategory=8

-- 基金累计净值数据
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