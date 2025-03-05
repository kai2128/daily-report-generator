#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
启动脚本，方便用户运行程序
"""

import os
import sys
from src import main

if __name__ == "__main__":
    # 确保当前目录在系统路径中
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    # 运行主程序
    main.main()
