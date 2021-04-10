import requests
from datetime import datetime,date,timedelta
#python_bitbankccのパッケージをインポート
import python_bitbankcc
import pandas as pd
import mplfinance as mpf
import matplotlib.pyplot as plt
import numpy as np
import time

class get_data():
  #APIオブジェクトを取得
  API = python_bitbankcc.public()

  def __init__(self,pair):
    self.pair = pair

  def get_ticker(self):
    #ティッカー情報を表示
    ticker = get_data.API.get_ticker(self.pair)
    
    ticker_info = "{:8}".format('Pair') + '\t' + 'Now' + '\t'  + 'Sell' + '\t' + 'Buy' \
          + '\t' + 'High' + '\t' +  'Low' + '\t' + 'Vol' + '\t' + '\n' \
          "{:8}".format(self.pair) + '\t' \
              + ticker['last'] + '\t' \
              + ticker['sell'] + '\t' \
              + ticker['buy'] + '\t' \
              + ticker['high'] + '\t' \
              + ticker['low'] + '\t' \
              + ticker['vol']

    return ticker_info

  #RSIクラス
  def close_and_rsi(self):

    #間隔を指定
    candle_type = '1day'
    #取得開始日を指定
    start_day = "20210101"
    start_dt = datetime.strptime(start_day,"%Y%m%d")
    #取得終了日を指定
    today =  datetime.today()
    today = today - timedelta(hours=8)

    dt = start_dt
      
    #ローソク足情報
    ohlcv = []
      
    while dt <= today:
      #指定期間のロウソク足データの取得
      ohlcv.extend(get_data.API.get_candlestick(self.pair,candle_type,datetime.strftime(dt,"%Y"))['candlestick'][0]['ohlcv'])
      dt = dt + timedelta(days=365)

    #DataFrame形式に変更
    df = pd.DataFrame(ohlcv,columns = ['open', 'high','low','close','volume','time']);
    #日時のフォーマットを変更
    df['time'] = [datetime.fromtimestamp(float(time)/1000) for time in df['time']]
    #日時をインデックスに変更
    df.set_index('time',inplace=True)
    #中身の型変換
    df = df[['open', 'high','low','close','volume']].astype('float64')

    #終値抽出
    close = df['close']
    #前日差分
    diff = close.diff()
    #最初の欠損を削除
    diff = diff[1:]

    up,down = diff.copy(),diff.copy()
    up[up < 0] = 0
    down[down > 0] = 0

    #RS(Relative Strength)の計算
    up_sma_14 = up.rolling(window = 14 ,center= False).mean()
    down_sma_14 = down.abs().rolling(window = 14,center = False).mean()

    #RSI(Relative Strength Index)計算
    RS = up_sma_14 / down_sma_14
    RSI = 100.0 - (100.0 / (1.0 + RS))

    #グラフの作成 close と RSI
    fig,(ax1,ax2) = plt.subplots(2,1,gridspec_kw={'height_ratios':[1,1]})
    #close plot
    ax1.plot(close.index,close)
    
    #RSI plot
    ax2.plot(RSI.index,RSI)
    
    #グラフ周りの設定
    #グリッド
    plt.ion()
    ax1.grid()
    ax2.grid()
    #タイトル
    ax1.set_title(str(self.pair) + '/JPY',fontsize=20)
    ax2.set_title('RSI(Relative Strength Index)',fontsize=20)

    #買われ過ぎ 売られ過ぎ可視化
    ax2.axhspan(0,30,facecolor = 'red',alpha = 0.5)
    ax2.axhspan(70,100,facecolor = 'lime',alpha = 0.5)

    #重なり防止
    fig.tight_layout()

    #画像保存
    plt.savefig('Close_and_RSI_'+ str(self.pair)+'.png')

    plt.close()

    #serise型の末尾の値のみ抽出
    return int(RSI.iloc[-1])

  def candle_plot(self):

    #取得開始日を指定
    start_day = "20210101"
    start_dt = datetime.strptime(start_day,"%Y%m%d")
    #取得終了日を指定
    today =  datetime.today()
    today = today - timedelta(hours=8)
    dt = start_dt
    
    #間隔を指定
    candle_type = '1day'

    #ローソク足情報
    ohlcv_day = []
    ohlcv_4hour = []

    #日足ローソク足情報取得 
    while dt <= today:
      #指定期間のロウソク足データの取得
      ohlcv_day.extend(get_data.API.get_candlestick(self.pair,candle_type,datetime.strftime(dt,"%Y"))['candlestick'][0]['ohlcv'])
      dt = dt + timedelta(days=365)
  
    #初期化
    dt_4hour = start_dt
    #間隔を指定
    candle_type = '4hour'

    #４時間足ローソク足情報取得
    while dt_4hour <= today:
      #指定期間のロウソク足データの取得
      ohlcv_4hour.extend(get_data.API.get_candlestick(self.pair,candle_type,datetime.strftime(dt_4hour,'%Y'))['candlestick'][0]['ohlcv'])
      dt_4hour = dt_4hour + timedelta(days=365)

    #DataFrame形式に変更
    data_day = pd.DataFrame(ohlcv_day,columns = ['open', 'high','low','close','volume','time']);
    #日時のフォーマットを変更
    data_day['time'] = [datetime.fromtimestamp(float(time)/1000) for time in data_day['time']]
    #日時をインデックスに変更
    data_day.set_index('time',inplace=True)

    #DataFrame形式に変更
    data_4hour = pd.DataFrame(ohlcv_4hour,columns = ['open', 'high','low','close','volume','time']);
    #日時のフォーマットを変更
    data_4hour['time'] = [datetime.fromtimestamp(float(time)/1000) for time in data_4hour['time']]
    #日時をインデックスに変更
    data_4hour.set_index('time',inplace=True)

    #中身の型変換
    df_day = data_day[['open', 'high','low','close','volume']].astype('float64')
    df_4hour = data_4hour[['open', 'high','low','close','volume']].astype('float64')

    fig_day = plt.figure(figsize=(10,4),dpi=120)
    plt.ion()
    #ローソク足チャートを作成する
    mpf.plot(df_day, type='candle', figratio=(24,8),
      volume=True, mav=(5, 25), style='yahoo')
    plt.close(fig_day)
    #画像保存
    plt.savefig('candle_day_'+ str(self.pair) + '.png')

    fig_4hour = plt.figure(figsize=(10,4),dpi=120)
    plt.ion()
    #ローソク足チャートを作成する
    mpf.plot(df_4hour, type='candle', figratio=(24,8),
      volume=True, mav=(12,25), style='yahoo')
    plt.close(fig_day)
    #画像保存
    plt.savefig('candle_4hour_'+ str(self.pair) + '.png')

