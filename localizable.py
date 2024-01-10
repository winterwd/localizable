#!/usr/bin/python3
# -*-: coding: utf-8 -*-
"""
:author: winter
:file: localizable
:date: 2023/09/11
:desc: 从 Excel 中找出对应的多国语言的文件,转为对应的Localizable.strings
"""

import os
import sys
import re
import shutil
import json
import xlwings as xw
from logger import setup_logger
from DotPrinter import DotPrinter

# 多语言翻译文件 Excel 文件
# line1: 语言类型 = zh-Hans, en ...
EXCEL_PATH = "./test/localString/localizable.xlsx"
# 需要进行翻译的语言(如果先运行了 findLocalizable，就会生成以下路径的文件)
LOCALIZABLE_PATH = "./result/Localizable.strings"
# /zh-Hans.lproj/Localizable.strings
TARGET_LOCALIZABLE_DIR = "./result/Localizable"
UNKNOWN_LOCALIZABLE_LOG = f"{TARGET_LOCALIZABLE_DIR}/unknown.log"
logger = setup_logger(f"{TARGET_LOCALIZABLE_DIR}/logger.log")

# 正则匹配 "重新添加" = "<#code#>";
PATTERN = r'"(?:\\.|[^"\\])*"'
REPLACE_TEXT = '<#code#>'


# 单行注释
def isSignalNote(string):
    if string.startswith("//"):
        return True
    if string.startswith('#pragma'):
        return True
    return False


# 解析取出 Excel 中的数据
# return {"zh-Hans": {"中文": "中文", "英文": "英文"}, "en": {"chinese": "chinese", "english": "english"}...}
def parse_xlsx(path):
    try:
        # 打开 Excel 文件
        wb = xw.Book(path)
        # 选择第一个工作表
        sheet = wb.sheets[0]
        # 获取工作表的使用范围（非空单元格的范围）
        used_range = sheet.used_range

        # 获取数据范围
        data_range = sheet.range("A1").expand("table")

        # 获取第一行和第一列的标签
        column_labels = data_range[0, 0:].value
        row_labels = data_range[1:, 0].value

        # 创建空字典来存储结果
        result_dict = {}

        # 遍历数据并构建字典
        for i, col_label in enumerate(column_labels):
            inner_dict = {}
            for j, row_label in enumerate(row_labels):
                inner_dict[row_label] = data_range[j + 1, i].value
            result_dict[col_label] = inner_dict

        return result_dict
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        return None
    finally:
        # 关闭 Excel 文件
        if 'wb' in locals():
            wb.close()
        # 退出 Excel 应用程序
        xw.apps.active.quit()
            

# 解析取出 Localizable.strings 中的需要翻译的文本
# file_path: 'xx/en.lproj/Localizable.strings'
# return: {"key": lineNumber,...};
def parse_localizable(path):
    # 获取需要翻译的数据，将作为 key
    f = open(path)
    data = {}
    for line, text in enumerate(f):
        text = text.strip()
        if not text:
            continue

        # 单行注释
        if isSignalNote(text):
            continue

        # 使用 re 模块的 findall 函数进行匹配
        matches = re.findall(PATTERN, text)
        count = len(matches)
        if count == 1:
            match = matches[0]
            # 去除双引号和转义字符，只保留内部内容，并去除首尾的双引号
            match = match[1:-1].replace('\\"', '"')
            data[match] = line

    return data


# 根据翻译中的语言类型，创建多语言文本
# keys: ["en", "cn"]
def create_localizable(source_file, keys):
    for key in keys:
        logger.info(f"create_localizable file :{key}.lproj/Localizable.strings")
        # 目标文件路径
        target_file = f"{TARGET_LOCALIZABLE_DIR}/{key}.lproj/Localizable.strings"
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


# datas: {"zh-Hans":{"中文":"中文",...}, "en": :{"en":"en",...}}
# key_lineNumber: {"中文":1,"en":2}
def replace_localizable(datas, key_lineNumber):
    try:
        os.remove(UNKNOWN_LOCALIZABLE_LOG)
    except Exception as e:
        logger.error(f'删除文件时出现错误: {e}')

    langs = datas.keys()
    for lang in langs:
        target_file = f"{TARGET_LOCALIZABLE_DIR}/{lang}.lproj/Localizable.strings"
        if not os.path.exists(target_file):
            logger.info(f"replace_localizable not find lang:{lang} file")
            continue

        logger.info(f"replace_localizable lang:「{lang}」file")
        lang_datas = datas.get(lang)
        # 开始替换每一个语言中的文本
        for key, line in key_lineNumber.items():
            text = lang_datas.get(key, None)
            if text is None:
                logger.info(f"replace_localizable not find「{key}」")
                un_find_lang(key)
            else:
                replace_text(target_file, line, text)


def un_find_lang(text):
    path = UNKNOWN_LOCALIZABLE_LOG
    # 打开文件以追加模式（如果文件不存在，则创建它）
    with open(path, 'a', encoding='utf-8') as file:
        file.writelines(f'"{text}"'+'\n')


# 替换文本中的给定行数中的指定字符
def replace_text(path, num, text):
    # 读取文件并将内容分割成行
    with open(path, 'r') as file:
        lines = file.readlines()

    # 要替换的行号
    line_number_to_replace = num

    # 要替换的字符
    old_char = REPLACE_TEXT
    new_char = f'"{text}"'

    # 检查行号是否在有效范围内
    if 0 <= line_number_to_replace < len(lines):
        # 获取要替换的行
        line_to_replace = lines[line_number_to_replace]

        # 执行替换操作
        modified_line = line_to_replace.replace(old_char, new_char)

        # 将修改后的行插回原文本
        lines[line_number_to_replace] = modified_line

        # 将修改后的文本写回文件
        with open(path, 'w') as file:
            file.writelines(lines)

        # logger.info(f"替换行 {line_number_to_replace + 1} 中的 '{old_char}' 为 '{new_char}' 完成。")
    else:
        logger.info(f"行号 {line_number_to_replace} 超出文本范围。")


def main():
    localizable_path = LOCALIZABLE_PATH
    if not os.path.exists(localizable_path):
        logger.error('LOCALIZABLE_PATH 不存在 = ' + localizable_path)
        sys.exit()

    file_path = TARGET_LOCALIZABLE_DIR
    # 如果目录不存在，则创建目录
    output_dir = os.path.dirname(file_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logger.info('创建目录：' + output_dir)

    datas = parse_xlsx(EXCEL_PATH)
    if datas is None:
        return

    create_localizable(localizable_path, datas.keys())
    key_lineNumber = parse_localizable(localizable_path)
    replace_localizable(datas, key_lineNumber)


if __name__ == '__main__':
    dot = DotPrinter()
    dot.start()
    main()
    dot.stop()
    print('已解析完成，结果已保存 : ' + TARGET_LOCALIZABLE_DIR)