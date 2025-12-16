"""
AI美股分析软件 - 主程序
专注于美股市场的股票分析
"""
import argparse
from data_fetcher import StockDataFetcher
from ai_analyzer import StockAnalyzer
from visualizer import StockVisualizer
from config import DEFAULT_STOCKS


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='AI美股分析软件')
    parser.add_argument('--symbol', '-s', type=str, 
                       help='美股代码（如: AAPL, MSFT, TSLA）', 
                       default='AAPL')
    parser.add_argument('--period', '-p', type=str, 
                       help='时间周期（1mo, 3mo, 6mo, 1y等）', 
                       default='1mo')
    parser.add_argument('--no-train', action='store_true',
                       help='跳过模型训练，仅进行信号分析')
    parser.add_argument('--no-plot', action='store_true',
                       help='不显示图表')
    parser.add_argument('--save', type=str,
                       help='保存图表到指定目录')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("AI美股分析软件")
    print("=" * 60)
    
    # 初始化组件
    fetcher = StockDataFetcher()
    analyzer = StockAnalyzer()
    visualizer = StockVisualizer()
    
    # 获取股票数据
    print(f"\n正在获取股票数据: {args.symbol}")
    data = fetcher.get_stock_data(args.symbol, period=args.period)
    
    if data.empty:
        print(f"错误: 无法获取股票 {args.symbol} 的数据")
        print("提示: 请检查美股代码是否正确")
        print("示例: AAPL (苹果), MSFT (微软), TSLA (特斯拉), GOOGL (谷歌)")
        return
    
    print(f"成功获取 {len(data)} 条数据")
    print(f"数据时间范围: {data.index[0].strftime('%Y-%m-%d')} 至 {data.index[-1].strftime('%Y-%m-%d')}")
    print(f"最新收盘价: ${data['Close'].iloc[-1]:.2f}")
    
    # 获取股票信息
    info = fetcher.get_stock_info(args.symbol)
    if info:
        print(f"\n股票信息:")
        print(f"  名称: {info.get('name', 'N/A')}")
        print(f"  行业: {info.get('industry', 'N/A')}")
        print(f"  市值: ${info.get('market_cap', 0):,.0f}" if info.get('market_cap') else "  市值: N/A")
        print(f"  市盈率: {info.get('pe_ratio', 0):.2f}" if info.get('pe_ratio') else "  市盈率: N/A")
    
    # AI分析
    if args.no_train:
        print("\n=== 技术信号分析 ===")
        signals = analyzer.analyze_signals(data)
        analysis_result = {'signals': signals}
    else:
        print("\n=== AI分析 ===")
        try:
            analysis_result = analyzer.full_analysis(data)
        except Exception as e:
            print(f"模型训练失败: {e}")
            print("改用技术信号分析...")
            signals = analyzer.analyze_signals(data)
            analysis_result = {'signals': signals}
    
    # 显示分析结果
    print("\n" + "=" * 60)
    print("分析结果")
    print("=" * 60)
    
    if 'signals' in analysis_result:
        signals = analysis_result['signals']
        print(f"\n当前价格: ${signals['current_price']:.2f}")
        print(f"RSI: {signals['rsi']:.2f}")
        print(f"MACD: {signals['macd']:.4f}")
        print(f"\n投资建议: {signals['recommendation']}")
        print(f"信号强度: {signals['signal_strength']}")
        print(f"\n技术信号:")
        for signal in signals['signals']:
            print(f"  • {signal}")
    
    if 'prediction' in analysis_result:
        pred = analysis_result['prediction']
        print(f"\n价格预测:")
        print(f"  当前价格: ${pred['current_price']:.2f}")
        print(f"  预测价格 ({pred['prediction_days']}天后): ${pred['predicted_price']:.2f}")
        print(f"  预期变化: {pred['change_percent']:+.2f}%")
        print(f"  趋势: {pred['trend']}")
    
    if 'model_performance' in analysis_result:
        perf = analysis_result['model_performance']
        print(f"\n模型性能:")
        print(f"  RMSE: {perf['rmse']:.2f}")
        print(f"  MAE: {perf['mae']:.2f}")
        print(f"  方向预测准确率: {perf['direction_accuracy']:.2f}%")
    
    # 显示图表
    if not args.no_plot:
        print("\n正在生成图表...")
        visualizer.show_all(data, args.symbol, analysis_result, args.save)
    
    print("\n" + "=" * 60)
    print("分析完成！")
    print("=" * 60)
    print("\n免责声明: 本软件仅供学习和研究使用，不构成投资建议。")
    print("股票投资有风险，请谨慎决策。")


if __name__ == '__main__':
    main()

