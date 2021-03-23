import time
import re
import pandas as pd
import traceback

from crawl import models
from sql.progress import progressbar

BASE_URL = 'http://fundf10.eastmoney.com/jjfl_000001.html'
PATTERN = re.compile('\d+')
DAY = re.compile('(\d+天)|(\d+年)|(\d+个月)')


def target_funds():
    funds = models.Holding.objects.values('secucode').distinct()
    funds = {x['secucode'] for x in funds}
    exists = models.FundPurchaseFee.objects.values('secucode').distinct()
    exists = {x['secucode'] for x in exists}
    funds = [x for x in funds if x not in exists]
    return funds


def judge_buy_amount(word: str):
    """通过大于、小于等逻辑判断次，解析上下边界"""
    if all({"大于等于" in word, "小于" in word}):
        num = PATTERN.findall(word)
        return int(num[0]), int(num[1])

    elif "大于等于" in word:
        num = PATTERN.findall(word)[0]
        num = int(num)
        return num, None

    elif "小于" in word:
        num = PATTERN.findall(word)[0]
        num = int(num)
        return 0, num

    else:
        return 0, None


def judge_buy_fee(word: str):
    """根据输入的字符串获取真实的费率
    形如：  1.50% | 0.15% | 0.15%
    """
    if "每笔" in word:
        num = PATTERN.findall(word)[0]
        num = int(num)
        return num
    words = word.split('|')
    # 0.15%
    word = words[-1].strip()
    # 0.0015
    num = float(word[:-1]) / 100
    return num


def judge_sell_days(word: str):
    """判断基金赎回适用期限
    形如：大于等于7天，小于1年 | 大于等于2年
    """
    split = re.findall(DAY, word)
    ret = []
    # [('7天', '')]
    for first in split:
        # ('7天', '')
        for second in first:
            if '天' in second:
                num = int(PATTERN.findall(second)[0])
                ret.append(num)
            elif '月' in second:
                num = int(PATTERN.findall(second)[0]) * 30
                ret.append(num)
            elif '年' in second:
                num = int(PATTERN.findall(second)[0]) * 365
                ret.append(num)
    if all({"大于" in word, "小于" in word}):
        return ret[0], ret[1]

    elif "大于" in word:
        return ret[0], None

    elif "小于" in word:
        return 0, ret[0]

    elif '本基金不收取赎回费用' in word:
        return 0, None


class CrawlFee(object):
    data = None

    def __init__(self, secucode):
        self.s = secucode
        self.fund = models.Funds.objects.get(secucode=secucode)
        self.get_data()

    def get_data(self):
        """获取全部数据"""
        url = BASE_URL.replace('000001', self.s)
        data = pd.read_html(url)
        self.data = data

    def process_buy(self):
        if len(self.data) >= 10:
            data = self.data[-3]
        elif len(self.data) == 9:
            data = self.data[-2]
        else:
            return
        data.columns = ['适用金额', '适用期限', '适用费率']
        data['适用金额'] = data['适用金额'].apply(judge_buy_amount)
        data['适用费率'] = data['适用费率'].apply(judge_buy_fee)
        data = data.dropna(how='any')
        for _, r in data.iterrows():
            amount = r['适用金额']
            models.FundPurchaseFee.objects.update_or_create(secucode=self.fund, low=amount[0], operate='buy', defaults={
                'low': amount[0], 'high': amount[1], 'fee': r['适用费率']
            })

    def process_sell(self):
        data = self.data[-1]
        data.columns = ['适用金额', '适用期限', '适用费率']
        data['适用期限'] = data['适用期限'].apply(judge_sell_days)
        data['适用费率'] = data['适用费率'].apply(judge_buy_fee)
        data = data.dropna(how='any')
        for _, r in data.iterrows():
            amount = r['适用期限']
            models.FundPurchaseFee.objects.update_or_create(
                secucode=self.fund, low=amount[0], operate='sell', defaults={
                    'low': amount[0], 'high': amount[1], 'fee': r['适用费率']
                })


def _commit(funds: list or set, retry=0):
    if retry > 3 or not funds:
        return
    failed = []
    for i, fund in enumerate(funds):
        try:
            cf = CrawlFee(fund)
            cf.process_buy()
            cf.process_sell()
        except Exception as e:
            failed.append(e)
        time.sleep(0.5)
        progressbar(i, len(funds))
    _commit(failed, retry+1)


def commit_fund_fee_em():
    funds = target_funds()
    _commit(funds)


if __name__ == '__main__':
    commit_fund_fee_em()
