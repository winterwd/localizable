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

#  多语言翻译文件 Excel 格式："{"zh-Hans":"xxx","zh-Hant":"xxx","en":"xxx"}"
DESPATH = "/xxx.xlsx"
# 需要进行翻译的语言(如果先运行了 findLocalizable，就会生成以下路径的文件)
LOCALIZABLE_PATH = "./result/Localizable.strings"
# /zh-Hans.lproj/Localizable.strings
TARGET_LOCALIZABLE_DIR = "./result/Localizable/"
UNKNOWN_LOCALIZABLE_LOG = "./result/Localizable/unknown.log"
logger = setup_logger(f'{TARGET_LOCALIZABLE_DIR}logger.log')

# 正则匹配「"重新添加" = <#code#>;」
PATTERN = r'"(?:\\.|[^"\\])*"'
REPLACE_TEXT = '<#code#>'


# 单行注释
def isSignalNote(string):
    if '//' in string:
        return True
    if string.startswith('#pragma'):
        return True
    return False


#  解析取出 Excel 中的数据
def parse_xlsx(path):
    try:
        # 打开 Excel 文件
        wb = xw.Book(path)
        # 选择第一个工作表
        sheet = wb.sheets[0]
        # 获取工作表的使用范围（非空单元格的范围）
        used_range = sheet.used_range
        # 获取最后一列的数据
        last_column_data = used_range[:, -1].value
        return [item for item in last_column_data if item is not None]
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        return None
    finally:
        # 关闭 Excel 文件
        if 'wb' in locals():
            wb.close()
        # 退出 Excel 应用程序
        xw.apps.active.quit()
            


def parse_xlsx_data(array):
    # 取出数据中的中文作为 key
    new_dict = {}
    for d in array:
        try:
            temp = d.replace('\n', '')
            t_dict = json.loads(temp)
            value = t_dict['zh-Hans']
            if value is None:
                logger.error('parse_xlsx_data「zh-Hans」is None')
                return None
            new_dict[value] = t_dict
        except KeyError:
            continue
    return new_dict


def parse_localizable(path):
    # 获取需要翻译的数据，将作为 key
    f = open(path)
    data = []
    for line, text in enumerate(f):
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
            data.append({match: line})

    return data


# 根据翻译中的语言类型，创建多语言文本
def create_localizable(source_file, d):
    temp = d.replace('\n', '')
    zh_dict = json.loads(temp)
    for key in zh_dict:
        logger.info(f'create_localizable file :{key}.lproj/Localizable.strings')
        # 目标文件路径
        target_file = f'{TARGET_LOCALIZABLE_DIR}{key}.lproj/Localizable.strings'
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


def replace_localizable(zh_dict, local_list):
    try:
        os.remove(UNKNOWN_LOCALIZABLE_LOG)
    except Exception as e:
        logger.error(f'删除文件时出现错误: {e}')

    for local_dict in local_list:
        for key, line in local_dict.items():
            language = zh_dict.get(key, None)
            if language is None:
                logger.info(f'replace_localizable not find「{key}」')
                un_find_lang(key)
            else:
                for lang, text in language.items():
                    target_file = f'{TARGET_LOCALIZABLE_DIR}{lang}.lproj/Localizable.strings'
                    if not os.path.exists(target_file):
                        logger.info(f'replace_localizable not find lang:{lang} file')
                        continue
                    if text is None or text == '':
                        continue
                    # logger.info(f'replace_localizable lang:{lang} text:{text}')
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

    datas = parse_xlsx(DESPATH)
    zh_CN_dict = parse_xlsx_data(datas)
    create_localizable(localizable_path, datas[0])
    localizable_list = parse_localizable(localizable_path)
    replace_localizable(zh_CN_dict, localizable_list)


if __name__ == '__main__':
    dot = DotPrinter()
    dot.start()
    main()
    dot.stop()
    print('已解析完成，结果已保存 : ' + TARGET_LOCALIZABLE_DIR)