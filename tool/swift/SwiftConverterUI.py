import sys
import json
import requests
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QTextEdit, QPushButton, QLabel,
                             QMessageBox, QSplitter)
from PyQt6.QtCore import Qt
import xml.dom.minidom


class SwiftConverterUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # 设置窗口基本属性
        self.setWindowTitle('SWIFT报文转换工具')
        self.setGeometry(100, 100, 1200, 800)

        # 创建主widget和布局
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # 创建分割器实现左右布局
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # 左侧面板（输入）
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.addWidget(QLabel('输入报文:'))
        self.input_text = QTextEdit()
        self.input_text.setFontFamily('Courier New')  # 使用等宽字体
        left_layout.addWidget(self.input_text)

        # 右侧面板（输出）
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.addWidget(QLabel('转换结果:'))
        self.output_text = QTextEdit()
        self.output_text.setFontFamily('Courier New')
        self.output_text.setReadOnly(True)
        right_layout.addWidget(self.output_text)

        # 添加到分割器
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        layout.addWidget(splitter)

        # 按钮区域
        button_layout = QHBoxLayout()

        # MT转MX按钮
        self.mt_to_mx_btn = QPushButton('MT → MX')
        self.mt_to_mx_btn.clicked.connect(lambda: self.convert('mt2mx'))
        button_layout.addWidget(self.mt_to_mx_btn)

        # MX转MT按钮
        self.mx_to_mt_btn = QPushButton('MX → MT')
        self.mx_to_mt_btn.clicked.connect(lambda: self.convert('mx2mt'))
        button_layout.addWidget(self.mx_to_mt_btn)

        # 复制结果按钮
        self.copy_btn = QPushButton('复制结果')
        self.copy_btn.clicked.connect(self.copy_output)
        button_layout.addWidget(self.copy_btn)

        # 清除按钮
        self.clear_btn = QPushButton('清除')
        self.clear_btn.clicked.connect(self.clear_all)
        button_layout.addWidget(self.clear_btn)

        layout.addLayout(button_layout)

    def format_xml(self, xml_string):
        """格式化XML字符串，减少不必要的空行"""
        try:
            # 解析XML
            dom = xml.dom.minidom.parseString(xml_string)
            # 获取格式化的XML，但包含很多空行
            pretty_xml = dom.toprettyxml(indent='  ')

            # 清理多余的空行，只保留包含实际内容的行
            cleaned_lines = [line for line in pretty_xml.splitlines()
                             if line.strip() and not line.isspace()]

            # 重新组合，使用单个换行符
            return '\n'.join(cleaned_lines)
        except:
            return xml_string

    def format_mt(self, mt_string):
        """格式化MT报文"""
        return '\n'.join(line.strip() for line in mt_string.split('\n') if line.strip())

    def convert(self, conv_type):
        """执行转换操作"""
        input_text = self.input_text.toPlainText().strip()
        if not input_text:
            QMessageBox.warning(self, '警告', '请输入需要转换的报文')
            return

        try:
            # 确定API端点
            endpoint = 'convertMtToMx' if conv_type == 'mt2mx' else 'convertMxMessageToMtMessage'
            url = f'http://localhost:8080/mcg/{endpoint}'

            # 发送请求
            response = requests.post(
                url,
                headers={'Content-Type': 'application/json'},
                json={
                    'originalMsg': input_text,
                    'additionalData': '{}'
                }
            )

            response.raise_for_status()
            result = response.json()

            # 根据不同的转换类型处理返回结果
            if conv_type == 'mt2mx':
                # MT转MX的情况
                if result['status'] == 'Success':
                    converted_msg = result['data']['convertedMsg']
                    # 检查是否有转换问题
                    if result['data']['conversionIssues']:
                        QMessageBox.warning(self, '警告',
                                            '转换完成，但存在以下问题：\n' +
                                            '\n'.join(str(issue) for issue in result['data']['conversionIssues']))
                else:
                    raise Exception('转换失败')
            else:
                # MX转MT的情况
                if result['translationResult'] == 'TROK':
                    converted_msg = result['translatedMTMessage']
                    if result['errors']:
                        QMessageBox.warning(self, '警告',
                                            '转换完成，但存在错误：\n' + str(result['errors']))
                else:
                    raise Exception('转换失败')

            # 格式化输出
            formatted_output = (self.format_xml(converted_msg)
                                if conv_type == 'mt2mx'
                                else self.format_mt(converted_msg))

            # 显示结果
            self.output_text.setText(formatted_output)

        except Exception as e:
            QMessageBox.critical(self, '错误', f'转换失败: {str(e)}')

    def copy_output(self):
        """复制输出结果到剪贴板"""
        output = self.output_text.toPlainText()
        if output:
            clipboard = QApplication.clipboard()
            clipboard.setText(output)
            QMessageBox.information(self, '提示', '已复制到剪贴板')
        else:
            QMessageBox.warning(self, '警告', '没有可复制的内容')

    def clear_all(self):
        """清除所有内容"""
        self.input_text.clear()
        self.output_text.clear()


def main():
    app = QApplication(sys.argv)

    # 设置应用样式
    app.setStyle('Fusion')

    window = SwiftConverterUI()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
