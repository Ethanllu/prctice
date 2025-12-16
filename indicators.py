"""
技术指标计算模块
"""
import pandas as pd
import numpy as np


class TechnicalIndicators:
    """技术指标计算类"""
    
    @staticmethod
    def calculate_ma(data, period=20):
        """
        计算移动平均线 (Moving Average)
        
        参数:
            data: 价格序列（通常是Close）
            period: 周期
        
        返回:
            Series: 移动平均线
        """
        return data.rolling(window=period).mean()
    
    @staticmethod
    def calculate_ema(data, period=20):
        """
        计算指数移动平均线 (Exponential Moving Average)
        
        参数:
            data: 价格序列
            period: 周期
        
        返回:
            Series: 指数移动平均线
        """
        return data.ewm(span=period, adjust=False).mean()
    
    @staticmethod
    def calculate_rsi(data, period=14):
        """
        计算相对强弱指标 (Relative Strength Index)
        
        参数:
            data: 价格序列
            period: 周期（默认14）
        
        返回:
            Series: RSI值 (0-100)
        """
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def calculate_macd(data, fast=12, slow=26, signal=9):
        """
        计算MACD指标 (Moving Average Convergence Divergence)
        
        参数:
            data: 价格序列
            fast: 快线周期
            slow: 慢线周期
            signal: 信号线周期
        
        返回:
            DataFrame: MACD, Signal, Histogram
        """
        ema_fast = TechnicalIndicators.calculate_ema(data, fast)
        ema_slow = TechnicalIndicators.calculate_ema(data, slow)
        macd = ema_fast - ema_slow
        signal_line = TechnicalIndicators.calculate_ema(macd, signal)
        histogram = macd - signal_line
        
        return pd.DataFrame({
            'MACD': macd,
            'Signal': signal_line,
            'Histogram': histogram
        })
    
    @staticmethod
    def calculate_bollinger_bands(data, period=20, std_dev=2):
        """
        计算布林带 (Bollinger Bands)
        
        参数:
            data: 价格序列
            period: 周期
            std_dev: 标准差倍数
        
        返回:
            DataFrame: Upper, Middle, Lower bands
        """
        middle = data.rolling(window=period).mean()
        std = data.rolling(window=period).std()
        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)
        
        return pd.DataFrame({
            'Upper': upper,
            'Middle': middle,
            'Lower': lower
        })
    
    @staticmethod
    def calculate_stochastic(high, low, close, k_period=14, d_period=3):
        """
        计算随机指标 (Stochastic Oscillator)
        
        参数:
            high: 最高价序列
            low: 最低价序列
            close: 收盘价序列
            k_period: %K周期
            d_period: %D周期
        
        返回:
            DataFrame: %K, %D
        """
        lowest_low = low.rolling(window=k_period).min()
        highest_high = high.rolling(window=k_period).max()
        
        k_percent = 100 * ((close - lowest_low) / (highest_high - lowest_low))
        d_percent = k_percent.rolling(window=d_period).mean()
        
        return pd.DataFrame({
            '%K': k_percent,
            '%D': d_percent
        })
    
    @staticmethod
    def add_all_indicators(df, ma_short=5, ma_mid=20, ma_long=60):
        """
        为DataFrame添加所有常用技术指标
        
        参数:
            df: 包含OHLCV数据的DataFrame
            ma_short: 短期均线周期
            ma_mid: 中期均线周期
            ma_long: 长期均线周期
        
        返回:
            DataFrame: 添加了技术指标的DataFrame
        """
        data = df.copy()
        close = data['Close']
        
        # 移动平均线
        data[f'MA_{ma_short}'] = TechnicalIndicators.calculate_ma(close, ma_short)
        data[f'MA_{ma_mid}'] = TechnicalIndicators.calculate_ma(close, ma_mid)
        data[f'MA_{ma_long}'] = TechnicalIndicators.calculate_ma(close, ma_long)
        
        # EMA
        data[f'EMA_{ma_mid}'] = TechnicalIndicators.calculate_ema(close, ma_mid)
        
        # RSI
        data['RSI'] = TechnicalIndicators.calculate_rsi(close)
        
        # MACD
        macd_data = TechnicalIndicators.calculate_macd(close)
        data['MACD'] = macd_data['MACD']
        data['MACD_Signal'] = macd_data['Signal']
        data['MACD_Hist'] = macd_data['Histogram']
        
        # 布林带
        bb_data = TechnicalIndicators.calculate_bollinger_bands(close)
        data['BB_Upper'] = bb_data['Upper']
        data['BB_Middle'] = bb_data['Middle']
        data['BB_Lower'] = bb_data['Lower']
        
        # 随机指标
        stoch_data = TechnicalIndicators.calculate_stochastic(
            data['High'], data['Low'], data['Close']
        )
        data['Stoch_%K'] = stoch_data['%K']
        data['Stoch_%D'] = stoch_data['%D']
        
        return data


if __name__ == '__main__':
    # 测试
    from data_fetcher import StockDataFetcher
    
    fetcher = StockDataFetcher()
    data = fetcher.get_stock_data('AAPL', period='6mo')
    
    indicators = TechnicalIndicators()
    data_with_indicators = indicators.add_all_indicators(data)
    
    print("\n技术指标计算完成")
    print(data_with_indicators[['Close', 'MA_20', 'RSI', 'MACD']].tail())

