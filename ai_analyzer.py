"""
AI分析模块
使用机器学习模型进行美股分析和预测
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error
from indicators import TechnicalIndicators
from config import PREDICTION_DAYS, TRAIN_TEST_SPLIT


class StockAnalyzer:
    """美股AI分析类"""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.indicators = TechnicalIndicators()
    
    def prepare_features(self, df):
        """
        准备特征数据
        
        参数:
            df: 包含技术指标的DataFrame
        
        返回:
            tuple: (X, y) 特征和标签
        """
        # 添加技术指标
        data = self.indicators.add_all_indicators(df.copy())
        
        # 选择特征列
        feature_cols = [
            'Open', 'High', 'Low', 'Close', 'Volume',
            'MA_5', 'MA_20', 'MA_60',
            'EMA_20',
            'RSI',
            'MACD', 'MACD_Signal', 'MACD_Hist',
            'BB_Upper', 'BB_Middle', 'BB_Lower',
            'Stoch_%K', 'Stoch_%D'
        ]
        
        # 添加价格变化特征
        data['Price_Change'] = data['Close'].pct_change()
        data['Volume_Change'] = data['Volume'].pct_change()
        data['High_Low_Ratio'] = data['High'] / data['Low']
        
        feature_cols.extend(['Price_Change', 'Volume_Change', 'High_Low_Ratio'])
        
        # 移除NaN值
        data = data.dropna()
        
        # 准备特征和目标
        X = data[feature_cols].values
        y = data['Close'].shift(-PREDICTION_DAYS).values  # 预测未来N天的收盘价
        
        # 移除最后N行（没有未来数据）
        valid_indices = ~np.isnan(y)
        X = X[valid_indices]
        y = y[valid_indices]
        
        return X, y, data.index[valid_indices]
    
    def train_model(self, df):
        """
        训练预测模型
        
        参数:
            df: 股票数据DataFrame
        
        返回:
            dict: 训练结果信息
        """
        print("正在准备特征数据...")
        X, y, indices = self.prepare_features(df)
        
        if len(X) < 100:
            raise ValueError("数据量不足，无法训练模型")
        
        # 划分训练集和测试集
        split_idx = int(len(X) * TRAIN_TEST_SPLIT)
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        # 标准化特征
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # 训练模型
        print("正在训练模型...")
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        self.model.fit(X_train_scaled, y_train)
        
        # 评估模型
        y_pred = self.model.predict(X_test_scaled)
        mse = mean_squared_error(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        
        # 计算准确率（方向预测准确率）
        direction_accuracy = np.mean(
            np.sign(y_test[1:] - y_test[:-1]) == np.sign(y_pred[1:] - y_pred[:-1])
        ) * 100
        
        results = {
            'rmse': rmse,
            'mae': mae,
            'direction_accuracy': direction_accuracy,
            'train_size': len(X_train),
            'test_size': len(X_test)
        }
        
        print(f"\n模型训练完成!")
        print(f"RMSE: {rmse:.2f}")
        print(f"MAE: {mae:.2f}")
        print(f"方向预测准确率: {direction_accuracy:.2f}%")
        
        return results
    
    def predict(self, df):
        """
        预测未来价格
        
        参数:
            df: 股票数据DataFrame
        
        返回:
            dict: 预测结果
        """
        if self.model is None:
            raise ValueError("模型未训练，请先调用train_model()")
        
        # 准备最新数据
        X, _, _ = self.prepare_features(df)
        if len(X) == 0:
            raise ValueError("无法准备特征数据")
        
        # 使用最新数据预测
        X_latest = X[-1:].reshape(1, -1)
        X_latest_scaled = self.scaler.transform(X_latest)
        
        predicted_price = self.model.predict(X_latest_scaled)[0]
        current_price = df['Close'].iloc[-1]
        
        change_percent = ((predicted_price - current_price) / current_price) * 100
        
        from datetime import datetime, timedelta
        
        # 计算预测日期范围（从今天开始）
        today = datetime.now().date()
        prediction_start = today
        prediction_end = today + timedelta(days=PREDICTION_DAYS)
        
        return {
            'current_price': current_price,
            'predicted_price': predicted_price,
            'prediction_days': PREDICTION_DAYS,
            'change_percent': change_percent,
            'trend': '上涨' if change_percent > 0 else '下跌',
            'prediction_start': prediction_start.strftime('%Y-%m-%d'),
            'prediction_end': prediction_end.strftime('%Y-%m-%d')
        }
    
    def analyze_signals(self, df):
        """
        分析买卖信号
        
        参数:
            df: 包含技术指标的DataFrame
        
        返回:
            dict: 信号分析结果
        """
        data = self.indicators.add_all_indicators(df.copy())
        latest = data.iloc[-1]
        
        signals = []
        signal_strength = 0
        
        # RSI信号
        rsi = latest['RSI']
        if rsi < 30:
            signals.append('RSI超卖，可能买入机会')
            signal_strength += 1
        elif rsi > 70:
            signals.append('RSI超买，可能卖出机会')
            signal_strength -= 1
        
        # MACD信号
        if latest['MACD'] > latest['MACD_Signal'] and data.iloc[-2]['MACD'] <= data.iloc[-2]['MACD_Signal']:
            signals.append('MACD金叉，买入信号')
            signal_strength += 2
        elif latest['MACD'] < latest['MACD_Signal'] and data.iloc[-2]['MACD'] >= data.iloc[-2]['MACD_Signal']:
            signals.append('MACD死叉，卖出信号')
            signal_strength -= 2
        
        # 均线信号
        if latest['MA_5'] > latest['MA_20'] > latest['MA_60']:
            signals.append('均线多头排列，看涨')
            signal_strength += 1
        elif latest['MA_5'] < latest['MA_20'] < latest['MA_60']:
            signals.append('均线空头排列，看跌')
            signal_strength -= 1
        
        # 布林带信号
        if latest['Close'] < latest['BB_Lower']:
            signals.append('价格触及布林带下轨，可能反弹')
            signal_strength += 1
        elif latest['Close'] > latest['BB_Upper']:
            signals.append('价格触及布林带上轨，可能回调')
            signal_strength -= 1
        
        # 综合判断
        if signal_strength >= 2:
            recommendation = '买入'
        elif signal_strength <= -2:
            recommendation = '卖出'
        else:
            recommendation = '持有'
        
        return {
            'recommendation': recommendation,
            'signal_strength': signal_strength,
            'signals': signals,
            'current_price': latest['Close'],
            'rsi': rsi,
            'macd': latest['MACD'],
            'macd_signal': latest['MACD_Signal']
        }
    
    def full_analysis(self, df):
        """
        完整分析（训练模型 + 预测 + 信号分析）
        
        参数:
            df: 股票数据DataFrame
        
        返回:
            dict: 完整分析结果
        """
        print("\n=== 开始AI分析 ===")
        
        # 训练模型
        train_results = self.train_model(df)
        
        # 预测
        prediction = self.predict(df)
        
        # 信号分析
        signals = self.analyze_signals(df)
        
        return {
            'model_performance': train_results,
            'prediction': prediction,
            'signals': signals
        }


if __name__ == '__main__':
    # 测试
    from data_fetcher import StockDataFetcher
    
    fetcher = StockDataFetcher()
    data = fetcher.get_stock_data('AAPL', period='1y')
    
    analyzer = StockAnalyzer()
    analysis = analyzer.full_analysis(data)
    
    print("\n=== 分析结果 ===")
    print(f"当前价格: ${analysis['signals']['current_price']:.2f}")
    print(f"预测价格 ({analysis['prediction']['prediction_days']}天后): ${analysis['prediction']['predicted_price']:.2f}")
    print(f"预期变化: {analysis['prediction']['change_percent']:.2f}%")
    print(f"建议: {analysis['signals']['recommendation']}")
    print(f"\n信号详情:")
    for signal in analysis['signals']['signals']:
        print(f"  - {signal}")

