from QAStrategy import QAStrategyCTABase
import QUANTAXIS as QA
import pprint
import pandas as pd
import numpy as np

from QAStrategy.qastockbase import QAStrategyStockBase

def MACD_JCSC(dataframe, SHORT=12, LONG=26, M=9):
    """
    1.DIF向上突破DEA，买入信号参考。
    2.DIF向下跌破DEA，卖出信号参考。
    """
    CLOSE = dataframe.close
    DIFF = QA.EMA(CLOSE, SHORT) - QA.EMA(CLOSE, LONG)
    if DIFF is None or np.isnan(DIFF[-1]):
        return None

    DEA = QA.EMA(DIFF, M)
    MACD = 2*(DIFF-DEA)

    CROSS_JC = QA.CROSS(DIFF, DEA)
    CROSS_SC = QA.CROSS(DEA, DIFF)
    ZERO = 0
    df=pd.DataFrame({'DIFF': DIFF, 'DEA': DEA, 'MACD': MACD, 'CROSS_JC': CROSS_JC, 'CROSS_SC': CROSS_SC, 'ZERO': ZERO})

    macd_rank = df.rank()
    df['DIFF_RANK'] = macd_rank['DIFF'] / len(df['DIFF'][df['DIFF'].notna()])
    df['DEA_RANK'] = macd_rank['DEA'] / len(df['DEA'][df['DEA'].notna()])
    df['MACD_RANK'] = macd_rank['MACD'] / len(df['MACD'][df['MACD'].notna()])


    count=1

    if df.MACD.tail(1)[0] > 0:
        sign = 1
    else:
        sign = -1
    for i in range(2,11):
        r=df.MACD.tail(i)[0]
        if r*sign>0:
            count=count+1
        else:
            break

    # 1表示为向上上涨阶段，-1表示下跌阶段
    df['SIGN']=sign
    df['COUNT']=count

    return df


class MACDStock(QAStrategyStockBase):

    def on_bar(self, data):
        #         print(data)
        code = self.code
        start = self.start
        macd = MACD_JCSC(self.market_data)  # 最新的macd
        if macd is None or macd.empty:
            print('%s %s 行情MACD为空' % (code, start))
            return

        trade_time = self.market_datetime[-1]
        if macd['SIGN'][-1] == 1 and macd['COUNT'][-1] == 2 and macd['DIFF'][-1] < 0 and macd['DEA'][-1] < 0:
            type = 'BUY'
        elif macd['SIGN'][-1] == -1 and macd['COUNT'][-1] == 2 and macd['DIFF'][-1] > 0 and macd['DEA'][-1] > 0:
            type = 'SELL'
        else:
            type = 'WAIT'

        if type == 'WAIT':
            #             qa.QA_util_log_info('%s %s 当前不具备交易条件' %(code,trade_time))
            mes_dict = None
        else:
            QA.QA_util_log_info('%s %s 准备交易 %s MACD:%s %s %s ' % (
            trade_time, code, type, macd['COUNT'][-1], macd['DIFF'][-1], macd['DEA'][-1]))

            if type == 'BUY':
                self.send_order('BUY', 'OPEN', price=data['close'], volume=100)
                self.send_order('SELL', 'CLOSE', price=data['close'], volume=100)
            elif type == 'SELL':
                self.send_order('SELL', 'OPEN', price=data['close'], volume=100)
                self.send_order('BUY', 'CLOSE', price=data['close'], volume=100)

    def risk_check(self):
        pass
        # pprint.pprint(self.qifiacc.message)


if __name__ == '__main__':
    g = MACDStock(code='000001', portfolio='x3', frequence='1min', start='2019-04-20', end='2019-05-01', strategy_id='x3')
    # MACD = MACDStock(code='000001', frequence='day',
    #      strategy_id='1dds1s2d-7902-4a85-adb2-fbac4bb977fe',start='2019-04-20', end='2019-5-01')
    g.run_backtest()
