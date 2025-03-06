#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
图像处理模块，用于处理图像和添加水印
"""

import os
import re
import random
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageColor
import config


def add_watermark(image_path, datetime_str=None, output_path=None):
    """
    为图像添加水印

    Args:
        image_path (str): 图像路径
        datetime_str (str, optional): 日期时间字符串，如果为None则使用当前时间
        output_path (str, optional): 输出路径，如果为None则在原图像名前添加watermarked_前缀

    Returns:
        str: 添加水印后的图像路径
    """
    try:
        # 打开图像
        image = Image.open(image_path)

        # 如果没有指定日期时间，则使用当前时间
        if datetime_str is None:
            now = datetime.now()
            datetime_str = now.strftime("%Y-%m-%d %I:%M %p")

        # 创建绘图对象
        draw = ImageDraw.Draw(image)

        # 加载字体
        try:
            font = ImageFont.truetype(config.WATERMARK_FONT, config.WATERMARK_FONT_SIZE)
        except IOError:
            # 如果无法加载指定字体，则使用默认字体
            font = ImageFont.load_default()

        # 计算水印文本的大小 - 兼容不同版本的Pillow
        try:
            # 对于Pillow 9.2.0及以上版本
            text_bbox = font.getbbox(datetime_str)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
        except AttributeError:
            try:
                # 对于Pillow 8.x版本
                text_width, text_height = font.getsize(datetime_str)
            except AttributeError:
                # 对于更旧版本的Pillow
                text_width, text_height = draw.textsize(datetime_str, font=font)

        # 计算水印位置（右下角，带内边距）
        position = (
            image.width - text_width - config.WATERMARK_PADDING,
            image.height - text_height - config.WATERMARK_PADDING,
        )

        # 添加水印（黑色轮廓白色文字）
        # 先绘制黑色轮廓
        for offset_x, offset_y in [
            (-1, -1),
            (-1, 0),
            (-1, 1),
            (0, -1),
            (0, 1),
            (1, -1),
            (1, 0),
            (1, 1),
        ]:
            draw.text(
                (position[0] + offset_x, position[1] + offset_y),
                datetime_str,
                font=font,
                fill=config.WATERMARK_OUTLINE_COLOR,
            )

        # 再绘制白色文字
        draw.text(position, datetime_str, font=font, fill=config.WATERMARK_TEXT_COLOR)

        # 如果没有指定输出路径，则在原图像名前添加watermarked_前缀
        if output_path is None:
            dir_name = os.path.dirname(image_path)
            file_name = os.path.basename(image_path)
            output_path = os.path.join(dir_name, f"watermarked_{file_name}")

        # 保存图像
        image.save(output_path)

        return output_path

    except Exception as e:
        print(f"添加水印时出错: {e}")
        return None


def process_image_pair(image1_path, image2_path, datetime_obj=None):
    """
    处理图像对，添加水印并调整为相同大小

    Args:
        image1_path (str): 第一张图像路径
        image2_path (str): 第二张图像路径
        datetime_obj (datetime, optional): 日期时间对象，如果为None则使用随机生成的日期时间

    Returns:
        tuple: (processed_image1_path, processed_image2_path, datetime_str)
    """
    try:
        # 如果没有指定日期时间，则使用随机生成的日期时间
        if datetime_obj is None:
            datetime_obj = config.generate_random_datetime()

        # 格式化日期时间
        datetime_str = datetime_obj.strftime(config.WATERMARK_DATETIME_FORMAT)

        # 为图像添加水印
        processed_image1 = add_watermark(image1_path, datetime_str)
        processed_image2 = add_watermark(image2_path, datetime_str)

        if processed_image1 is None or processed_image2 is None:
            return (None, None, None)

        # 如果启用了图像大小调整，则调整图像大小
        if config.IMAGE_RESIZE_ENABLED:
            # 获取两张图像的尺寸
            try:
                img1 = Image.open(processed_image1)
                img2 = Image.open(processed_image2)

                width1, height1 = img1.size
                width2, height2 = img2.size

                # 首先检查是否超过最大尺寸限制
                if width1 > config.IMAGE_MAX_WIDTH or height1 > config.IMAGE_MAX_HEIGHT:
                    print(f"图像1超过最大尺寸限制，调整大小")
                    # 计算缩放比例
                    ratio1 = min(
                        config.IMAGE_MAX_WIDTH / width1,
                        config.IMAGE_MAX_HEIGHT / height1,
                    )
                    new_width1 = int(width1 * ratio1)
                    new_height1 = int(height1 * ratio1)
                    processed_image1 = resize_image(
                        processed_image1, new_width1, new_height1
                    )
                    # 更新尺寸
                    width1, height1 = new_width1, new_height1

                if width2 > config.IMAGE_MAX_WIDTH or height2 > config.IMAGE_MAX_HEIGHT:
                    print(f"图像2超过最大尺寸限制，调整大小")
                    # 计算缩放比例
                    ratio2 = min(
                        config.IMAGE_MAX_WIDTH / width2,
                        config.IMAGE_MAX_HEIGHT / height2,
                    )
                    new_width2 = int(width2 * ratio2)
                    new_height2 = int(height2 * ratio2)
                    processed_image2 = resize_image(
                        processed_image2, new_width2, new_height2
                    )
                    # 更新尺寸
                    width2, height2 = new_width2, new_height2

                # 如果两张图像尺寸不同，则调整为相同大小
                if width1 != width2 or height1 != height2:
                    print(f"图像尺寸不同，调整为相同大小")
                    print(
                        f"图像1尺寸: {width1}x{height1}, 图像2尺寸: {width2}x{height2}"
                    )

                    # 计算目标尺寸（取两张图像的最大宽度和最大高度）
                    target_width = max(width1, width2)
                    target_height = max(height1, height2)

                    # 调整图像大小
                    if width1 != target_width or height1 != target_height:
                        processed_image1 = resize_image(
                            processed_image1, target_width, target_height
                        )

                    if width2 != target_width or height2 != target_height:
                        processed_image2 = resize_image(
                            processed_image2, target_width, target_height
                        )

                    print(f"调整后的尺寸: {target_width}x{target_height}")
            except Exception as e:
                print(f"获取或调整图像尺寸时出错: {e}")
                # 如果出错，继续使用原始处理后的图像

        return (processed_image1, processed_image2, datetime_str)

    except Exception as e:
        print(f"处理图像对时出错: {e}")
        return (None, None, None)


def get_image_pairs(images_dir):
    """
    获取图像对

    Args:
        images_dir (str): 图像目录路径

    Returns:
        list: 图像对列表，每个元素是一个元组 (image1_path, image2_path)
    """
    # 获取目录中的所有图像文件
    image_files = []
    for root, _, files in os.walk(images_dir):
        for file in files:
            if file.lower().endswith((".jpg", ".jpeg", ".png")):
                image_files.append(os.path.join(root, file))

    # 如果图像文件数量为奇数，则移除最后一个
    if len(image_files) % 2 != 0:
        print(f"警告：图像文件数量为奇数，将忽略最后一个图像：{image_files[-1]}")
        image_files = image_files[:-1]

    # 如果没有图像文件，则返回空列表
    if not image_files:
        return []

    # 将图像文件分成对
    image_pairs = []
    for i in range(0, len(image_files), 2):
        image_pairs.append((image_files[i], image_files[i + 1]))

    return image_pairs


def get_manual_image_pairs(images_dir):
    """
    从images/before和images/after目录获取手动配对的图像对

    命名规则：
    - before目录: <pairing_id>_<optional_capa_index>.jpg/png
    - after目录: <pairing_id>.jpg/png

    Args:
        images_dir (str): 图像根目录路径

    Returns:
        list: 图像对列表，每个元素是一个元组 (before_image_path, after_image_path, capa_index, pairing_id)
              capa_index可能为None，表示随机选择CAPA
    """
    before_dir = os.path.join(images_dir, "before")
    after_dir = os.path.join(images_dir, "after")

    # 检查目录是否存在
    if not os.path.exists(before_dir) or not os.path.exists(after_dir):
        print(f"警告：before或after目录不存在，将使用默认图像对获取方法")
        return None

    # 获取before和after目录中的所有图像文件
    before_images = {}
    after_images = {}

    # 正则表达式匹配before图像的命名模式
    before_pattern = re.compile(r"^(\d+)(?:_(\d+))?\.(?:jpg|jpeg|png)$", re.IGNORECASE)
    after_pattern = re.compile(r"^(\d+)\.(?:jpg|jpeg|png)$", re.IGNORECASE)

    # 获取before目录中的图像
    for file in os.listdir(before_dir):
        if file.lower().endswith((".jpg", ".jpeg", ".png")):
            match = before_pattern.match(file)
            if match:
                pairing_id = int(match.group(1))
                capa_index = match.group(2)
                if capa_index:
                    capa_index = int(capa_index)
                before_images[pairing_id] = (os.path.join(before_dir, file), capa_index)

    # 获取after目录中的图像
    for file in os.listdir(after_dir):
        if file.lower().endswith((".jpg", ".jpeg", ".png")):
            match = after_pattern.match(file)
            if match:
                pairing_id = int(match.group(1))
                after_images[pairing_id] = os.path.join(after_dir, file)

    # 匹配图像对
    image_pairs = []
    for pairing_id in before_images:
        if pairing_id in after_images:
            before_image, capa_index = before_images[pairing_id]
            after_image = after_images[pairing_id]
            image_pairs.append((before_image, after_image, capa_index, pairing_id))

    if not image_pairs:
        print("警告：未找到匹配的图像对")
        return None

    print(f"找到 {len(image_pairs)} 对手动配对的图像")
    return image_pairs


def resize_image(image_path, target_width=None, target_height=None, output_path=None):
    """
    调整图像大小

    Args:
        image_path (str): 图像路径
        target_width (int, optional): 目标宽度，如果为None则保持原始宽高比
        target_height (int, optional): 目标高度，如果为None则保持原始宽高比
        output_path (str, optional): 输出路径，如果为None则覆盖原图像

    Returns:
        str: 调整大小后的图像路径
    """
    try:
        # 打开图像
        image = Image.open(image_path)

        # 获取原始尺寸
        original_width, original_height = image.size

        # 如果没有指定目标尺寸，则返回原图像路径
        if target_width is None and target_height is None:
            return image_path

        # 计算新尺寸，保持原始宽高比
        if target_width is None:
            # 只指定了高度，按比例计算宽度
            ratio = target_height / original_height
            new_width = int(original_width * ratio)
            new_height = target_height
        elif target_height is None:
            # 只指定了宽度，按比例计算高度
            ratio = target_width / original_width
            new_width = target_width
            new_height = int(original_height * ratio)
        else:
            # 同时指定了宽度和高度
            new_width = target_width
            new_height = target_height

        # 调整图像大小
        resized_image = image.resize((new_width, new_height), Image.LANCZOS)

        # 如果没有指定输出路径，则覆盖原图像
        if output_path is None:
            output_path = image_path

        # 保存图像，使用配置中的图像质量
        if output_path.lower().endswith((".jpg", ".jpeg")):
            resized_image.save(output_path, quality=config.IMAGE_QUALITY)
        else:
            # 对于非JPEG格式，不指定质量参数
            resized_image.save(output_path)

        return output_path

    except Exception as e:
        print(f"调整图像大小时出错: {e}")
        return None
