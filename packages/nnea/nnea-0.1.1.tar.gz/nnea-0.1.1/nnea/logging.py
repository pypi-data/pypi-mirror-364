import logging
import coloredlogs  # 需安装：pip install coloredlogs

# 创建Logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# 配置彩色日志
coloredlogs.install(
    level='DEBUG',  # 日志级别
    logger=logger,
    fmt='%(asctime)s [%(levelname)s] %(message)s',  # 自定义格式
    datefmt='%H:%M:%S',
    field_styles={
        'levelname': {'color': 'white', 'bold': True},  # 级别名称样式
        'asctime': {'color': 'cyan'}
    },
    level_styles={
        'debug': {'color': 'blue'},
        'info': {'color': 'green'},
        'warning': {'color': 'yellow'},
        'error': {'color': 'red'},
        'critical': {'color': 'red', 'bold': True}  # 加粗红色
    }
)
