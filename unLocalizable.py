# coding=utf-8
"""
:file: unLocalizable
:desc: 查找项目中未国际化的脚本,不准确仅供参考 适用于中文
"""

import os
import re

# 汉语写入文件时需要
import sys
import importlib

importlib.reload(sys)

# 将要解析的项目名称
DESPATH = "./test"

# 解析结果存放的路径
WDESPATH = "./result/unLocalizable.log"

# 目录黑名单，这个目录下所有的文件将被忽略
BLACKDIRLIST = [
    DESPATH + "/Classes/Personal/PERSetting/PERAccount",  # 多级目录
    DESPATH + "/Utils",  # Utils 下所有的文件将被忽略
    "xxx.m",  # 文件名直接写，将忽略这个文件
]

# 输出分隔符
SEPREATE = " <=> "
wf = None


def isInBlackList(filePath):
    if os.path.isfile(filePath):
        return fileNameAtPath(filePath) in BLACKDIRLIST
    if filePath:
        return filePath in BLACKDIRLIST
    return False


def fileNameAtPath(filePath):
    return os.path.split(filePath)[1]


def isSignalNote(str):
    if str.startswith("//"):
        return True
    if str.startswith("#pragma"):
        return True
    return False


def isLogMsg(str):
    if str.startswith("NSLog"):
        return True
    if str.startswith("FLOG"):
        return True
    if str.startswith("print"):
        return True
    if str.startswith("NSAssert"):
        return True
    if str.startswith("assert"):
        return True
    return False


# 是否为swift文件
def isSwiftFile(filePath):
    return filePath.endswith(".swift")


# 是否为OC文件
def isOCFile(filePath):
    return filePath.endswith(".m")


# 使用正则表达式匹配中文
def remove_special_characters(input_string):
    # 匹配中文、英文和数字，并将其保留 r"[^\u4e00-\u9fa5a-zA-Z0-9]"
    # 匹配中文 r"[^\u4e00-\u9fa5]"
    result = re.sub(r"[^\u4e00-\u9fa5]", "", input_string)
    return result


def unlocalizedStrs(filePath):
    f = open(filePath)
    fileName = fileNameAtPath(filePath)
    isMutliNote = False
    isHaveWriteFileName = False
    for index, line in enumerate(f):
        # 多行注释
        line = line.strip()
        if "/*" in line:
            isMutliNote = True
        if "*/" in line:
            isMutliNote = False
        if isMutliNote:
            continue

        # 单行注释
        if isSignalNote(line):
            continue

        # 打印信息
        if isLogMsg(line):
            continue

        # 替换文本中出现的\"转义字符 "abcd\"efg\"hij" -> "abcd&&efg&&hij"
        line_text = line.replace('\\"', "&&")
        # 找出文本中的所有 "" 的字符串
        matches = re.findall(r"\".*?\"", line_text)

        count = len(matches)
        if count > 0:
            write_texts = []
            for item in matches:
                # 去除字符串中所有的特殊字符
                if not remove_special_characters(item):
                    continue
                # 在对该 line 文本替换后，是否不会发生改变，如果没有变化那就说明没有国际化
                # [String:NSLocalizedString(@"abcd\"efg\"hij", nil) object] -> [String: object]
                if isOCFile(filePath):
                    temp = line_text.replace(f"NSLocalizedString(@{item}", "")
                elif isSwiftFile(filePath):
                    temp = line_text.replace(f"NSLocalizedString({item}", "")
                else:
                    continue

                if temp == line_text:
                    # 还原 && 去除字符串中所有的特殊字符
                    item = item.replace("&&", '\\"')
                    write_texts.append(item)

            if len(write_texts) > 0:
                if not isHaveWriteFileName:
                    wf.write("\n" + filePath)
                    wf.write("\n" + fileName + "\n")
                    isHaveWriteFileName = True

                for item in write_texts:
                    print("match = " + item)
                    wf.write(str(index + 1) + ": " + item + SEPREATE + line + "\n")


def findFromFile(path):
    paths = os.listdir(path)
    for aCompent in paths:
        aPath = os.path.join(path, aCompent)
        if isInBlackList(aPath):
            print("在黑名单中，被自动忽略" + aPath)
            continue
        if os.path.isdir(aPath):
            findFromFile(aPath)
        elif os.path.isfile(aPath) and (
            os.path.splitext(aPath)[1] == ".m" or os.path.splitext(aPath)[1] == ".swift"
        ):
            unlocalizedStrs(aPath)


def main():
    file_path = WDESPATH
    # 如果目录不存在，则创建目录
    output_dir = os.path.dirname(file_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print("创建目录：" + output_dir)

    global wf
    _wf = open(file_path, "w")
    wf = _wf
    findFromFile(DESPATH)
    _wf.close()
    print("已解析完成，结果已保存 : " + file_path)


if __name__ == "__main__":
    main()
