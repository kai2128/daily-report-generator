# 日报生成器

一个用于生成日常检查报告的Python工具，支持图像处理和AI图像识别功能。

## 功能特点

- **自动生成报告**：根据图片和描述自动生成日常检查报告
- **图像处理**：自动添加水印、调整图像大小、统一图像对尺寸
- **AI图像识别**：使用AI识别图像内容，自动分类为"之前"和"之后"的图片
- **手动模式**：支持通过文件命名规则手动指定"之前"和"之后"图片以及描述
- **备选方案**：当高级AI功能不可用时，自动切换到基于图像特征的简化分析
- **数据源**：从CAPA CSV文件中读取描述和纠正措施
- **命令行界面**：支持通过命令行参数自定义报告生成过程

## 安装

1. 克隆仓库：

```bash
git clone https://github.com/yourusername/daily-report-generator.git
cd daily-report-generator
```

2. 安装依赖：

```bash
pip install -r requirements.txt
```

## 使用方法

### 基本用法

1. 将CAPA CSV文件放在`docs`文件夹中（默认名称为`capa.csv`）
2. 将需要处理的图片放在`images`文件夹中
3. 运行主程序：

```bash
python src/main.py
```

### 手动模式

手动模式允许您通过特定的文件命名规则来指定"之前"和"之后"的图片，以及要使用的CAPA描述：

1. 创建`images/before`和`images/after`目录
2. 在`before`目录中放置"之前"图片，命名格式为：`<pairing_id>_<optional_capa_index>.jpg`
   - `pairing_id`：图片对的唯一标识符（数字）
   - `capa_index`：（可选）CAPA CSV文件中的No列值，用于选择特定的描述
3. 在`after`目录中放置"之后"图片，命名格式为：`<pairing_id>.jpg`
4. 使用`--manual-mode`参数运行程序：

```bash
python src/main.py --manual-mode
```

示例：
- `images/before/1_12.jpg`：第1对图片的"之前"图片，使用CAPA No.12的描述
- `images/after/1.jpg`：第1对图片的"之后"图片
- `images/before/2.jpg`：第2对图片的"之前"图片，随机选择描述
- `images/after/2.jpg`：第2对图片的"之后"图片

### 图像处理功能

系统会自动处理图像，包括：

1. **添加水印**：在图像右下角添加日期时间水印
2. **调整图像大小**：如果图像超过最大尺寸限制，会自动缩小
3. **统一图像对尺寸**：确保每对"之前"和"之后"的图像具有相同的尺寸

这些图像处理参数可以在`config.py`中配置：

```python
# 图像处理配置
IMAGE_RESIZE_ENABLED = True  # 是否启用图像大小调整
IMAGE_MAX_WIDTH = 1200  # 图像最大宽度
IMAGE_MAX_HEIGHT = 800  # 图像最大高度
IMAGE_QUALITY = 90  # 图像质量（1-100）
```

### 命令行参数

可以使用以下命令行参数自定义报告生成过程：

- `--output`：指定输出文件夹路径
- `--images`：指定图片文件夹路径
- `--capa`：指定CAPA CSV文件路径
- `--watermark`：指定水印文本
- `--no-watermark`：不添加水印
- `--ai`：启用AI图像识别功能
- `--no-ai`：禁用AI图像识别功能
- `--manual-mode`：使用手动模式（从images/before和images/after目录获取图像对）

示例：

```bash
# 使用自定义路径
python src/main.py --output ./output --images ./my_images --capa ./my_data/capa.csv

# 不添加水印
python src/main.py --no-watermark

# 使用自定义水印
python src/main.py --watermark "我的公司名称"

# 启用AI图像识别
python src/main.py --ai

# 禁用AI图像识别
python src/main.py --no-ai

# 使用手动模式
python src/main.py --manual-mode

# 组合使用
python src/main.py --manual-mode --no-ai
```

### AI图像识别功能

系统使用CLIP Interrogator模型来识别图像内容，并自动将图片分类为"之前"和"之后"。

测试AI图像识别功能：

```bash
python src/test_ai.py --image1 ./images/image1.jpg --image2 ./images/image2.jpg
```

#### 备选方案

当高级AI功能不可用时，系统会自动切换到基于图像特征的简化分析：

1. **基于亮度分析**：亮度高的图片可能是"之后"图片，亮度低的图片可能是"之前"图片
2. **基于对比度分析**：对比度高的图片通常包含更多细节
3. **关键词匹配**：使用简单的关键词匹配来选择最相关的描述

### 测试CAPA CSV功能

测试从CAPA CSV文件读取数据：

```bash
python src/test_capa.py
```

## 项目结构

```
daily-report-generator/
├── src/                  # 源代码
│   ├── main.py           # 主程序
│   ├── config.py         # 配置文件
│   ├── data_processor.py # 数据处理模块
│   ├── image_processor.py # 图像处理模块
│   ├── report_generator.py # 报告生成模块
│   ├── ai_processor.py   # AI处理模块
│   ├── test_ai.py        # AI测试脚本
│   └── test_capa.py      # CAPA CSV测试脚本
├── images/               # 图片文件夹
│   ├── before/           # 手动模式下的"之前"图片
│   └── after/            # 手动模式下的"之后"图片
├── docs/                 # 包含CAPA CSV文件
├── output/               # 输出文件夹
├── requirements.txt      # 依赖列表
└── README.md             # 说明文档
```

## 工作流程

1. 从CAPA CSV文件中读取描述和纠正措施
2. 处理`images`文件夹中的图片（或手动模式下的`images/before`和`images/after`目录）
3. 如果启用AI功能，使用AI识别图片内容并分类为"之前"和"之后"
4. 如果使用手动模式，根据文件名中的CAPA索引选择描述
5. 为每对图片添加水印和时间戳
6. 调整图片大小，确保每对图片具有相同的尺寸
7. 生成包含图片和描述的报告
8. 将报告保存到`output`文件夹中

## 注意事项

- CAPA CSV文件应包含"No"、"Before"和"CAPA"列，分别对应编号、描述和纠正措施
- 图片应为JPG或PNG格式
- 在手动模式下，确保`before`和`after`目录中的图片按照正确的命名规则命名
- 为获得最佳AI识别效果，图片应清晰且内容相关
- 如果AI功能不可用，系统会自动切换到基于图像特征的简化分析

## 依赖

- Python 3.8+
- Pillow
- pandas
- torch
- transformers
- open-clip-torch
- nltk

## 许可证

MIT 