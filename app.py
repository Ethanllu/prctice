"""
AI美股分析软件 - Web应用
Flask Web界面
"""
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import json
from data_fetcher import StockDataFetcher
from ai_analyzer import StockAnalyzer
from visualizer import StockVisualizer
from config import DEFAULT_PERIOD, PREDICTION_DAYS
import base64
import io
from matplotlib.figure import Figure

app = Flask(__name__)
CORS(app)

# 初始化组件
fetcher = StockDataFetcher()
analyzer = StockAnalyzer()
visualizer = StockVisualizer()


@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


@app.route('/api/analyze', methods=['POST'])
def analyze_stock():
    """分析股票API"""
    try:
        data = request.get_json()
        symbol = data.get('symbol', 'AAPL').upper()
        period = data.get('period', DEFAULT_PERIOD)
        use_ai = data.get('use_ai', True)
        
        # 获取股票数据
        stock_data = fetcher.get_stock_data(symbol, period=period)
        
        if stock_data.empty:
            return jsonify({
                'success': False,
                'error': f'无法获取股票 {symbol} 的数据，请检查股票代码是否正确'
            }), 400
        
        # 获取股票信息
        stock_info = fetcher.get_stock_info(symbol)
        
        # 执行分析
        if use_ai:
            try:
                analysis_result = analyzer.full_analysis(stock_data)
            except Exception as e:
                # 如果AI分析失败，改用技术信号分析
                signals = analyzer.analyze_signals(stock_data)
                analysis_result = {'signals': signals}
        else:
            signals = analyzer.analyze_signals(stock_data)
            analysis_result = {'signals': signals}
        
        # 准备返回数据
        result = {
            'success': True,
            'symbol': symbol,
            'stock_info': stock_info,
            'data_summary': {
                'data_points': len(stock_data),
                'date_range': {
                    'start': stock_data.index[0].strftime('%Y-%m-%d'),
                    'end': stock_data.index[-1].strftime('%Y-%m-%d')
                },
                'current_price': float(stock_data['Close'].iloc[-1]),
                'price_change': float(stock_data['Close'].iloc[-1] - stock_data['Close'].iloc[0]),
                'price_change_percent': float((stock_data['Close'].iloc[-1] / stock_data['Close'].iloc[0] - 1) * 100)
            }
        }
        
        # 添加信号分析结果
        if 'signals' in analysis_result:
            signals = analysis_result['signals']
            result['signals'] = {
                'recommendation': signals['recommendation'],
                'signal_strength': signals['signal_strength'],
                'signals_list': signals['signals'],
                'current_price': float(signals['current_price']),
                'rsi': float(signals['rsi']),
                'macd': float(signals['macd']),
                'macd_signal': float(signals['macd_signal'])
            }
        
        # 添加预测结果
        if 'prediction' in analysis_result:
            pred = analysis_result['prediction']
            result['prediction'] = {
                'current_price': float(pred['current_price']),
                'predicted_price': float(pred['predicted_price']),
                'prediction_days': pred['prediction_days'],
                'change_percent': float(pred['change_percent']),
                'trend': pred['trend']
            }
        
        # 添加模型性能
        if 'model_performance' in analysis_result:
            perf = analysis_result['model_performance']
            result['model_performance'] = {
                'rmse': float(perf['rmse']),
                'mae': float(perf['mae']),
                'direction_accuracy': float(perf['direction_accuracy'])
            }
        
        # 生成图表（转换为base64）
        try:
            chart_data = generate_chart_data(stock_data, symbol, analysis_result)
            result['charts'] = chart_data
        except Exception as e:
            print(f"生成图表时出错: {e}")
            result['charts'] = None
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def generate_chart_data(df, symbol, analysis_result):
    """生成图表数据（返回base64编码的图片）"""
    charts = {}
    
    try:
        # 价格走势图
        fig = Figure(figsize=(12, 6))
        ax = fig.add_subplot(111)
        ax.plot(df.index, df['Close'], linewidth=2, color='#2563eb', label='收盘价')
        ax.set_title(f'{symbol} 价格走势', fontsize=14, fontweight='bold')
        ax.set_xlabel('日期', fontsize=10)
        ax.set_ylabel('价格 ($)', fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.legend()
        fig.tight_layout()
        
        # 转换为base64
        img_buffer = io.BytesIO()
        fig.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight')
        img_buffer.seek(0)
        charts['price_chart'] = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
        
        # 如果有预测，添加预测图
        if 'prediction' in analysis_result:
            pred = analysis_result['prediction']
            fig2 = Figure(figsize=(12, 6))
            ax2 = fig2.add_subplot(111)
            
            # 历史价格
            ax2.plot(df.index, df['Close'], linewidth=2, color='#2563eb', label='历史价格')
            
            # 预测价格（简单线性预测）
            import pandas as pd
            import numpy as np
            from datetime import timedelta
            
            current_price = df['Close'].iloc[-1]
            predicted_price = pred['predicted_price']
            prediction_days = pred['prediction_days']
            
            future_dates = pd.date_range(
                start=df.index[-1] + timedelta(days=1),
                periods=prediction_days,
                freq='D'
            )
            
            predicted_prices = np.linspace(current_price, predicted_price, prediction_days)
            ax2.plot(future_dates, predicted_prices, 
                    linewidth=2, color='#ef4444', linestyle='--', 
                    label=f'预测价格 ({prediction_days}天)')
            ax2.axhline(y=predicted_price, color='#ef4444', 
                       linestyle=':', alpha=0.5, label=f'目标: ${predicted_price:.2f}')
            
            ax2.set_title(f'{symbol} 价格预测（未来{prediction_days}天）', fontsize=14, fontweight='bold')
            ax2.set_xlabel('日期', fontsize=10)
            ax2.set_ylabel('价格 ($)', fontsize=10)
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            fig2.tight_layout()
            
            img_buffer2 = io.BytesIO()
            fig2.savefig(img_buffer2, format='png', dpi=100, bbox_inches='tight')
            img_buffer2.seek(0)
            charts['prediction_chart'] = base64.b64encode(img_buffer2.getvalue()).decode('utf-8')
        
    except Exception as e:
        print(f"生成图表错误: {e}")
    
    return charts


@app.route('/api/popular-stocks', methods=['GET'])
def get_popular_stocks():
    """获取热门股票列表"""
    popular_stocks = [
        {'symbol': 'AAPL', 'name': '苹果'},
        {'symbol': 'MSFT', 'name': '微软'},
        {'symbol': 'GOOGL', 'name': '谷歌'},
        {'symbol': 'TSLA', 'name': '特斯拉'},
        {'symbol': 'AMZN', 'name': '亚马逊'},
        {'symbol': 'META', 'name': 'Meta'},
        {'symbol': 'NVDA', 'name': '英伟达'},
        {'symbol': 'JPM', 'name': '摩根大通'},
        {'symbol': 'V', 'name': 'Visa'},
        {'symbol': 'JNJ', 'name': '强生'}
    ]
    return jsonify(popular_stocks)


if __name__ == '__main__':
    print("=" * 60)
    print("AI美股分析软件 - Web版")
    print("=" * 60)
    print(f"访问地址: http://localhost:5000")
    print(f"默认数据周期: {DEFAULT_PERIOD}")
    print(f"预测天数: {PREDICTION_DAYS}天（一个月）")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)

