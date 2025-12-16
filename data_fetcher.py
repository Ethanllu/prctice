"""
美股数据获取模块
使用yfinance库获取美股数据
"""
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import os
from config import DATA_DIR


class StockDataFetcher:
    """美股数据获取类"""
    
    def __init__(self):
        self.data_dir = DATA_DIR
    
    def get_stock_data(self, symbol, period='1y', interval='1d', save_cache=True):
        """
        获取美股数据
        
        参数:
            symbol: 美股代码（如 'AAPL', 'MSFT', 'TSLA'）
            period: 时间周期 ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max')
            interval: 数据间隔 ('1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo')
            save_cache: 是否保存缓存
        
        返回:
            pandas DataFrame with columns: Open, High, Low, Close, Volume
        """
        try:
            # 尝试从缓存读取
            cache_file = os.path.join(self.data_dir, f'{symbol}_{period}_{interval}.csv')
            if os.path.exists(cache_file):
                data = pd.read_csv(cache_file, index_col=0, parse_dates=True)
                # 检查缓存是否过期（超过1小时）
                file_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
                if datetime.now() - file_time < timedelta(hours=1):
                    print(f"从缓存加载数据: {symbol}")
                    return data
            
            # 从yfinance获取数据
            print(f"正在获取股票数据: {symbol}")
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, interval=interval)
            
            if data.empty:
                raise ValueError(f"无法获取股票数据: {symbol}")
            
            # 保存缓存
            if save_cache:
                data.to_csv(cache_file)
                print(f"数据已保存到缓存: {cache_file}")
            
            return data
        
        except Exception as e:
            print(f"获取股票数据时出错: {e}")
            return pd.DataFrame()
    
    def get_stock_info(self, symbol):
        """
        获取美股基本信息
        
        参数:
            symbol: 美股代码
        
        返回:
            dict: 股票信息
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            return {
                'symbol': symbol,
                'name': info.get('longName', 'N/A'),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'market_cap': info.get('marketCap', 0),
                'current_price': info.get('currentPrice', 0),
                'pe_ratio': info.get('trailingPE', 0),
                'dividend_yield': info.get('dividendYield', 0),
            }
        except Exception as e:
            print(f"获取股票信息时出错: {e}")
            return {}
    
    def get_multiple_stocks(self, symbols, period='1y', interval='1d'):
        """
        批量获取多只美股数据
        
        参数:
            symbols: 美股代码列表
            period: 时间周期
            interval: 数据间隔
        
        返回:
            dict: {symbol: DataFrame}
        """
        data_dict = {}
        for symbol in symbols:
            data = self.get_stock_data(symbol, period, interval)
            if not data.empty:
                data_dict[symbol] = data
        return data_dict


if __name__ == '__main__':
    # 测试
    fetcher = StockDataFetcher()
    data = fetcher.get_stock_data('AAPL', period='6mo')
    print(f"\n获取到 {len(data)} 条数据")
    print(data.head())
    print(f"\n最新价格: {data['Close'].iloc[-1]:.2f}")

