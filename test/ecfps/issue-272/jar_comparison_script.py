import os
import json
import shutil
import logging
from datetime import datetime
import configparser
from pathlib import Path
import sys

# 设置日志
logging.basicConfig(filename='jar_comparison.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class TeeLogger:
    def __init__(self, filename):
        self.terminal = sys.stdout
        self.log = open(filename, "a")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        self.flush()

    def flush(self):
        self.terminal.flush()
        self.log.flush()

sys.stdout = TeeLogger("detailed_process.log")

def log_info(message):
    print(message)
    logging.info(message)


def read_config(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
    return config


def validate_paths(config):
    paths = ['tomcat_path', 'maven_path', 'input_json', 'output_folder']
    for path in paths:
        if not os.path.exists(config['Paths'][path]):
            if path == 'output_folder':
                os.makedirs(config['Paths'][path])
                logging.info(f"Created output folder: {config['Paths'][path]}")
            else:
                logging.error(f"Path does not exist: {config['Paths'][path]}")
                return False
    return True


def load_json_data(json_file):
    with open(json_file, 'r') as f:
        return json.load(f)


def scan_tomcat_webapps(tomcat_path):
    webapps_path = os.path.join(tomcat_path, 'webapps')
    return {dir_name: os.path.join(webapps_path, dir_name, 'WEB-INF', 'lib')
            for dir_name in os.listdir(webapps_path)
            if os.path.isdir(os.path.join(webapps_path, dir_name, 'WEB-INF', 'lib'))}


def find_jar_in_maven(maven_path, jar_name):
    logging.info(f"Searching for {jar_name} in {maven_path}")
    for root, dirs, files in os.walk(maven_path):
        for file in files:
            logging.debug(f"Found file: {file}")
        if jar_name in files:
            logging.info(f"Found {jar_name} at {os.path.join(root, jar_name)}")
            return os.path.join(root, jar_name)
    logging.warning(f"Could not find {jar_name} in Maven repository")
    return None



def convert_size_to_bytes(size_str):
    """将带单位的大小字符串转换为字节数"""
    size_str = size_str.upper()
    if size_str.endswith('K'):
        return int(float(size_str[:-1]) * 1024)
    elif size_str.endswith('M'):
        return int(float(size_str[:-1]) * 1024 * 1024)
    elif size_str.endswith('G'):
        return int(float(size_str[:-1]) * 1024 * 1024 * 1024)
    else:
        return int(float(size_str))  # 假设没有单位时为字节

def bytes_to_human_readable(bytes_size):
    for unit in ['', 'K', 'M', 'G']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f}{unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f}T"


def compare_jars(local_jar, client_jar):
    local_size = os.path.getsize(local_jar)
    local_mtime = datetime.fromtimestamp(os.path.getmtime(local_jar))

    client_size = convert_size_to_bytes(client_jar['size'])

    size_difference = abs(local_size - client_size)
    size_tolerance = max(local_size, client_size) * 0.01

    return {
        'name': os.path.basename(local_jar),
        'local_size': bytes_to_human_readable(local_size),
        'local_mtime': local_mtime.strftime("%Y-%m-%d %H:%M:%S"),
        'client_size': client_jar['size'],
        'client_mtime': client_jar['lastModified'],
        'size_match': size_difference <= size_tolerance,
        'mtime_match': local_mtime.strftime("%Y-%m-%d %H:%M:%S") == client_jar['lastModified'],
        'version_match': os.path.basename(local_jar) == client_jar['name']
    }


def process_service(service_name, service_data, tomcat_lib_path, maven_path, output_folder, replace_jars):
    service_output = os.path.join(output_folder, service_name)
    os.makedirs(service_output, exist_ok=True)
    backup_folder = os.path.join(service_output, 'backup')
    maven_folder = os.path.join(service_output, 'maven_jars')
    os.makedirs(backup_folder, exist_ok=True)
    os.makedirs(maven_folder, exist_ok=True)

    report = {'matching_jars': [], 'mismatching_jars': [], 'missing_local': [], 'missing_client': []}

    local_jars = set(os.listdir(tomcat_lib_path))
    client_jars = set(jar['name'] for jar in service_data['jars'])

    log_info(f"Started processing service: {service_name}")

    for jar in service_data['jars']:
        local_jar_path = os.path.join(tomcat_lib_path, jar['name'])
        if os.path.exists(local_jar_path):
            comparison = compare_jars(local_jar_path, jar)
            if comparison['version_match'] and comparison['size_match'] and comparison['name'] == jar['name']:
                report['matching_jars'].append(comparison)
                log_info(f"JAR {jar['name']} matches in {service_name}")
            else:
                report['mismatching_jars'].append(comparison)
                log_info(f"JAR {jar['name']} mismatches in {service_name}")
        else:
            report['missing_local'].append(jar['name'])
            log_info(f"JAR {jar['name']} is missing locally in {service_name}")

    for local_jar in local_jars - client_jars:
        report['missing_client'].append(local_jar)
        log_info(f"JAR {local_jar} is missing in client data for {service_name}")

    # 输出报告
    with open(os.path.join(service_output, f'{service_name}_report.json'), 'w') as f:
        json.dump(report, f, indent=2)

    log_info(f"Report generated for service: {service_name}")

    # 处理不匹配的 JAR 文件
    for comparison in report['mismatching_jars']:
        jar_name = comparison['name']
        maven_jar = find_jar_in_maven(maven_path, jar_name)
        if maven_jar:
            log_info(f"Copying {jar_name} from {maven_jar} to {maven_folder}")
            shutil.copy2(maven_jar, maven_folder)

        # 无论是否在 Maven 中找到，都备份 Tomcat 中的 JAR 文件
        local_jar_path = os.path.join(tomcat_lib_path, jar_name)
        if os.path.exists(local_jar_path):
            log_info(f"Backing up {jar_name} from {local_jar_path} to {backup_folder}")
            shutil.copy2(local_jar_path, backup_folder)

        if maven_jar and replace_jars:
            log_info(f"Replacing {jar_name} in {local_jar_path} with {maven_jar}")
            shutil.copy2(maven_jar, local_jar_path)

    # 处理本地缺失的 JAR 文件
    for missing_jar in report['missing_local']:
        maven_jar = find_jar_in_maven(maven_path, missing_jar)
        if maven_jar:
            log_info(f"Found missing JAR {missing_jar} in Maven, copying to {maven_folder}")
            shutil.copy2(maven_jar, maven_folder)
        else:
            log_info(f"Could not find missing JAR {missing_jar} in Maven repository for {service_name}")

    log_info(f"Finished processing service: {service_name}")



def main():
    config = read_config('config.ini')
    if not validate_paths(config):
        return

    tomcat_path = config['Paths']['tomcat_path']
    maven_path = config['Paths']['maven_path']
    input_json = config['Paths']['input_json']
    output_folder = config['Paths']['output_folder']
    replace_jars = config['Options'].getboolean('replace_jars')

    webapps = scan_tomcat_webapps(tomcat_path)

    if os.path.isfile(input_json):
        data = load_json_data(input_json)
        if data['service'] in webapps:
            process_service(data['service'], data, webapps[data['service']], maven_path, output_folder, replace_jars)
        else:
            logging.warning(f"Service {data['service']} not found in Tomcat webapps")
    elif os.path.isdir(input_json):
        for json_file in os.listdir(input_json):
            if json_file.endswith('.json'):
                data = load_json_data(os.path.join(input_json, json_file))
                if data['service'] in webapps:
                    process_service(data['service'], data, webapps[data['service']], maven_path, output_folder,
                                    replace_jars)
                else:
                    logging.warning(f"Service {data['service']} not found in Tomcat webapps")
    else:
        logging.error("Invalid input_json path")


if __name__ == "__main__":
    main()
