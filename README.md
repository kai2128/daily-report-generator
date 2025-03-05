# 日报表生成器

这是一个用于生成日报表的Python项目。它可以处理图片，添加日期时间水印，并从Excel文件中获取描述和纠正措施，最终生成Word文档格式的报告。

## 功能特点

- 处理图片并在右下角添加日期时间水印（透明背景，黑色轮廓白色文字）
- 从Excel文件中读取描述和纠正措施
- 将图片和描述组织成表格格式
- 生成Word文档格式的报告

## 项目结构

```
daily-report-generator/
├── src/                    # 源代码
│   ├── image_processor.py  # 图片处理模块
│   ├── data_processor.py   # Excel数据处理模块
│   ├── report_generator.py # 报告生成模块
│   ├── config.py           # 配置文件
│   ├── test_watermark.py   # 水印测试脚本
│   └── main.py             # 主程序
├── docs/                   # 存放Excel文件
├── images/                 # 存放原始图片
├── output/                 # 存放生成的报告
├── requirements.txt        # 依赖包列表
└── README.md               # 项目说明
```

## 安装

1. 克隆或下载本项目
2. 安装依赖包：

```bash
pip install -r requirements.txt
```

## 使用方法

1. 将需要处理的图片放入`images`文件夹
2. 将包含描述和纠正措施的Excel文件放入`docs`文件夹
3. 运行主程序：

```bash
python run.py
```

或者：

```bash
python src/main.py
```

### 命令行参数

- `--images`: 图片文件夹路径（默认为`images`）
- `--excel`: Excel文件路径（默认为`docs/Daily inspection Summary.xlsx`）
- `--output`: 输出文件夹路径（默认为`output`）

示例：

```bash
python src/main.py --images /path/to/images --excel /path/to/excel.xlsx --output /path/to/output
```

### 测试水印功能

可以使用测试脚本单独测试水印功能：

```bash
python src/test_watermark.py --image /path/to/image.jpg
```

参数说明：
- `--image`: 要添加水印的图片路径（必需）
- `--output`: 输出图片路径（可选，默认在原图片名前添加watermarked_前缀）
- `--datetime`: 要添加的日期时间，格式为YYYY-MM-DD HH:MM（可选，默认使用当前时间）

## 水印特性

- 透明背景，不会遮挡图片内容
- 黑色轮廓白色文字，确保在任何背景下都清晰可见
- 位于图片右下角，带有适当的内边距
- 可以自定义字体大小、颜色和位置（通过修改config.py）

## 工作流程

1. 程序读取`images`文件夹中的所有图片
2. 程序读取Excel文件中的描述和纠正措施数据
3. 对于每张原始图片：
   - 生成随机日期时间
   - 添加水印
   - 选择一张纠正后的图片并添加相同的水印
   - 从Excel中选择描述和纠正措施
   - 将这对图片及其描述添加到报告中
4. 生成最终的Word文档报告
5. 保存报告到`output`文件夹

## 依赖包

- Pillow (PIL) - 用于图片处理和添加水印
- pandas - 用于读取和处理Excel数据
- openpyxl - 用于支持pandas读取Excel文件
- python-docx - 用于生成Word文档

## 注意事项

- 图片文件夹中的图片数量应该是偶数，以便配对处理
- Excel文件中的第一列应该是描述，第二列应该是纠正措施
- 如果描述和纠正措施的数量少于图片对的数量，则会循环使用 