import time
import sys


def progressbar(current: int, total: int):
    # 转化为百分占比
    c = int(100 * current / total)
    symbol = ''.join(['\u2708'] * int(c / 5))
    sys.stdout.write(f'\r{c/100: <3.0%} {symbol}')
    sys.stdout.flush()


if __name__ == '__main__':
    total = 100
    for i in range(0, 100):
        progressbar(i, total)
