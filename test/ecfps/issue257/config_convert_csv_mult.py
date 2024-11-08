import csv
import os
import re
from collections import defaultdict


main_config_boa = 'C:\\github\\ecfps\\ecfps-boa\\src\\main\\resources\\boa-core.properties'
bank_configs_boa = {
        'OCBC': 'C:\\github\\ecfps\\ecfps-boa\\src\\ocbc\\resources\\boa-core.properties',
        'DBS': 'C:\\github\\ecfps\\ecfps-boa\\src\\dsb\\resources\\boa-core.properties',
        'MOX': 'C:\\github\\ecfps\\ecfps-boa\\src\\mox\\resources\\boa-core.properties',
        'PBHK': 'C:\\github\\ecfps\\ecfps-boa\\src\\pbhk\\resources\\boa-core.properties',
        'SCB': 'C:\\github\\ecfps\\ecfps-boa\\src\\scb\\resources\\boa-core.properties',
        'WLB': 'C:\\github\\ecfps\\ecfps-boa\\src\\wlb\\resources\\boa-core.properties'
    }
output_file_boa = 'C:\\Users\\admin\\Desktop\\ecfps_doc\\issue-257\\boa-core-config-comparison.csv'

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


def read_properties(file_path):
    properties = {}
    current_comments = []

    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith('#'):
                current_comments.append(line[1:].strip())
            elif '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                properties[key] = {
                    'value': value,
                    'comments': ' '.join(current_comments)
                }
                current_comments = []

    return properties


def generate_config_csv(main_config, bank_configs, output_file, module, common_bank, branches):
    all_configs = set()
    bank_specific_configs = defaultdict(set)

    # 读取主配置和所有银行配置
    main_properties = read_properties(main_config)
    all_configs.update(main_properties.keys())

    bank_properties = {}
    for bank, config_file in bank_configs.items():
        bank_properties[bank] = read_properties(config_file)
        all_configs.update(bank_properties[bank].keys())

        # 找出每个银行特有的配置
        for key in bank_properties[bank]:
            if key not in main_properties:
                bank_specific_configs[bank].add(key)

    # 准备CSV数据
    headers = ['Module', 'File', 'Config', 'Default', 'Possible Value(s)', 'Description', 'Bank'] + list(
        branches.keys())
    csv_data = []

    # 首先添加所有通用配置
    for config in sorted(main_properties.keys()):
        prop = main_properties[config]
        value_type, possible_values = determine_type_and_possible_values(prop['value'])
        row = [
            module,
            os.path.basename(main_config),
            config,
            prop['value'],
            possible_values,
            prop['comments'],
            common_bank
        ]
        # 添加分支信息
        row.extend([branches.get(branch, '') for branch in branches])
        csv_data.append(row)

    # 然后按银行添加特有配置
    for bank, config_file in bank_configs.items():
        bank_specific_data = []
        for config in sorted(bank_specific_configs[bank]):
            prop = bank_properties[bank][config]
            value_type, possible_values = determine_type_and_possible_values(prop['value'])
            row = [
                module,
                os.path.basename(config_file),
                config,
                prop['value'],
                possible_values,
                prop['comments'],
                bank
            ]
            # 添加分支信息
            row.extend([branches.get(branch, '') for branch in branches])
            bank_specific_data.append(row)

        # 如果该银行有特有配置，添加一个空行作为分隔
        if bank_specific_data:
            if csv_data:  # 如果不是第一个银行，添加空行
                csv_data.append([''] * len(headers))
            csv_data.extend(bank_specific_data)

    # 写入CSV文件
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(csv_data)

    print(f"CSV file has been generated: {output_file}")


if __name__ == "__main__":
    # 使用示例


    main_config = 'C:\\github\\ecfps\\ecfps-web\\resources\\ecfps-core-acd.properties'
    bank_configs = {
        'OTHER': 'C:\\github\\ecfps\\ecfps-web\\ecfps-acd-web\\conf\\ecfps-core-acd.properties'
    }
    output_file = 'C:\\Users\\admin\\Desktop\\ecfps_doc\\issue-257\\acd-core-config-comparison.csv'


    # 新增的配置参数
    module = 'CBE'
    common_bank = 'Common'
    branches = {'2.1': '', '2.2': '', 'ocbc/uat': 'Y'}

    generate_config_csv(main_config, bank_configs, output_file, module, common_bank, branches)
