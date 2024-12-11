import sys
import json
import requests
import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QTextEdit, QPushButton, QLabel,
                             QMessageBox, QSplitter, QLineEdit, QFileDialog)
from PyQt6.QtCore import Qt
import xml.dom.minidom
import os


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
        main_layout = QVBoxLayout(main_widget)

        # 创建输入输出文本区域
        text_widget = QWidget()
        text_layout = QHBoxLayout(text_widget)

        # 左侧输入区域
        input_layout = QVBoxLayout()
        input_label = QLabel('输入SWIFT报文:')
        self.input_text = QTextEdit()
        input_layout.addWidget(input_label)
        input_layout.addWidget(self.input_text)
        text_layout.addLayout(input_layout)

        # 右侧输出区域
        output_layout = QVBoxLayout()
        output_label = QLabel('转换结果:')
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_text)
        text_layout.addLayout(output_layout)

        main_layout.addWidget(text_widget)

        # 添加按钮区域
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)

        # MT转MX按钮
        mt_to_mx_btn = QPushButton('MT → MX')
        mt_to_mx_btn.clicked.connect(lambda: self.convert('mt2mx'))
        button_layout.addWidget(mt_to_mx_btn)

        # MX转MT按钮
        mx_to_mt_btn = QPushButton('MX → MT')
        mx_to_mt_btn.clicked.connect(lambda: self.convert('mx2mt'))
        button_layout.addWidget(mx_to_mt_btn)

        # 清空按钮
        clear_btn = QPushButton('清空')
        clear_btn.clicked.connect(self.clear_text)
        button_layout.addWidget(clear_btn)

        # 复制按钮
        copy_btn = QPushButton('复制结果')
        copy_btn.clicked.connect(self.copy_result)
        button_layout.addWidget(copy_btn)

        main_layout.addWidget(button_widget)

        # 添加报告生成区域（使用PyQt6控件）
        report_widget = QWidget()
        report_layout = QVBoxLayout(report_widget)

        # 文件名输入框
        filename_layout = QHBoxLayout()
        filename_layout.addWidget(QLabel('文件名:'))
        self.filename_input = QLineEdit()
        self.filename_input.setText('conversion_report.txt')
        filename_layout.addWidget(self.filename_input)
        report_layout.addLayout(filename_layout)

        # 路径输入框和选择按钮
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel('保存路径:'))
        self.path_input = QLineEdit()
        self.path_input.setText(os.path.expanduser('~'))
        path_layout.addWidget(self.path_input)

        choose_path_btn = QPushButton('选择...')
        choose_path_btn.clicked.connect(self.choose_directory)
        path_layout.addWidget(choose_path_btn)
        report_layout.addLayout(path_layout)

        # 生成报告按钮
        generate_btn = QPushButton('生成转换报告')
        generate_btn.clicked.connect(self.generate_report)
        report_layout.addWidget(generate_btn)

        main_layout.addWidget(report_widget)

    def convert_text(self):
        """转换SWIFT报文"""
        input_text = self.input_text.toPlainText()
        if not input_text:
            QMessageBox.warning(self, '警告', '请输入需要转换的SWIFT报文')
            return

        # TODO: 这里添加实际的转换逻辑
        converted_text = input_text  # 临时示例，实际需要替换为真实的转换逻辑
        self.output_text.setText(converted_text)

    def clear_text(self):
        """清空输入输出文本框"""
        self.input_text.clear()
        self.output_text.clear()

    def copy_result(self):
        """复制转换结果到剪贴板"""
        result = self.output_text.toPlainText()
        if result:
            clipboard = QApplication.clipboard()
            clipboard.setText(result)
            QMessageBox.information(self, '提示', '结果已复制到剪贴板')
        else:
            QMessageBox.warning(self, '警告', '没有可复制的内容')

    def choose_directory(self):
        directory = QFileDialog.getExistingDirectory(
            self,
            "选择保存目录",
            self.path_input.text(),
            QFileDialog.Option.ShowDirsOnly
        )
        if directory:
            self.path_input.setText(directory)

    def generate_report(self):
        try:
            filename = self.filename_input.text()
            path = self.path_input.text()

            # 确保文件名有.txt后缀
            if not filename.endswith('.txt'):
                filename += '.txt'

            # 完整文件路径
            full_path = os.path.join(path, filename)

            # 生成报告内容
            report_content = f"""SWIFT报文转换报告
生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'=' * 50}

原始MT报文:
{self.input_text.toPlainText().strip()}

{'=' * 50}

转换后的MX报文:
{self.output_text.toPlainText().strip()}

{'=' * 50}
"""

            # 写入文件
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(report_content)

            QMessageBox.information(self, "成功", f"报告已生成：\n{full_path}")

        except Exception as e:
            QMessageBox.critical(self, "错误", f"生成报告时发生错误：\n{str(e)}")

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
