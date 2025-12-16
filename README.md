# AI美股分析软件

一个专注于美股的AI股票分析工具，提供股票数据获取、技术分析、趋势预测和可视化功能。

## 功能特性

- 📊 实时股票数据获取
- 🤖 AI驱动的技术分析和趋势预测
- 📈 多种技术指标计算（MA、RSI、MACD等）
- 📉 数据可视化（K线图、指标图表）
- 💡 智能买卖信号提示

## 技术栈

- Python 3.8+
- yfinance - 股票数据获取
- pandas - 数据处理
- numpy - 数值计算
- matplotlib/plotly - 数据可视化
- scikit-learn - 机器学习模型
- tensorflow/pytorch - 深度学习（可选）

## 安装

```bash
pip install -r requirements.txt
```

## 使用方法

### Web界面（推荐）

启动Web服务器：
```bash
python app.py
```

然后在浏览器中访问：`http://localhost:5000`

Web界面功能：
- 🎯 直观的图形界面
- 📊 实时股票数据展示
- 🔮 未来一个月（30天）走势预测
- 📈 交互式图表可视化
- 💡 智能买卖信号提示

### 命令行界面

```bash
# 分析苹果股票（默认使用1个月数据，预测未来30天）
python main.py --symbol AAPL

# 分析特斯拉股票
python main.py --symbol TSLA

# 自定义时间周期
python main.py --symbol MSFT --period 6mo
```

## 支持的股票代码

本软件专注于美股市场，支持所有在NYSE、NASDAQ等交易所上市的股票代码，例如：
- AAPL (苹果)
- MSFT (微软)
- GOOGL (谷歌)
- TSLA (特斯拉)
- AMZN (亚马逊)
- META (Meta/Facebook)
- NVDA (英伟达)

## 项目结构

```
.
├── app.py                 # Web应用入口（Flask）
├── main.py                # 命令行程序入口
├── data_fetcher.py        # 股票数据获取模块
├── ai_analyzer.py         # AI分析模块
├── indicators.py          # 技术指标计算
├── visualizer.py          # 数据可视化
├── config.py              # 配置文件
├── templates/             # HTML模板目录
│   └── index.html        # Web界面模板
├── requirements.txt       # 依赖包
└── README.md              # 项目说明
```

## 示例

```python
from data_fetcher import StockDataFetcher
from ai_analyzer import StockAnalyzer

# 获取美股数据
fetcher = StockDataFetcher()
data = fetcher.get_stock_data('AAPL', period='1y')  # 苹果股票

# AI分析
analyzer = StockAnalyzer()
analysis = analyzer.full_analysis(data)
print(analysis)
```

## 功能说明

- **数据周期**: 默认获取最近1个月的历史数据
- **预测周期**: 预测未来30天（一个月）的股票走势
- **AI模型**: 使用随机森林算法进行价格预测
- **技术指标**: 包含MA、RSI、MACD、布林带等多种技术指标

## 注意事项

- 本软件仅供学习和研究使用，不构成投资建议
- 股票投资有风险，请谨慎决策
- 数据来源依赖于第三方API，请遵守相关使用条款
- 预测结果仅供参考，实际投资请结合多方面因素

