import PyInstaller.__main__
import sys
import os

# 获取当前目录
current_dir = os.path.dirname(os.path.abspath(__file__))

PyInstaller.__main__.run([
    'SwiftConverterUI.py',  # 你的主程序文件名
    '--name=SWIFT报文转换工具',  # 生成的exe名称
    '--windowed',  # 不显示控制台窗口
    '--onefile',  # 打包成单个文件
    f'--icon={os.path.join(current_dir, "icon.ico")}',  # 如果有图标的话
    '--add-data=tool;tool',  # 添加tool文件夹
    '--clean',  # 清理临时文件
    '--noconfirm',  # 不确认覆盖
])
