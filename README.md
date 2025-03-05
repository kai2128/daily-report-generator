# 日报表生成器

这是一个用于生成日报表的Python项目。它可以处理图片，添加日期时间水印，并从Excel文件中获取描述和纠正措施，最终生成Word文档格式的报告。

## 功能特点

- 处理图片并在右下角添加日期时间水印（透明背景，黑色轮廓白色文字）
- 水印使用大号字体和AM/PM时间格式，确保清晰可见
- **AI图像识别**：自动识别图片内容，判断哪个是"之前"图片，哪个是"之后"图片
- **智能匹配**：根据图片内容自动选择最匹配的描述和纠正措施
- **备选方案**：当高级AI功能不可用时，自动切换到基于图像特征的简化分析
- 从Excel文件中读取描述和纠正措施
- 将图片和描述组织成表格格式
- 生成Word文档格式的报告
- model saved at `~/.cache/huggingface`

## 项目结构

```
daily-report-generator/
├── src/                    # 源代码
│   ├── image_processor.py  # 图片处理模块
│   ├── data_processor.py   # Excel数据处理模块
│   ├── report_generator.py # 报告生成模块
│   ├── ai_processor.py     # AI图像识别模块
│   ├── config.py           # 配置文件
│   ├── test_watermark.py   # 水印测试脚本
│   ├── test_ai.py          # AI测试脚本
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
- `--use-ai`: 使用AI识别图片内容（默认开启）
- `--no-ai`: 不使用AI识别图片内容

示例：

```bash
# 使用AI识别图片内容（默认）
python src/main.py --images /path/to/images --excel /path/to/excel.xlsx

# 不使用AI识别图片内容
python src/main.py --no-ai
```

### 测试水印功能

可以使用测试脚本单独测试水印功能：

```bash
python src/test_watermark.py --image /path/to/image.jpg
```

参数说明：
- `--image`: 要添加水印的图片路径（必需）
- `--output`: 输出图片路径（可选，默认在原图片名前添加watermarked_前缀）
- `--datetime`: 要添加的日期时间，格式为YYYY-MM-DD HH:MM AM/PM（可选，默认使用当前时间）
- `--font-size`: 水印字体大小（可选，默认为30）

示例：

```bash
# 使用默认设置添加水印
python src/test_watermark.py --image images/example.jpg

# 自定义日期时间和字体大小
python src/test_watermark.py --image images/example.jpg --datetime "2023-05-15 02:30 PM" --font-size 40
```

### 测试AI功能

可以使用测试脚本单独测试AI图像识别功能：

```bash
python src/test_ai.py --image1 /path/to/image1.jpg --image2 /path/to/image2.jpg
```

参数说明：
- `--image1`: 第一张图片路径（必需）
- `--image2`: 第二张图片路径（必需）
- `--excel`: Excel文件路径（可选，默认为配置中的路径）

## AI图像识别功能

本项目使用CLIP Interrogator和自然语言处理技术来识别图片内容并自动选择最匹配的描述：

1. **图片内容识别**：使用CLIP模型识别图片中的内容和场景
2. **图片分类**：自动判断哪个是"之前"图片，哪个是"之后"图片
3. **描述匹配**：根据图片内容自动从Excel文件中选择最匹配的描述和纠正措施

AI功能可以大大提高报告生成的自动化程度和准确性，减少手动选择的工作量。

### 备选方案

如果高级AI功能（CLIP Interrogator）不可用，系统会自动切换到基于图像特征的简化分析：

1. **基于亮度分析**：亮度高的图片通常是"之后"的图片，亮度低的图片通常是"之前"的图片
2. **基于对比度分析**：对比度高的图片通常有更多细节
3. **关键词匹配**：使用简单的关键词匹配来选择最匹配的描述

这种备选方案确保即使在高级AI功能不可用的情况下，系统仍然可以正常工作。

## 水印特性

- 透明背景，不会遮挡图片内容
- 黑色轮廓白色文字，确保在任何背景下都清晰可见
- 大号字体（默认30点）和AM/PM时间格式
- 位于图片右下角，带有适当的内边距
- 可以自定义字体大小、颜色和位置（通过修改config.py）

## 工作流程

1. 程序读取`images`文件夹中的所有图片
2. 程序读取Excel文件中的描述和纠正措施数据
3. 对于每对图片：
   - 使用AI识别图片内容并判断哪个是"之前"图片，哪个是"之后"图片
   - 根据图片内容自动选择最匹配的描述和纠正措施
   - 生成随机日期时间
   - 添加水印
   - 将这对图片及其描述添加到报告中
4. 生成最终的Word文档报告
5. 保存报告到`output`文件夹

## 依赖包

- Pillow (PIL) - 用于图片处理和添加水印
- pandas - 用于读取和处理Excel数据
- openpyxl - 用于支持pandas读取Excel文件
- python-docx - 用于生成Word文档
- torch - 用于AI模型
- transformers - 用于加载和使用CLIP模型
- open-clip-torch - 用于CLIP Interrogator
- nltk - 用于自然语言处理

## 注意事项

- 图片文件夹中的图片数量应该是偶数，以便配对处理
- Excel文件中的第一列应该是描述，第二列应该是纠正措施
- 首次运行时，程序会下载AI模型，可能需要一些时间
- AI功能需要较多的计算资源，如果遇到性能问题，可以使用`--no-ai`参数禁用AI功能
- 如果高级AI功能不可用，系统会自动切换到基于图像特征的简化分析 