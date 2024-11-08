import os
import json
import re
import sys
from datetime import datetime

record_filename = "file_rename_record.json"

# 视频文件的扩展名集合
video_extensions = {
    '.mp4', '.mkv', '.avi', '.mov', '.flv', '.wmv', '.mpg', '.mpeg',
    '.m4v', '.h264', '.divx', '.ts', '.webm', '.3gp', '.3g2', '.qt',
    '.f4v', '.m2v', '.m4v', '.rm', '.rmvb', '.vob', '.ogv', '.gifv'
}


def is_video_file(filename):
    # 获取文件扩展名并判断是否在视频扩展名集合中
    _, ext = os.path.splitext(filename)
    return ext.lower() in video_extensions


def get_sorted_files_by_mtime(folder_path):
    # 获取文件夹内所有文件的完整路径
    files = [os.path.join(folder_path, f) for f in os.listdir(folder_path)]
    # 过滤掉目录，只保留文件
    files = [f for f in files if os.path.isfile(f)]
    # 按照最后修改时间对文件进行排序
    files.sort(key=lambda x: os.path.getmtime(x))
    return files


def simplify_filename(filename):
    # 示例：简化文件名，去除过长和无意义的部分
    max_length = 50  # 假设最大长度
    new_name = filename
    if len(filename) > max_length:
        base, ext = os.path.splitext(filename)
        new_name = base[:max_length] + ext
    return new_name


def is_processed(filename):
    # 正则表达式匹配模式：数字_日期_大小M/G
    pattern = r"^\d+_\d{8}_(\d+M|\d+G)_"
    return re.match(pattern, filename) is not None


def scan_and_rename_files(folder_path, added_files_count):
    record_path = os.path.join(folder_path, record_filename)

    # 如果记录文件不存在，创建一个新的
    if not os.path.exists(record_path):
        with open(record_path, 'w', encoding='utf-8') as record_file:
            json.dump({"processed_files": {}, "log": [], "current_id": 0}, record_file, indent=4)

    # 读取记录文件
    with open(record_path, 'r', encoding='utf-8') as record_file:
        record_data = json.load(record_file)

    processed_files = record_data.get("processed_files", {})
    log = record_data.get("log", [])
    current_id = record_data.get("current_id", 0)
    isProcessed = False

    # 获取当前文件夹下的所有文件
    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

    # 按文件的最后修改日期排序
    files.sort(key=lambda x: os.path.getmtime(os.path.join(folder_path, x)))
    # 遍历文件夹中的所有文件
    for filename in files:
        if is_processed(filename) or filename == record_filename or not is_video_file(filename):
            continue  # 跳过记录文件和非视频文件
        file_path = os.path.join(folder_path, filename)
        # 检查文件是否已经处理过
        if filename not in processed_files:
            current_id += 1
            new_name = generate_new_name(file_path, current_id)
            new_file_path = os.path.join(folder_path, new_name)
            os.rename(file_path, new_file_path)
            processed_files[filename] = new_name  # 使用原始文件路径作为键
            isProcessed = True
            log_entry = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "original_name": filename,
                "new_name": new_name,
                "id": current_id
            }
            log.append(log_entry)
    if isProcessed:
        log.append({"added_files_count": added_files_count})
    # 更新记录文件
    with open(record_path, 'w', encoding='utf-8') as record_file:
        json.dump({
            "processed_files": processed_files,
            "log": log,
            "current_id": current_id
        }, record_file, ensure_ascii=False, indent=4)


def generate_new_name(file_path, current_id):
    file_size = os.path.getsize(file_path)
    modification_time = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%Y%m%d")
    creation_time = datetime.fromtimestamp(os.path.getctime(file_path)).strftime("%Y%m%d")
    size_unit = "M" if file_size < 1024 ** 3 else "G"
    formatted_size = f"{file_size // (1024 ** 2) if size_unit == 'M' else file_size // (1024 ** 3)}{size_unit}"
    new_name = f"{current_id}_{modification_time}_{formatted_size}_{simplify_filename(os.path.basename(file_path))}"
    return new_name


if __name__ == "__main__":
    print("Number of arguments:", len(sys.argv), "arguments.")
    print("Argument List:", str(sys.argv))

    # 现在检查我们是否得到了三个参数：脚本名，文件夹路径，文件数量
    if len(sys.argv) == 3:
        folder_path = sys.argv[1]
        added_files_count = int(sys.argv[2])  # 确保转换为整数
        scan_and_rename_files(folder_path, added_files_count)
    else:
        print("Incorrect number of arguments provided.")

# if __name__ == "__main__":
#     folder_path = "/Volumes/flamenco-T7-2T/视频库"
#     added_files_count = 1
#     scan_and_rename_files(folder_path, added_files_count)
