import csv
import os
import re


def determine_type_and_possible_values(value):
    # 移除首尾的引号（如果有）
    value = value.strip('"\'')

    # 布尔值
    if value.lower() in ['true', 'false']:
        return 'Boolean', 'true,false'

    # 整数
    elif value.isdigit():
        return 'Integer', 'Integer'

    # 浮点数
    elif re.match(r'^-?\d+(\.\d+)?$', value):
        return 'Float', 'Float'

    # 数组（假设用逗号分隔）
    elif ',' in value and all(v.strip() for v in value.split(',')):
        return 'Array', f'Array of {determine_type_and_possible_values(value.split(",")[0])[0]}s'

    # 文件路径
    elif os.path.sep in value or value.startswith('/') or re.match(r'^[a-zA-Z]:\\', value):
        return 'FilePath', 'Valid file path'

    # Cron表达式（简化版，可能需要更复杂的正则表达式）
    elif re.match(r'^(\*|[0-9,-/]+\s){4}(\*|[0-9,-/]+)$', value):
        return 'Cron', 'Valid cron expression'

    # 环境变量
    elif re.match(r'\$\{.*\}', value):
        return 'EnvironmentVariable', 'Environment variable'

    # URL
    elif re.match(r'^(http|https|ftp)://', value):
        return 'URL', 'Valid URL'

    # 日期时间格式（简化版，可能需要更多格式）
    elif re.match(r'\d{4}-\d{2}-\d{2}( \d{2}:\d{2}:\d{2})?', value):
        return 'DateTime', 'YYYY-MM-DD [HH:MM:SS]'

    # 如果都不匹配，默认为字符串
    else:
        return 'String', 'String'


def generate_config_csv(input_file, output_file, module, bank, branches):
    headers = ['Module', 'File', 'Config', 'Default', 'Possible Value(s)', 'Description'] + ['Bank'] + list(
        branches.keys()) + ['InputFile']

    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    csv_data = []
    current_comments = []

    for line in lines:
        line = line.strip()
        if line.startswith('#'):
            current_comments.append(line[1:].strip())
        elif '=' in line:
            config, default = line.split('=', 1)
            config = config.strip()
            default = default.strip()

            value_type, possible_values = determine_type_and_possible_values(default)

            description = ' '.join(current_comments)
            current_comments = []  # Reset comments for next config

            csv_row = [
                module,
                os.path.basename(input_file),
                config,
                default,
                possible_values,
                description
            ]

            # Add bank name
            csv_row.append(bank)

            # Add branch values
            for branch in branches:
                csv_row.append(branches[branch])

            # Add input path
            csv_row.append(input_file)

            csv_data.append(csv_row)

    # Write to CSV file
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(csv_data)

    print(f"CSV file has been generated: {output_file}")


if __name__ == "__main__":
    # 使用示例
    input_file = 'C:\\github\\ecfps\\ecfps-web\\resources\\ecfps-core-mqai.properties'
    output_file = 'C:\\Users\\admin\\Desktop\\ecfps_doc\\issue-257\\ecfps-core-mqai.csv'
    module = 'MQAI'
    bank = 'COMMON'
    branches = {'2.1': '', '2.2': '', 'ocbc/uat': 'Y'}
    generate_config_csv(input_file, output_file, module, bank, branches)
