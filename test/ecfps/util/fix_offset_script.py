import re


def fix_field_offsets(java_code):
    lines = java_code.split('\n')
    result_lines = []

    # 存储当前应该的offset
    current_offset = None

    for line in lines:
        # 检查是否包含@Field注解
        if '@Field(' in line:
            # 提取offset和length，不管它们的顺序
            offset_match = re.search(r'offset\s*=\s*(\d+)', line)
            length_match = re.search(r'length\s*=\s*(\d+)', line)

            if offset_match and length_match:
                old_offset = int(offset_match.group(1))
                length = int(length_match.group(1))

                if current_offset is None:
                    # 第一个offset保持不变
                    current_offset = old_offset
                    result_lines.append(line)
                else:
                    # 替换offset值
                    new_line = re.sub(
                        r'offset\s*=\s*\d+',
                        f'offset = {current_offset}',
                        line
                    )
                    result_lines.append(new_line)

                    # 如果offset被修改了，打印提示
                    if old_offset != current_offset:
                        print(f"修正: offset {old_offset} -> {current_offset} (length={length})")

                # 计算下一个offset
                current_offset = current_offset + length
            else:
                # 如果@Field注解中没有找到offset或length，保持原样
                result_lines.append(line)
                print(f"警告: 无法解析 @Field 注解: {line.strip()}")
        else:
            result_lines.append(line)

    return '\n'.join(result_lines)


# 使用方法
if __name__ == "__main__":
    # 读取Java文件
    with open('XbPaymentInfo.java', 'r', encoding='utf-8') as f:
        java_code = f.read()

    # 修正offset
    fixed_code = fix_field_offsets(java_code)

    # 写回文件（或者写到新文件）
    with open('XbPaymentInfo-output.java', 'w', encoding='utf-8') as f:
        f.write(fixed_code)

    print("处理完成！")
