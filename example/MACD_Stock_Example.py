from QAStrategy import QAStrategyCTABase
import QUANTAXIS as QA
import pprint

from QAStrategy.qastockbase import QAStrategyStockBase


class MACDStock(QAStrategyStockBase):

    def on_bar(self, bar):

        res = self.macd()

        print(res.iloc[-1])

        if res.DIF[-1] > res.DEA[-1]:

            print('LONG')

            if self.positions.volume_long == 0:
                self.send_order('BUY', 'OPEN', price=bar['close'], volume=1)
            if self.positions.volume_short > 0:
                self.send_order('BUY', 'CLOSE', price=bar['close'], volume=1)

        else:
            print('SHORT')
            if self.positions.volume_short == 0:
                self.send_order('SELL', 'OPEN', price=bar['close'], volume=1)
            if self.positions.volume_long > 0:
                self.send_order('SELL', 'CLOSE', price=bar['close'], volume=1)


    def macd(self,):
        return QA.QA_indicator_MACD(self.market_data)

    def risk_check(self):
        pass
        # pprint.pprint(self.qifiacc.message)


if __name__ == '__main__':
    MACD = MACDStock(code='000001', frequence='day',
         strategy_id='1dds1s2d-7902-4a85-adb2-fbac4bb977fe',start='2019-04-01', end='2019-5-01')
    MACD.run_backtest()
