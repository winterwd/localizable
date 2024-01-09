#!/usr/bin/python3
# -*-: coding: utf-8 -*-
"""
:author: winter
:file: localizableReplace
:date: 2024/01/08
:desc: 替换已有的多国语言
"""

import os
import sys
import shutil

from logger import setup_logger
from DotPrinter import DotPrinter

# 已存在的多国语言文件目录
DESPATH = "./test/localString"
# 需要进行翻译的语言(如果先运行了 findLocalizable，就会生成以下路径的文件)
LOCALIZABLE_PATH = "./result/Localizable.strings"
# /zh-Hans.lproj/Localizable.strings
TARGET_LOCALIZABLE_DIR = "./result/Localizable/"
UNKNOWN_LOCALIZABLE_LOG = "./result/Localizable/unknown.log"
logger = setup_logger(f"{TARGET_LOCALIZABLE_DIR}logger.log")

# 正则匹配 "重新添加" = <#code#>;
PATTERN = r'"(?:\\.|[^"\\])*"'
REPLACE_TEXT = "<#code#>"

# 在该文件中找不到对应的 key=value，则注释这行
ANNOTATION_FILE_NAME = "zh-Hans"


# 单行注释
def isSignalNote(string):
    if string.startswith("//"):
        return True
    if string.startswith("#pragma"):
        return True
    return False


# 根据翻译中的语言类型，创建多语言文本
# keys: ["en.lproj", "cn.lproj"]
def create_localizable(source_file, keys):
    for key in keys:
        logger.info(f"create_localizable file :{key}/Localizable.strings")
        # 目标文件路径
        target_file = f"{TARGET_LOCALIZABLE_DIR}{key}/Localizable.strings"
        # 确保目标目录存在
        os.makedirs(os.path.dirname(target_file), exist_ok=True)
        try:
            # 复制文件 A 的内容到文件 B
            shutil.copyfile(source_file, target_file)
            # logger.info(f"文件 '{source_file}' 的内容已成功复制到文件 '{target_file}'。")
        except FileNotFoundError:
            logger.error(f"源文件 '{source_file}' 不存在。")
        except Exception as e:
            logger.error(f"复制文件时出现错误：{str(e)}")


# datas: {"zh_CN.lproj": {key:value}, "en.lproj": {key:value}, ...}
# localKeyLines: {key:line1, key:line2, ...}
def replace_localizable(datas, localKeyLines):
    try:
        os.remove(UNKNOWN_LOCALIZABLE_LOG)
    except Exception as e:
        logger.error(f"删除文件时出现错误: {e}")

    for file_name, zh_dict in datas.items():
        # file_name: zh_CN.lproj
        # zh_dict: {key:value}
        target_file = f"{TARGET_LOCALIZABLE_DIR}{file_name}/Localizable.strings"
        if not os.path.exists(target_file):
            logger.error(f"replace_localizable not find lang:{file_name} file")
            continue

        # 遍历localKeyLines，读取key和行号
        for key, line in localKeyLines.items():
            value = zh_dict.get(key, None)
            if value is None or value == "":
                logger.info(f"replace_localizable not find「{key}」")
                un_find_lang(key)

                if ANNOTATION_FILE_NAME in file_name:
                    # 如果是 zh-hans.lproj 则在该行最前面加上注释符号 //
                    replace_text(target_file, line, value, is_annotation=True)
            else:
                replace_text(target_file, line, value)


def un_find_lang(text):
    path = UNKNOWN_LOCALIZABLE_LOG
    # 打开文件以追加模式（如果文件不存在，则创建它）
    with open(path, "a", encoding="utf-8") as file:
        file.writelines(f'"{text}"' + "\n")


