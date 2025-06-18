import re
import sys


def process_dto_file(file_path):
    """处理DTO文件，为字段添加@CSVField注解"""

    # 读取文件
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    order = 1

    for line in lines:
        # 检查是否为字段声明行
        if is_field_line(line):
            # 添加注解
            indent = get_indent(line)
            annotation = f"{indent}@CSVField(order = {order})\n"
            new_lines.append(annotation)
            order += 1

        new_lines.append(line)

    # 写回原文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

    print(f"✅ 处理完成! 共添加了 {order - 1} 个注解")


def is_field_line(line):
    """判断是否为字段声明行"""
    line = line.strip()

    # 跳过空行、注释、方法等
    if (not line or
            line.startswith('//') or
            line.startswith('/*') or
            line.startswith('*') or
            line.startswith('@') or
            line.startswith('public ') or
            line.startswith('protected ') or
            'class ' in line or
            line.startswith('{') or
            line.startswith('}') or
            '(' in line and ')' in line):  # 方法调用
        return False

    # 匹配字段声明: private/public/protected + 类型 + 字段名 + ; 或 =
    pattern = r'\b(private|public|protected)\s+\w+.*?\w+\s*[;=]'
    return bool(re.search(pattern, line))


def get_indent(line):
    """获取行的缩进"""
    return line[:len(line) - len(line.lstrip())]


if __name__ == "__main__":
    process_dto_file('PayeeRemittanceOutwardReportRecordDTO.java')