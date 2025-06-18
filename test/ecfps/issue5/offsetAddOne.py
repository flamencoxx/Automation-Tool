import re

def main():
    file_path = "PayeeRemittanceOutwardReportRecordDTO.java"  # 直接写死文件名

    # 读取文件
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 替换：找到 offset = 数字，把数字+1
    def add_one(match):
        return match.group(1) + str(int(match.group(2)) + 1) + match.group(3)

    new_content = re.sub(r'(offset\s*=\s*)(\d+)(\s*,)', add_one, content)

    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print("完成")

if __name__ == "__main__":
    main()
