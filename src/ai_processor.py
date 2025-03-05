#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
AI图像识别模块，使用CLIP Interrogator识别图片内容并使用NLP判断图片是"之前"还是"之后"
"""

import os
import sys
import torch

try:
    import nltk
    from nltk.corpus import stopwords

    NLTK_AVAILABLE = True
except ImportError:
    print("警告: nltk库不可用，将使用简化版文本处理")
    NLTK_AVAILABLE = False

import numpy as np
from PIL import Image

try:
    from transformers import CLIPProcessor, CLIPModel
    import open_clip

    CLIP_AVAILABLE = True
except ImportError:
    print("警告: transformers或open_clip库不可用，将使用简化版图像分析")
    CLIP_AVAILABLE = False

import config
import random

# 下载nltk数据
if NLTK_AVAILABLE:
    try:
        stopwords.words("english")
    except LookupError:
        nltk.download("stopwords")

# 全局变量，用于存储模型，避免重复加载
_clip_model = None
_clip_processor = None
_clip_interrogator = None


def load_clip_model():
    """
    加载CLIP模型（仅用于参考，当前未使用）

    Returns:
        tuple: (model, processor)
    """
    global _clip_model, _clip_processor

    if _clip_model is None or _clip_processor is None:
        try:
            print("正在加载CLIP模型...")
            _clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
            _clip_processor = CLIPProcessor.from_pretrained(
                "openai/clip-vit-base-patch32"
            )
            print("CLIP模型加载完成")
        except Exception as e:
            print(f"加载CLIP模型失败: {e}")
            _clip_model = None
            _clip_processor = None

    return _clip_model, _clip_processor


class ClipInterrogator:
    """CLIP Interrogator类，用于识别图片内容"""

    def __init__(self):
        # 如果CLIP库不可用，抛出异常
        if not CLIP_AVAILABLE:
            raise ImportError("CLIP库不可用，无法初始化CLIP Interrogator")

        print("初始化CLIP Interrogator...")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        # 修复：正确处理open_clip.create_model_and_transforms()返回的值
        model_and_transforms = open_clip.create_model_and_transforms(
            "ViT-L-14", pretrained="openai", device=self.device
        )

        # 解包返回值，可能返回3个或4个值
        if isinstance(model_and_transforms, tuple):
            if len(model_and_transforms) == 3:
                self.clip_model, self.clip_preprocess, _ = model_and_transforms
            elif len(model_and_transforms) == 4:
                self.clip_model, self.clip_preprocess, _, _ = model_and_transforms
            else:
                # 如果返回值格式变化，使用更安全的方式
                self.clip_model = model_and_transforms[0]
                self.clip_preprocess = model_and_transforms[1]
        else:
            # 如果返回值不是元组，可能是单个对象
            self.clip_model = model_and_transforms
            self.clip_preprocess = None
            raise ValueError("无法获取CLIP模型和预处理函数")

        self.tokenizer = open_clip.get_tokenizer("ViT-L-14")
        print(f"CLIP Interrogator初始化完成，使用设备: {self.device}")

    def interrogate(self, image_path, max_flavors=3):
        """
        识别图片内容

        Args:
            image_path (str): 图片路径
            max_flavors (int): 最大描述数量

        Returns:
            str: 图片内容描述
        """
        try:
            # 加载图片
            image = Image.open(image_path).convert("RGB")

            # 预处理图片
            image_tensor = self.clip_preprocess(image).unsqueeze(0).to(self.device)

            # 准备一些常见的描述词
            descriptions = [
                "construction site",
                "safety hazard",
                "workplace safety",
                "construction safety",
                "safety violation",
                "safety equipment",
                "protective gear",
                "hard hat",
                "safety vest",
                "safety goggles",
                "safety gloves",
                "safety boots",
                "safety harness",
                "safety sign",
                "warning sign",
                "danger sign",
                "caution sign",
                "safety barrier",
                "safety fence",
                "safety net",
                "safety tape",
                "safety cone",
                "safety ladder",
                "safety scaffold",
                "safety platform",
                "safety rail",
                "safety guard",
                "safety cover",
                "safety lock",
                "safety switch",
                "safety valve",
                "safety sensor",
                "safety alarm",
                "safety light",
                "safety camera",
                "safety monitor",
                "safety inspection",
                "safety audit",
                "safety training",
                "safety meeting",
                "safety briefing",
                "safety plan",
                "safety policy",
                "safety procedure",
                "safety protocol",
                "safety standard",
                "safety regulation",
                "safety requirement",
                "safety guideline",
                "safety manual",
                "safety handbook",
                "safety report",
                "safety record",
                "safety certificate",
                "safety certification",
                "safety compliance",
                "safety violation",
                "safety incident",
                "safety accident",
                "safety injury",
                "safety fatality",
                "safety near miss",
                "safety hazard",
                "safety risk",
                "safety danger",
                "safety threat",
                "safety emergency",
                "safety crisis",
                "safety disaster",
                "safety catastrophe",
                "clean workplace",
                "organized workplace",
                "tidy workplace",
                "neat workplace",
                "messy workplace",
                "disorganized workplace",
                "cluttered workplace",
                "dirty workplace",
                "unsafe condition",
                "safe condition",
                "hazardous condition",
                "dangerous condition",
                "risky condition",
                "precarious condition",
                "unstable condition",
                "stable condition",
                "secure condition",
                "insecure condition",
                "protected condition",
                "unprotected condition",
                "guarded condition",
                "unguarded condition",
                "shielded condition",
                "unshielded condition",
                "before repair",
                "after repair",
                "before maintenance",
                "after maintenance",
                "before cleaning",
                "after cleaning",
                "before organizing",
                "after organizing",
                "before fixing",
                "after fixing",
                "before improvement",
                "after improvement",
                "before renovation",
                "after renovation",
                "before restoration",
                "after restoration",
                "before upgrade",
                "after upgrade",
                "before update",
                "after update",
                "before modification",
                "after modification",
                "before alteration",
                "after alteration",
                "before transformation",
                "after transformation",
                "before conversion",
                "after conversion",
                "before change",
                "after change",
                "before adjustment",
                "after adjustment",
                "before correction",
                "after correction",
                "before rectification",
                "after rectification",
                "before remediation",
                "after remediation",
                "before treatment",
                "after treatment",
            ]

            # 计算图片与描述的相似度
            text_tokens = self.tokenizer(descriptions).to(self.device)
            with torch.no_grad():
                image_features = self.clip_model.encode_image(image_tensor)
                text_features = self.clip_model.encode_text(text_tokens)

                image_features /= image_features.norm(dim=-1, keepdim=True)
                text_features /= text_features.norm(dim=-1, keepdim=True)

                similarity = (100.0 * image_features @ text_features.T).softmax(dim=-1)
                values, indices = similarity[0].topk(max_flavors)

            # 获取最相似的描述
            top_descriptions = [descriptions[idx] for idx in indices]

            # 添加日志记录
            print(f"CLIP识别结果 ({os.path.basename(image_path)}):")
            for i, (desc, val) in enumerate(zip(top_descriptions, values)):
                print(f"  {i+1}. {desc} (置信度: {val.item():.2f})")

            return top_descriptions

        except Exception as e:
            print(f"图片识别出错: {e}")
            return ["unknown content"]


def get_clip_interrogator():
    """
    获取CLIP Interrogator实例

    Returns:
        ClipInterrogator: CLIP Interrogator实例，如果不可用则返回None
    """
    global _clip_interrogator

    # 如果CLIP库不可用，直接返回None
    if not CLIP_AVAILABLE:
        print("CLIP库不可用，将使用简化版图片识别功能")
        return None

    if _clip_interrogator is None:
        try:
            _clip_interrogator = ClipInterrogator()
        except Exception as e:
            print(f"初始化CLIP Interrogator失败: {e}")
            print("将使用简化版图片识别功能")
            _clip_interrogator = None

    return _clip_interrogator


def simple_image_analysis(image_path):
    """
    简化版图片分析，基于图片的基本特征

    Args:
        image_path (str): 图片路径

    Returns:
        list: 图片内容描述列表
    """
    try:
        # 加载图片
        image = Image.open(image_path).convert("RGB")

        # 计算图片的亮度、对比度等基本特征
        # 将图片转换为灰度图
        gray_image = image.convert("L")

        # 计算平均亮度
        brightness = np.mean(np.array(gray_image))

        # 计算对比度
        contrast = np.std(np.array(gray_image))

        print(
            f"图片分析 ({os.path.basename(image_path)}) - 亮度: {brightness:.2f}, 对比度: {contrast:.2f}"
        )

        # 根据亮度和对比度判断图片内容
        descriptions = []

        # 亮度高的图片可能是"之后"的图片
        if brightness > 150:
            descriptions.append("clean workplace")
            descriptions.append("organized workplace")
            descriptions.append("after improvement")
            descriptions.append("safe condition")
            descriptions.append("after cleaning")
            descriptions.append("after fixing")
            descriptions.append("workplace safety")
        else:
            descriptions.append("messy workplace")
            descriptions.append("safety hazard")
            descriptions.append("before improvement")
            descriptions.append("unsafe condition")
            descriptions.append("before cleaning")
            descriptions.append("before fixing")
            descriptions.append("safety violation")

        # 对比度高的图片可能有更多细节
        if contrast > 50:
            descriptions.append("detailed view")
            descriptions.append("clear image")
            descriptions.append("construction site")
            descriptions.append("safety equipment")
        else:
            descriptions.append("uniform scene")
            descriptions.append("simple view")
            descriptions.append("workplace environment")
            descriptions.append("safety area")

        # 添加一些通用的描述
        descriptions.append("construction safety")
        descriptions.append("workplace inspection")

        # 随机打乱描述顺序，避免总是选择相同的描述
        random.shuffle(descriptions)

        return descriptions[:5]  # 返回前5个描述

    except Exception as e:
        print(f"简化版图片分析出错: {e}")
        return ["unknown content"]


def is_before_image(descriptions):
    """
    判断图片是否为"之前"图片

    Args:
        descriptions (list): 图片内容描述列表

    Returns:
        bool: 是否为"之前"图片
    """
    # 统计"之前"和"之后"相关词汇的出现次数
    before_count = 0
    after_count = 0

    # 之前相关词汇
    before_keywords = [
        "before",
        "messy",
        "dirty",
        "unsafe",
        "hazard",
        "violation",
        "disorganized",
        "cluttered",
        "dangerous",
        "risky",
        "precarious",
        "unstable",
        "insecure",
        "unprotected",
        "unguarded",
        "unshielded",
    ]

    # 之后相关词汇
    after_keywords = [
        "after",
        "clean",
        "tidy",
        "safe",
        "organized",
        "neat",
        "secure",
        "stable",
        "protected",
        "guarded",
        "shielded",
        "improvement",
    ]

    # 统计词汇出现次数
    for desc in descriptions:
        desc_lower = desc.lower()

        # 检查"之前"相关词汇
        for keyword in before_keywords:
            if keyword in desc_lower:
                before_count += 1
                break

        # 检查"之后"相关词汇
        for keyword in after_keywords:
            if keyword in desc_lower:
                after_count += 1
                break

    print(
        f"'之前'相关词汇出现次数: {before_count}, '之后'相关词汇出现次数: {after_count}"
    )

    # 如果"之前"相关词汇出现次数更多，则判断为"之前"图片
    # 如果"之后"相关词汇出现次数更多，则判断为"之后"图片
    # 如果出现次数相同，则根据第一个描述判断
    if before_count > after_count:
        return True
    elif after_count > before_count:
        return False
    else:
        # 如果出现次数相同，则检查第一个描述
        if descriptions and descriptions[0].lower().startswith("before"):
            return True
        else:
            return False


def analyze_image_pair(image1_path, image2_path):
    """
    分析一对图片，识别内容并判断哪个是"之前"图片，哪个是"之后"图片

    Args:
        image1_path (str): 第一张图片路径
        image2_path (str): 第二张图片路径

    Returns:
        tuple: (before_image_path, after_image_path, content_description)
    """
    # 获取CLIP Interrogator实例
    interrogator = get_clip_interrogator()

    # 识别图片内容
    print(f"正在识别图片内容: {os.path.basename(image1_path)}")
    if interrogator:
        # 使用CLIP Interrogator
        image1_descriptions = interrogator.interrogate(image1_path)

        print(f"正在识别图片内容: {os.path.basename(image2_path)}")
        image2_descriptions = interrogator.interrogate(image2_path)
    else:
        # 使用简化版图片分析
        print("使用简化版图片分析...")
        image1_descriptions = simple_image_analysis(image1_path)
        print(
            f"简化分析结果 ({os.path.basename(image1_path)}): {', '.join(image1_descriptions)}"
        )

        image2_descriptions = simple_image_analysis(image2_path)
        print(
            f"简化分析结果 ({os.path.basename(image2_path)}): {', '.join(image2_descriptions)}"
        )

    # 判断哪个是"之前"图片，哪个是"之后"图片
    image1_is_before = is_before_image(image1_descriptions)
    image2_is_before = is_before_image(image2_descriptions)

    print(
        f"图片1 ({os.path.basename(image1_path)}) 是否为'之前'图片: {image1_is_before}"
    )
    print(
        f"图片2 ({os.path.basename(image2_path)}) 是否为'之前'图片: {image2_is_before}"
    )

    # 如果两张图片都被判断为"之前"或都被判断为"之后"，则使用第一张作为"之前"，第二张作为"之后"
    if image1_is_before == image2_is_before:
        print("两张图片的'之前/之后'判断结果相同，默认使用第一张作为'之前'图片")
        before_image_path = image1_path
        after_image_path = image2_path
        content_description = " ".join(image1_descriptions[:2])
    else:
        if image1_is_before:
            before_image_path = image1_path
            after_image_path = image2_path
            content_description = " ".join(image1_descriptions[:2])
        else:
            before_image_path = image2_path
            after_image_path = image1_path
            content_description = " ".join(image2_descriptions[:2])

    print(f"内容描述: {content_description}")
    return (before_image_path, after_image_path, content_description)


def simple_description_match(content_description, descriptions_list):
    """
    简化版描述匹配，基于关键词匹配

    Args:
        content_description (str): 图片内容描述
        descriptions_list (list): 描述列表，每个元素是一个元组 (描述, 纠正措施)

    Returns:
        tuple: (描述, 纠正措施)
    """
    # 如果描述列表为空，则返回默认描述
    if not descriptions_list:
        print("描述列表为空，返回默认描述")
        return ("无描述", "无纠正措施")

    print(f"内容描述: '{content_description}'")
    print(f"可用描述数量: {len(descriptions_list)}")

    # 打印前5个可用描述
    print("可用描述示例:")
    for i, (desc, action) in enumerate(descriptions_list[:5]):
        print(f"  {i+1}. 描述: '{desc}', 纠正措施: '{action}'")

    # 将内容描述分词
    content_words = set(content_description.lower().split())
    print(f"内容关键词: {', '.join(content_words)}")

    # 计算每个描述与内容描述的匹配度
    best_match_index = 0
    best_match_score = 0
    match_scores = []

    # 过滤掉过短的描述（如只有"Before "这样的）
    min_desc_length = 5  # 最小描述长度

    for i, (desc, _) in enumerate(descriptions_list):
        # 跳过过短的描述
        if len(desc.strip()) < min_desc_length:
            continue

        # 将描述分词
        desc_words = set(desc.lower().split())

        # 计算匹配度（加权分数）
        # 1. 交集大小
        intersection_size = len(content_words.intersection(desc_words))
        # 2. 描述长度奖励（避免选择过短的描述）
        length_bonus = min(1.0, len(desc.strip()) / 20.0)  # 最多1.0的奖励
        # 3. 词汇丰富度奖励（避免选择词汇单一的描述）
        vocab_bonus = min(1.0, len(desc_words) / 5.0)  # 最多1.0的奖励

        # 综合分数
        match_score = intersection_size + length_bonus + vocab_bonus

        match_scores.append((i, match_score, desc))

        # 更新最佳匹配
        if match_score > best_match_score:
            best_match_score = match_score
            best_match_index = i

    # 打印匹配分数最高的前3个
    print("匹配分数最高的描述:")
    sorted_matches = sorted(match_scores, key=lambda x: x[1], reverse=True)
    for i, (idx, score, desc) in enumerate(sorted_matches[:3]):
        print(f"  {i+1}. 描述: '{desc}', 匹配分数: {score}")

    # 如果没有找到匹配的描述，或者最佳匹配分数太低，则选择一个有意义的描述
    if not match_scores or best_match_score < 0.5:
        print("没有找到好的匹配描述，选择一个有意义的描述")
        # 按描述长度排序，选择一个较长的描述
        meaningful_descriptions = [
            (i, len(desc.strip()), desc)
            for i, (desc, _) in enumerate(descriptions_list)
            if len(desc.strip()) >= min_desc_length
        ]

        if meaningful_descriptions:
            # 按描述长度排序，选择一个较长的描述
            sorted_by_length = sorted(
                meaningful_descriptions, key=lambda x: x[1], reverse=True
            )
            best_match_index = sorted_by_length[0][0]
            print(f"选择了较长的描述: '{descriptions_list[best_match_index][0]}'")
        else:
            # 如果没有足够长的描述，随机选择一个
            best_match_index = random.randint(0, len(descriptions_list) - 1)
            print(f"随机选择描述: '{descriptions_list[best_match_index][0]}'")

    result = descriptions_list[best_match_index]
    print(f"选择的描述: '{result[0]}'")
    print(f"选择的纠正措施: '{result[1]}'")

    return result


def find_best_description_match(content_description, descriptions_list):
    """
    根据图片内容描述，从Excel数据中找到最匹配的描述

    Args:
        content_description (str): 图片内容描述
        descriptions_list (list): 描述列表，每个元素是一个元组 (描述, 纠正措施)

    Returns:
        tuple: (描述, 纠正措施)
    """
    # 如果描述列表为空，则返回默认描述
    if not descriptions_list:
        return ("无描述", "无纠正措施")

    try:
        # 使用简化版描述匹配，因为CLIP模型需要图像输入
        # 这里我们只有文本描述，没有图像，所以不能直接使用CLIP模型
        print("使用简化版描述匹配...")
        return simple_description_match(content_description, descriptions_list)

    except Exception as e:
        print(f"描述匹配出错: {e}")
        print("使用简化版描述匹配...")
        return simple_description_match(content_description, descriptions_list)


def process_image_pair_with_ai(image1_path, image2_path, descriptions_list):
    """
    使用AI处理一对图片，识别内容，判断哪个是"之前"图片，哪个是"之后"图片，并选择最匹配的描述

    Args:
        image1_path (str): 第一张图片路径
        image2_path (str): 第二张图片路径
        descriptions_list (list): 描述列表，每个元素是一个元组 (描述, 纠正措施)

    Returns:
        tuple: (before_image_path, after_image_path, description, action)
    """
    try:
        # 分析图片对
        before_image_path, after_image_path, content_description = analyze_image_pair(
            image1_path, image2_path
        )

        print(
            f"AI识别结果: 之前图片={os.path.basename(before_image_path)}, 之后图片={os.path.basename(after_image_path)}"
        )

        # 找到最匹配的描述
        description, action = find_best_description_match(
            content_description, descriptions_list
        )

        # 确保描述不为空
        if not description or description.strip() == "":
            print("警告: 选择的描述为空，使用默认描述")
            description = "安全隐患"

        if not action or action.strip() == "":
            print("警告: 选择的纠正措施为空，使用默认纠正措施")
            action = "采取安全措施，消除隐患"

        print(f"最终选择的描述: '{description}'")
        print(f"最终选择的纠正措施: '{action}'")

        return (before_image_path, after_image_path, description, action)

    except Exception as e:
        print(f"处理图片对时出错: {e}")
        # 返回默认值
        print("使用默认值")
        return (image1_path, image2_path, "安全隐患", "采取安全措施，消除隐患")
