#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置文件，包含项目所需的各种路径和参数设置
"""

import os
from datetime import datetime, timedelta
import random

# 路径配置
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGES_DIR = os.path.join(BASE_DIR, "images")
DOCS_DIR = os.path.join(BASE_DIR, "docs")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
DEBUG_MODE = False
# 文件配置
CAPA_CSV_FILE = os.path.join(DOCS_DIR, "capa.csv")  # CAPA CSV文件路径
INPUT_CSV_FILE = os.path.join(
    DOCS_DIR, "input.csv"
)  # 输入CSV文件路径，包含编号、位置和日期信息
OUTPUT_REPORT = os.path.join(
    OUTPUT_DIR, f'Daily_Report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.docx'
)

# 水印配置
WATERMARK_FONT = "Arial"  # 水印字体，如果不存在会使用默认字体
WATERMARK_FONT_SIZE = 30  # 增大字体大小
WATERMARK_TEXT_COLOR = (255, 255, 255, 255)  # 白色文字，完全不透明
WATERMARK_OUTLINE_COLOR = (0, 0, 0, 255)  # 黑色轮廓，完全不透明
WATERMARK_POSITION = "bottom_right"  # 水印位置：右下角
WATERMARK_PADDING = 15  # 水印与图片边缘的距离（像素）
WATERMARK_DATETIME_FORMAT = "%Y-%m-%d %I:%M %p"  # 添加AM/PM格式

# 图像处理配置
IMAGE_RESIZE_ENABLED = True  # 是否启用图像大小调整
IMAGE_MAX_WIDTH = 1200  # 图像最大宽度
IMAGE_MAX_HEIGHT = 800  # 图像最大高度
IMAGE_QUALITY = 90  # 图像质量（1-100）

# 报告配置
REPORT_TITLE = "Daily Report"
REPORT_AUTHOR = "System"

# AI配置
USE_AI = True  # 是否使用AI识别图片内容
AI_CONFIDENCE_THRESHOLD = 0.7  # AI识别的置信度阈值
AI_MAX_DESCRIPTIONS = 3  # 每张图片最多返回的描述数量

# 输入配置
USE_INPUT_CSV = True  # 是否使用input.csv文件中的数据


# 随机日期时间生成配置
def generate_random_datetime():
    """生成随机的过去日期时间（在当前日期之前）"""
    # 生成1到30天之间的随机天数
    days_ago = random.randint(1, 30)
    # 生成随机的小时和分钟
    random_hour = random.randint(8, 17)  # 工作时间 8:00 - 17:59
    random_minute = random.randint(0, 59)

    # 计算随机日期时间
    random_date = datetime.now() - timedelta(days=days_ago)
    random_datetime = random_date.replace(
        hour=random_hour, minute=random_minute, second=0, microsecond=0
    )

    return random_datetime


# 确保输出目录存在
os.makedirs(OUTPUT_DIR, exist_ok=True)
