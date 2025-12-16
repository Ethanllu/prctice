"""
配置文件
"""
import os

# 数据存储路径
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(DATA_DIR, exist_ok=True)

# 默认美股代码（示例）
DEFAULT_STOCKS = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'AMZN']

# 数据获取参数
DEFAULT_PERIOD = '1y'  # 1年数据
DEFAULT_INTERVAL = '1d'  # 日线数据

# AI模型参数
PREDICTION_DAYS = 30  # 预测未来30天
TRAIN_TEST_SPLIT = 0.8  # 训练集比例

# 技术指标参数
MA_SHORT = 5   # 短期均线
MA_MID = 20    # 中期均线
MA_LONG = 60   # 长期均线
RSI_PERIOD = 14  # RSI周期

