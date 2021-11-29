#【FOF】SMA投资管理系统

## 一、系统介绍

SMA投资管理系统基于恒生O3.2基金管理系统和FA估值记账系统，除了跟踪产品的估值和持仓信息外，还针对FOF做了一些风险收益的扩展，方便投资经理管理多个单一FOF。

系统按功能可以分为三个大的模块，包括**产品投后信息跟踪**、**产品绩效归因**和其他预功能。

## 二、功能展示

### 1.首页

首页汇总了当前运作中的产品资产情况，上半部分为公募FOF（集合FOF和SMA单一FOF），下半部分为私募FOF；首页子菜单中还包含了资金分析、账户分析和申赎分析等情况。

首页预览图如下：

![home1-1](/images/management/1-1.png)

![home1-2](/images/management/1-2.png)

资金分析：

![home1-3](/images/management/1-3.png)

已投资底层基金的基金管理人发布的公告：

![home1-4](/images/management/1-4.png)

公告具体内容：

![home1-5](/images/management/1-5.png)

### 2.账户总览

点击任意产品的产品代码即可进入账户总览页面，账户总览主要以图表展示产品穿透后资产配置情况（权益、固收、另类等）、当日盘中估值、历史每日估值比对、历史净值、公募基金平均仓位测算。

账户总览图表如下：

![overview2-1](/images/management/2-1.png)

![overview2-2](/images/management/2-2.png)

### 3.投资分析

投资分析板块分为四个小的模块，分别为业绩指标、持仓分布、业绩归因和绩效分析。

#### 3.1 业绩指标

业绩指标展示产品收益和风险指标数据，以及产品拆分到各类资产上的收益率。

![analysis3-1](/images/management/3-1.png)

#### 3.2 持仓分布

持仓分布展示产品持仓情况，包括穿透与非穿透的、行业、主题等，一个可以分为5个功能区，包括持基分析、持股分析、申赎渠道、资产分类和ETF表现。

##### 3.2.1 持基分析

产品持有基金展示，包括基金的分类信息、持仓信息、持有期业绩表现和基金业绩表现与开放信息。
![analysis3-2](/images/management/3-2.png)

##### 3.2.2 持股分析

根据持有基金的最新一期报告，穿透查看组合持股信息。
![analysis3-3](/images/management/3-3.png)

##### 3.2.3 申赎渠道

申赎渠道主要展示基金在不同渠道购买的金额以及当前的持仓份额，方便投资经理减仓。

##### 3.2.4 资产分类

根据基金类型查看组合在不同类型基金上的仓位暴露。
![analysis3-4](/images/management/3-4.png)

##### 3.2.5 ETF表现

统计ETF交易收益情况，如交易记录、胜率、损益等。
![analysis3-5](/images/management/3-5.png)

#### 3.3 业绩归因

业绩归因板块展示组合归因数据，包括Brinson归因，RBSA风格系数、Barra风格暴露和滚动波动率。
页面预览如下：
![analysis3-6](/images/management/3-6.png)
![analysis3-7](/images/management/3-7.png)

#### 3.4 绩效分析

对组合底层基金在不同分类下的聚合统计。
页面预览如下：
![analysis3-8](/images/management/3-8.png)

### 4.投资历史

展示组合交易记录，包含交易类型、金额、成交数量和成交价格。

![history4-1](/images/management/4-1.png)

### 5.调仓贡献

选择历史上某个调仓日，会展示从改日起调仓后持仓的拟合业绩与调仓前的拟合业绩，考虑交易费用等因素，考察调仓是否创造了正向收益。

![mock5-1](/images/management/5-1.png)

### 6.模拟投资

对现有持仓基金调仓试算。

![emulate6-1](/images/management/6-1.png)

### 7.资产配置

根据均值方差模型，试算的组合最近配置比例，仅作为标准组合业绩参考。

![allocate7-1](/images/management/7-1.png)

![allocate7-2](/images/management/7-2.png)

### 8.资金流向

监控每日主动买卖成交额，与均线比较，判断是否有超买超卖。

![cashflow8-1](/images/management/8-1.png)

![cashflow8-2](/images/management/8-2.png)

### 9.盘中估值

基金盘中估值。

![valuation9-1](/images/management/9-1.png)

## 三、技术栈

### 1.数据库

数据库采用MySQL 8.x，数据源包括恒生聚源数据、通联数据和网络爬虫数据。

数据处理上，

1. 聚源和通联数据采用Python编写SQL Template，根据特定字段增量更新数据，日频；
2. 爬虫数据采用异步方式，进程监控采用supervisor，主要采集新浪财经A股、港股和ETF盘中数据；
3. 组合数据主要源于SMA客户服务系统，采用异步rpc方式与该程序通信获取；
4. 所有任务按规则定时运行，定时任务管理框架采用django-q，分布式任务执行则是基于rpc实现。

### 2.后端

后端采用Python的Django 3.x框架，初版采用同步方式，但由于图表瞬时请求过多导致后端响应很慢，因此进行过一次迭代升级，升级后通过以下方式来保证性能：

1. 同步api全部更改异步api；
2. 盘中估值采用websocket方式推送；
3. 多个程序间通信采用rpc；
4. 多个进程做负载均衡。

### 3.前端

前端语言采用TypeScript，框架使用Ant Design Pro，图表插件使用echarts。

