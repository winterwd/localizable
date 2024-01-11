# coding=utf-8
"""
:file: unLocalizable
:desc: 查找项目中未国际化的脚本,不准确仅供参考
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

# # 正则匹配(修改为自己的规则) @"你好!".yg_localized
# PATTERN = r'@"([^\"]*[\u4e00-\u9fa5]+[^\"]*)"(?!\s*\.yg_localized)'

# 正则匹配 NSLocalizedString(@"你好!", nil)
# PATTERN = r"(?<!NSLocalizedString\()\".*?[\u4e00-\u9fa5a-zA-Z]+.*?\"(?!, nil\))"
PATTERN = r"(?<!NSLocalizedString\()\".*?[\u4e00-\u9fa5]+.*?\"(?!, nil\))"
# swift NSLocalizedString("你好!", comment: "")
SWIFT_PATTERN = r"(?<!NSLocalizedString\()\".*?[\u4e00-\u9fa5]+.*?\"(?!, comment: \"\")"

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
    if str.startswith("NSLog") or str.startswith("FLOG") or str.startswith("print"):
        return True
    return False


# 是否为swift文件
def isSwiftFile(filePath):
    return filePath.endswith(".swift")


# 是否为OC文件
def isOCFile(filePath):
    return filePath.endswith(".m")


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

        # 正则表达式匹配
        matches: list
        if isOCFile(filePath):
            matches = re.findall(PATTERN, line)
        elif isSwiftFile(filePath):
            matches = re.findall(SWIFT_PATTERN, line)
        else:
            continue

        count = len(matches)
        if count > 0:
            if not isHaveWriteFileName:
                wf.write("\n" + fileName + "\n")
                isHaveWriteFileName = True

            for item in matches:
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
