"""
数据可视化模块
"""
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import font_manager
import pandas as pd
import numpy as np
from indicators import TechnicalIndicators


# 设置中文字体（Windows）
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False


class StockVisualizer:
    """美股数据可视化类"""
    
    def __init__(self):
        self.indicators = TechnicalIndicators()
    
    def plot_candlestick(self, df, title='美股K线图', save_path=None):
        """
        绘制K线图
        
        参数:
            df: 包含OHLC数据的DataFrame
            title: 图表标题
            save_path: 保存路径（可选）
        """
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # 绘制K线
        for i in range(len(df)):
            row = df.iloc[i]
            color = 'red' if row['Close'] >= row['Open'] else 'green'
            
            # 绘制实体
            ax.bar(i, abs(row['Close'] - row['Open']), 
                   bottom=min(row['Open'], row['Close']),
                   color=color, alpha=0.8, width=0.6)
            
            # 绘制上下影线
            ax.plot([i, i], [row['Low'], row['High']], 
                   color=color, linewidth=1)
        
        ax.set_title(title, fontsize=16, fontweight='bold')
        ax.set_xlabel('日期', fontsize=12)
        ax.set_ylabel('价格', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        # 设置x轴标签
        if len(df) > 20:
            step = len(df) // 10
            ax.set_xticks(range(0, len(df), step))
            ax.set_xticklabels([df.index[i].strftime('%Y-%m-%d') 
                               for i in range(0, len(df), step)], 
                               rotation=45, ha='right')
        else:
            ax.set_xticks(range(len(df)))
            ax.set_xticklabels([d.strftime('%Y-%m-%d') for d in df.index], 
                               rotation=45, ha='right')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"图表已保存到: {save_path}")
        
        return fig
    
    def plot_price_with_indicators(self, df, symbol='', save_path=None):
        """
        绘制价格和技术指标综合图
        
        参数:
            df: 包含技术指标的DataFrame
            symbol: 股票代码
            save_path: 保存路径（可选）
        """
        data = self.indicators.add_all_indicators(df.copy())
        
        fig = plt.figure(figsize=(16, 12))
        gs = fig.add_gridspec(4, 1, hspace=0.3)
        
        # 1. 价格和均线
        ax1 = fig.add_subplot(gs[0, 0])
        ax1.plot(data.index, data['Close'], label='收盘价', linewidth=2, color='black')
        ax1.plot(data.index, data['MA_5'], label='MA5', linewidth=1, alpha=0.7)
        ax1.plot(data.index, data['MA_20'], label='MA20', linewidth=1, alpha=0.7)
        ax1.plot(data.index, data['MA_60'], label='MA60', linewidth=1, alpha=0.7)
        ax1.fill_between(data.index, data['BB_Upper'], data['BB_Lower'], 
                         alpha=0.2, label='布林带', color='gray')
        ax1.set_title(f'{symbol} 价格走势和技术指标', fontsize=14, fontweight='bold')
        ax1.set_ylabel('价格', fontsize=10)
        ax1.legend(loc='best', fontsize=8)
        ax1.grid(True, alpha=0.3)
        
        # 2. 成交量
        ax2 = fig.add_subplot(gs[1, 0])
        colors = ['red' if data['Close'].iloc[i] >= data['Open'].iloc[i] 
                 else 'green' for i in range(len(data))]
        ax2.bar(data.index, data['Volume'], color=colors, alpha=0.6)
        ax2.set_ylabel('成交量', fontsize=10)
        ax2.grid(True, alpha=0.3)
        
        # 3. RSI
        ax3 = fig.add_subplot(gs[2, 0])
        ax3.plot(data.index, data['RSI'], label='RSI', linewidth=1.5, color='purple')
        ax3.axhline(y=70, color='r', linestyle='--', alpha=0.5, label='超买线')
        ax3.axhline(y=30, color='g', linestyle='--', alpha=0.5, label='超卖线')
        ax3.fill_between(data.index, 30, 70, alpha=0.1, color='yellow')
        ax3.set_ylabel('RSI', fontsize=10)
        ax3.set_ylim(0, 100)
        ax3.legend(loc='best', fontsize=8)
        ax3.grid(True, alpha=0.3)
        
        # 4. MACD
        ax4 = fig.add_subplot(gs[3, 0])
        ax4.plot(data.index, data['MACD'], label='MACD', linewidth=1.5, color='blue')
        ax4.plot(data.index, data['MACD_Signal'], label='Signal', linewidth=1.5, color='red')
        ax4.bar(data.index, data['MACD_Hist'], label='Histogram', alpha=0.6, color='gray')
        ax4.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax4.set_ylabel('MACD', fontsize=10)
        ax4.set_xlabel('日期', fontsize=10)
        ax4.legend(loc='best', fontsize=8)
        ax4.grid(True, alpha=0.3)
        
        # 格式化x轴日期
        for ax in [ax1, ax2, ax3, ax4]:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            if len(data) > 30:
                ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
            else:
                ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(data)//10)))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"图表已保存到: {save_path}")
        
        return fig
    
    def plot_prediction(self, df, predicted_price, prediction_days=30, save_path=None):
        """
        绘制预测结果
        
        参数:
            df: 历史数据DataFrame
            predicted_price: 预测价格
            prediction_days: 预测天数
            save_path: 保存路径（可选）
        """
        fig, ax = plt.subplots(figsize=(14, 6))
        
        # 绘制历史价格
        historical_days = len(df)
        dates_historical = pd.date_range(
            end=df.index[-1], 
            periods=historical_days, 
            freq='D'
        )
        ax.plot(dates_historical, df['Close'].values, 
               label='历史价格', linewidth=2, color='blue')
        
        # 绘制预测
        future_dates = pd.date_range(
            start=df.index[-1] + pd.Timedelta(days=1),
            periods=prediction_days,
            freq='D'
        )
        current_price = df['Close'].iloc[-1]
        
        # 简单线性插值预测（实际应该用模型预测）
        price_change = predicted_price - current_price
        predicted_prices = np.linspace(
            current_price, 
            predicted_price, 
            prediction_days
        )
        
        ax.plot(future_dates, predicted_prices, 
               label=f'预测价格 ({prediction_days}天)', 
               linewidth=2, color='red', linestyle='--')
        ax.axhline(y=predicted_price, color='red', 
                  linestyle=':', alpha=0.5, label=f'目标价格: ${predicted_price:.2f}')
        
        ax.set_title('价格预测', fontsize=14, fontweight='bold')
        ax.set_xlabel('日期', fontsize=12)
        ax.set_ylabel('价格', fontsize=12)
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"图表已保存到: {save_path}")
        
        return fig
    
    def show_all(self, df, symbol='', analysis_result=None, save_dir=None):
        """
        显示所有图表
        
        参数:
            df: 股票数据DataFrame
            symbol: 股票代码
            analysis_result: 分析结果（可选）
            save_dir: 保存目录（可选）
        """
        import os
        
        if save_dir:
            os.makedirs(save_dir, exist_ok=True)
        
        # 价格和技术指标图
        fig1 = self.plot_price_with_indicators(
            df, symbol, 
            save_path=os.path.join(save_dir, f'{symbol}_indicators.png') if save_dir else None
        )
        
        # 如果有预测结果，绘制预测图
        if analysis_result and 'prediction' in analysis_result:
            pred = analysis_result['prediction']
            fig2 = self.plot_prediction(
                df, 
                pred['predicted_price'], 
                pred['prediction_days'],
                save_path=os.path.join(save_dir, f'{symbol}_prediction.png') if save_dir else None
            )
        
        plt.show()


if __name__ == '__main__':
    # 测试
    from data_fetcher import StockDataFetcher
    
    fetcher = StockDataFetcher()
    data = fetcher.get_stock_data('AAPL', period='6mo')
    
    visualizer = StockVisualizer()
    visualizer.plot_price_with_indicators(data, 'AAPL')