# 替换文本中的给定行数中的指定字符
# is_annotation 为 True 则在该行最前面加上注释符号 //
def replace_text(path, num, text, is_annotation=False):
    # 读取文件并将内容分割成行
    with open(path, "r") as file:
        lines = file.readlines()

    # 要替换的行号
    line_number_to_replace = num

    # 要替换的字符
    old_char = REPLACE_TEXT
    new_char = text

    # 检查行号是否在有效范围内
    if 0 <= line_number_to_replace < len(lines):
        # 获取要替换的行
        line_to_replace = lines[line_number_to_replace]
        if old_char not in line_to_replace:
            # 不存在 REPLACE_TEXT
            return
        
        if is_annotation:
            # 加上注释符号 //
            modified_line = "// " + line_to_replace
        else:
            # 执行替换操作
            modified_line = line_to_replace.replace(old_char, new_char)

        # 将修改后的行插回原文本
        lines[line_number_to_replace] = modified_line

        # 将修改后的文本写回文件
        with open(path, "w") as file:
            file.writelines(lines)

        # logger.info(f"替换行 {line_number_to_replace + 1} 中的 '{old_char}' 为 '{new_char}' 完成。")
    else:
        logger.info(f"行号 {line_number_to_replace} 超出文本范围。")


# 将内容以字典形式返回
# file_path: 'xx/en.lproj/Localizable.strings'
# "key" = "value";
def parse_localizable(file_path):
    # 读取文件并将内容分割成行
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()

    # 多行注释
    isMultiNote = False

    # 创建一个空的字典
    zh_dict = {}
    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 多行注释
        if line.startswith("/*"):
            isMultiNote = True
            continue
        if line.endswith("*/"):
            isMultiNote = False
            continue
        if isMultiNote:
            continue

        # 单行注释
        if line.startswith("//"):
            continue

        # 剔除文本末尾的英文分号
        line = line.strip(";")
        try:
            # 将行分割成两部分
            key, value = line.strip().split("=", 1)
            zh_dict[key] = value
        except:
            logger.error(f"文本处理异常：{line}")
            pass

    return zh_dict


# 将已给定的多语言转为字典数据格式，方便后面使用
# {"zh_CN.lproj": {key:value}, "en.lproj": {key:value}, ...}
def paras_preset_localising(dirPath):
    # 目录不存在
    output_dir = dirPath
    if not os.path.exists(output_dir):
        logger.info("给定的多语言目录不存在：" + output_dir)
        return None

    subdirectories = [
        name
        for name in os.listdir(output_dir)
        if os.path.isdir(os.path.join(output_dir, name))
    ]
    if len(subdirectories) == 0:
        return None

    datas = {}
    for subdirectory in subdirectories:
        # subdirectory: 'en.lproj'
        # file_path: 'xx/en.lproj/Localizable.strings'
        file_path = os.path.join(dirPath, subdirectory, "Localizable.strings")
        if not os.path.exists(file_path):
            logger.info("给定的多语言文件不存在：" + file_path)
            continue

        key = subdirectory
        datas[key] = parse_localizable(file_path)

    return datas


# 处理本地化 filePath: 'xx/Localizable.strings'，目标文件路径(DESPATH)
# 将每行的文本("key" = "value";)处理转为 {"key" : lineNumber}
def parse_local_line_number(filePath):
    f = open(filePath)

    data = {}
    # 遍历每行文本，读取key和行号
    for i, text in enumerate(f):
        text = text.strip()
        if not text:
            continue

        # 单行注释
        if isSignalNote(text):
            continue

        try:
            # 将行分割成两部分
            key, value = text.strip().split("=", 1)
            data[key] = i
        except:
            logger.error(f"文本处理读取行号异常：{text}")
            pass

    return data


def main():
    localizable_path = LOCALIZABLE_PATH
    if not os.path.exists(localizable_path):
        logger.error("LOCALIZABLE_PATH 不存在 = " + localizable_path)
        sys.exit()

    file_path = TARGET_LOCALIZABLE_DIR
    # 如果目录不存在，则创建目录
    output_dir = os.path.dirname(file_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logger.info("创建目录：" + output_dir)

    datas: {} = paras_preset_localising(DESPATH)
    if datas is None or len(datas) == 0:
        return

    create_localizable(localizable_path, datas.keys())
    localKeyLines = parse_local_line_number(localizable_path)
    replace_localizable(datas, localKeyLines)


if __name__ == "__main__":
    dot = DotPrinter()
    dot.start()
    main()
    dot.stop()
    print("已解析完成，结果已保存 : " + TARGET_LOCALIZABLE_DIR)