class line_class():

  def __init__(self,token,api_url):
    self.token = token
    self.api_url = api_url
    self.token_dic = {'Authorization' : 'Bearer' + ' ' + token}

  def send_message(self,message):
    #情報の辞書型
    send_dic  = {'message' : '\n' + message}

    #LINE通知を送る(200:成功 400:リクエストが不正 401: アクセストークンが無効)
    requests.post(self.api_url,headers = self.token_dic,data = send_dic)

  def send_file(self,message,file):
    send_dic  = {'message' : '\n' + message}
    send_files = {'imageFile' : open(file,'rb')}

    #画像+説明送信
    requests.post(self.api_url,headers = self.token_dic,params = send_dic,files = send_files)

def jage(RSI):

    if RSI >=70:
      message = 'RSI='+str(RSI)+'\n買われ過ぎです'
    elif RSI <= 30:
      message = 'RSI='+str(RSI)+'\n売られ過ぎです。'
    else:
      message = 'RSI='+str(RSI)+'\n中立です。'

    return message

def main():

  #データ収集クラス
  pub_data_xrp = get_data('xrp_jpy')
  pub_data_eth = get_data('eth_jpy')
  pub_data_btc = get_data('btc_jpy')
  #ティッカー情報取得1
  ticker_info_xrp = pub_data_xrp.get_ticker()
  ticker_info_eth = pub_data_eth.get_ticker()
  ticker_info_btc = pub_data_btc.get_ticker()
  #ローソク足作成
  pub_data_xrp.candle_plot()
  RSI_xrp = pub_data_xrp.close_and_rsi()
  pub_data_eth.candle_plot()
  RSI_eth = pub_data_eth.close_and_rsi()
  pub_data_btc.candle_plot()
  RSI_btc = pub_data_btc.close_and_rsi()
  #RSI判定&メッセージ作成
  XRP_RSI_message = 'xrp_jpy\n' + jage(RSI_xrp)
  ETH_RSI_message = 'eth_jpy\n' +jage(RSI_eth)
  BTC_RSI_message = 'btc_jpy\n' + jage(RSI_btc)
  #ラインクラス
  pub_line = line_class('ibscPdt9IYBwf6hHQIg7TJS4S61ivvZo9vZfu9116Iu','https://notify-api.line.me/api/notify')
  #現在時刻取得
  today =  datetime.today()
  #変換
  now = datetime.strftime(today,"%m月%d日　%H:%M")
  #ラインにメッセージ＆ファイル送信
  pub_line.send_message(now)
  
  pub_line.send_message(ticker_info_btc)
  pub_line.send_message(BTC_RSI_message)
  pub_line.send_message(ticker_info_eth)
  pub_line.send_message(ETH_RSI_message)
  pub_line.send_message(ticker_info_xrp)
  pub_line.send_message(XRP_RSI_message)
  pub_line.send_file('ローソク足（1日足)','candle_day_xrp_jpy.png')
  pub_line.send_file('ローソク足（４時間足)','candle_4hour_xrp_jpy.png')
  pub_line.send_file('RSI(買い圧売り圧)','Close_and_RSI_xrp_jpy.png')

if __name__ == '__main__':
  main()