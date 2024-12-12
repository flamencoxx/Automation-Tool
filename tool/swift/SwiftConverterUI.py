import re
import sys
import json
import requests
import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QTextEdit, QPushButton, QLabel,
                             QMessageBox, QSplitter, QLineEdit, QFileDialog,
                             QTextBrowser, QListWidgetItem, QListWidget)  # 添加 QTextBrowser
from PyQt6.QtCore import Qt, QDateTime
import xml.dom.minidom
import os

from tool.swift.ConversionRecord import ConversionRecord


class SwiftConverterUI(QMainWindow):
    RECORDS_PER_PAGE = 50  # 每页显示的记录数
    def __init__(self):
        super().__init__()
        self.current_page = 1
        self.total_pages = 1
        self.conversion_history = []
        self.initUI()
        self.load_history()

    def initUI(self):
        # 设置窗口基本属性
        self.setWindowTitle('SWIFT报文转换工具')
        self.setGeometry(100, 100, 1200, 800)

        # 创建主widget和布局
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        # 创建按钮区域
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

        # 创建中央区域的水平布局
        central_widget = QWidget()
        central_layout = QHBoxLayout(central_widget)

        # 创建左侧文本区域
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        # 原始报文输入区域
        input_label = QLabel('输入SWIFT报文:')
        self.input_text = QTextEdit()
        left_layout.addWidget(input_label)
        left_layout.addWidget(self.input_text)

        # 添加 Additional Data 输入区域
        additional_label = QLabel('Additional Data (可选):')
        self.additional_data_input = QTextEdit()
        self.additional_data_input.setMaximumHeight(100)  # 限制高度
        self.additional_data_input.setPlaceholderText("在此输入额外参数...")
        left_layout.addWidget(additional_label)
        left_layout.addWidget(self.additional_data_input)

        central_layout.addWidget(left_widget)

        # 创建中间文本区域
        middle_widget = QWidget()
        middle_layout = QVBoxLayout(middle_widget)
        output_label = QLabel('转换结果:')
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        middle_layout.addWidget(output_label)
        middle_layout.addWidget(self.output_text)
        central_layout.addWidget(middle_widget)

        # 创建右侧区域
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_widget.setMaximumWidth(300)

        # 右侧上方（处理信息区域）
        error_label = QLabel('处理信息:')
        self.error_text = QTextEdit()
        self.error_text.setReadOnly(True)
        self.error_text.setMaximumHeight(200)
        right_layout.addWidget(error_label)
        right_layout.addWidget(self.error_text)

        # 修改历史记录区域的布局
        history_widget = QWidget()
        history_layout = QVBoxLayout(history_widget)

        history_label = QLabel('历史记录:')
        history_layout.addWidget(history_label)

        # 历史记录文本区域
        # 改为：
        self.history_list = QListWidget()
        self.history_list.setStyleSheet("""
            QListWidget {
                background-color: #2b2b2b;
                border: none;
                outline: none;
            }
            QListWidget::item {
                background-color: #3c3f41;
                border: 1px solid #2b2b2b;
                border-radius: 4px;
                color: #bbbbbb;
                padding: 8px 12px;
                margin: 4px 8px;
            }
            QListWidget::item:hover {
                background-color: #4c5052;
                border: 1px solid #5c6366;
            }
            QListWidget::item:selected {
                background-color: #4b6eaf;
                border: 1px solid #5c84cc;
            }
        """)
        self.history_list.itemClicked.connect(self.on_history_item_clicked)
        history_layout.addWidget(self.history_list)

        # 分页控制区域
        pagination_widget = QWidget()
        pagination_layout = QHBoxLayout(pagination_widget)

        self.prev_page_btn = QPushButton('上一页')
        self.prev_page_btn.clicked.connect(self.prev_page)
        self.next_page_btn = QPushButton('下一页')
        self.next_page_btn.clicked.connect(self.next_page)
        self.page_info_label = QLabel('第 1 页')

        pagination_layout.addWidget(self.prev_page_btn)
        pagination_layout.addWidget(self.page_info_label)
        pagination_layout.addWidget(self.next_page_btn)

        history_layout.addWidget(pagination_widget)

        # 将整个历史记录区域添加到主布局
        right_layout.addWidget(history_widget)

        central_layout.addWidget(right_widget)

        # 设置比例
        central_layout.setStretch(0, 2)  # 左侧占2
        central_layout.setStretch(1, 2)  # 中间占2
        central_layout.setStretch(2, 1)  # 右侧占1

        main_layout.addWidget(central_widget)

        # 添加报告生成区域
        report_widget = QWidget()
        report_layout = QVBoxLayout(report_widget)

        # 文件名输入框
        filename_layout = QHBoxLayout()
        filename_layout.addWidget(QLabel('文件名:'))
        self.filename_input = QLineEdit()
        self.filename_input.setText('conversion_report.txt')
        filename_layout.addWidget(self.filename_input)

        # 添加生成文件名按钮
        self.generate_filename_btn = QPushButton("生成文件名")
        self.generate_filename_btn.clicked.connect(self.generate_filename)
        filename_layout.addWidget(self.generate_filename_btn)

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

    def on_history_item_clicked(self, item):
        """处理历史记录项点击事件"""
        record = item.data(Qt.ItemDataRole.UserRole)
        if record:
            # 显示历史记录的详细信息
            self.input_text.setText(record.input_msg)
            self.output_text.setText(record.output_msg)
            self.error_text.clear()
            for info in record.process_info:
                self.error_text.append(info)
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

            if not filename.endswith('.txt'):
                filename += '.txt'

            full_path = os.path.join(path, filename)

            # 更新报告内容格式
            report_content = f"""SWIFT报文转换报告
    转换类型: {getattr(self, 'conversion_type', 'Unknown')}
    生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    {'=' * 50}

    原始报文:
    {self.input_text.toPlainText().strip()}

    {'=' * 50}

    处理信息:
    {chr(10).join(getattr(self, 'process_info', ['无处理信息']))}

    {'=' * 50}

    转换结果:
    {self.output_text.toPlainText().strip()}

    {'=' * 50}
    """

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
        additional_data = self.additional_data_input.toPlainText().strip()
        if additional_data:
            additional_data_formatted = '{' + additional_data + '}'
        else:
            additional_data_formatted = None
        if not input_text:
            QMessageBox.warning(self, '警告', '请输入需要转换的报文')
            return

        # 清空处理信息和输出
        self.error_text.clear()
        self.output_text.clear()

        # 用于生成报告的完整信息
        self.process_info = []
        self.conversion_type = 'MT → MX' if conv_type == 'mt2mx' else 'MX → MT'

        try:
            endpoint = 'convertMtToMx' if conv_type == 'mt2mx' else 'convertMxMessageToMtMessage'
            url = f'http://localhost:8080/mcg/{endpoint}'

            # 构建请求体
            request_body = {
                'originalMsg': input_text,
                'additionalData': additional_data_formatted
            }

            # 界面只显示简洁信息
            start_msg = f"开始{self.conversion_type}转换..."
            self.error_text.append(start_msg)

            # 报告保存详细信息
            self.process_info.append(start_msg)
            self.process_info.append("\n=== 请求信息 ===")
            self.process_info.append(f"URL: {url}")
            self.process_info.append("Request Body:")
            self.process_info.append(json.dumps(request_body, indent=2, ensure_ascii=False))

            # 发送请求
            response = requests.post(
                url,
                headers={'Content-Type': 'application/json'},
                json=request_body
            )

            response.raise_for_status()
            result = response.json()

            # 保存响应信息到报告
            self.process_info.append("\n=== 响应信息 ===")
            self.process_info.append(json.dumps(result, indent=2, ensure_ascii=False))

            # MT → MX 转换处理
            if conv_type == 'mt2mx':
                if result['status'] == 'Success':
                    converted_msg = result['data']['convertedMsg']
                    # 提取报文类型
                    msg_type = self.extract_message_info().get('msg_type', '')
                    self.error_text.append(f"转换类型: {msg_type if msg_type else 'Unknown'}")

                    # 处理转换问题
                    if result['data']['conversionIssues']:
                        issue_msg = "\n转换问题:"
                        self.error_text.append(issue_msg)
                        self.process_info.append(issue_msg)
                        for issue in result['data']['conversionIssues']:
                            issue_str = f"- {str(issue)}"
                            self.error_text.append(issue_str)
                            self.process_info.append(issue_str)
                else:
                    raise Exception('转换失败：状态不是Success')

            # MX → MT 转换处理
            else:
                converted_msg = result['translatedMTMessage']
                # 检查转换结果
                if result['translationResult'] in ['TROK', 'TRAK']:
                    if result['errors']:
                        error_msg = "\n转换问题:"
                        self.error_text.append(error_msg)
                        self.process_info.append(error_msg)
                        for error in result['errors']:
                            error_detail = f"- {error.get('message', '未知错误')}"
                            self.error_text.append(error_detail)
                            self.process_info.append(error_detail)
                else:
                    raise Exception('转换失败：translationResult 既不是 TROK 也不是 TRAK')

            # 格式化输出并显示
            formatted_output = (self.format_xml(converted_msg)
                                if conv_type == 'mt2mx'
                                else self.format_mt(converted_msg))

            complete_msg = "\n转换完成"
            self.error_text.append(complete_msg)
            self.process_info.append(complete_msg)
            self.output_text.setText(formatted_output)

            # 创建新的转换记录
            new_record = ConversionRecord(
                timestamp=QDateTime.currentDateTime(),
                conv_type=self.conversion_type,
                input_msg=input_text,
                output_msg=formatted_output,
                process_info=self.process_info
            )
            self.conversion_history.append(new_record)

            # 保存历史记录
            self.save_history_to_file()

            # 更新显示
            self.update_history_display()

        except Exception as e:
            error_msg = f'转换失败: {str(e)}'
            self.error_text.append(error_msg)
            self.process_info.append(error_msg)
            QMessageBox.critical(self, '错误', error_msg)

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

    def extract_message_info(self):
        """从报文中提取信息"""
        info = {}
        input_text = self.input_text.toPlainText()

        try:
            if '{1:F01' in input_text:  # MT报文
                # 提取MT报文类型 - 考虑输入和输出报文格式
                mt_type_match = re.search(r'{2:[IO](\d{3})', input_text)
                if mt_type_match:
                    info['msg_type'] = f'MT{mt_type_match.group(1)}'

                # 可选：尝试提取金额信息（考虑多种可能的字段）
                amount_match = None
                for field in [':32A:', ':32B:', ':33B:', ':19A:']:
                    amount_match = re.search(f'{field}([A-Z]{{3}})(\d+)', input_text)
                    if amount_match:
                        info['amount_ccy'] = f"{amount_match.group(1)}{amount_match.group(2)}"
                        break

            else:  # MX报文
                # 优先使用 MsgDefIdr 提取报文类型（保留完整版本信息）
                msg_def_match = re.search(r'<MsgDefIdr>([^<]+)</MsgDefIdr>', input_text)
                if msg_def_match:
                    # 保留完整的报文类型，例如 camt.057.001.06
                    info['msg_type'] = msg_def_match.group(1)

                # 备选方案1：从 Document 标签提取
                elif '<Document' in input_text:
                    doc_match = re.search(r'<Document xmlns="[^"]*?:(\w+\.\d{3}\.\d{3}\.\d{2})', input_text)
                    if doc_match:
                        info['msg_type'] = doc_match.group(1)

                # 备选方案2：从 xmlns URI 提取
                else:
                    xmlns_match = re.search(r'xmlns="urn:iso:std:iso:20022:tech:xsd:(\w+\.\d{3}\.\d{3}\.\d{2})',
                                            input_text)
                    if xmlns_match:
                        info['msg_type'] = xmlns_match.group(1)

        except Exception as e:
            print(f"提取报文信息时发生错误: {str(e)}")

        return info

    def generate_filename(self):
        """生成文件名"""
        current_time = QDateTime.currentDateTime()
        timestamp = current_time.toString('yyyyMMdd_HHmmss')

        # 获取转换类型
        conv_type = 'MT2MX' if self.conversion_type == 'MT → MX' else 'MX2MT'

        # 提取报文信息
        msg_info = self.extract_message_info()

        # 构建文件名基础部分（必需信息）
        filename_parts = [
            conv_type,  # 转换类型
            msg_info.get('msg_type', ''),  # 报文类型
            timestamp,  # 时间戳
        ]

        # 添加可选信息（如果存在）
        if 'amount_ccy' in msg_info:
            filename_parts.append(msg_info['amount_ccy'])

        # 过滤掉空字符串，并用下划线连接
        filename = '_'.join(filter(None, filename_parts)) + '.txt'

        # 更新文件名输入框
        self.filename_input.setText(filename)

    def get_history_folder_path(self):
        """获取历史记录文件夹路径"""
        # 在程序目录下创建 history_records 文件夹
        base_path = os.path.dirname(os.path.abspath(__file__))
        history_path = os.path.join(base_path, 'history_records')
        if not os.path.exists(history_path):
            os.makedirs(history_path)
        return history_path

    def get_current_history_file(self):
        """获取当前月份的历史记录文件路径"""
        current_date = QDateTime.currentDateTime()
        filename = f"history_{current_date.toString('yyyy_MM')}.json"
        return os.path.join(self.get_history_folder_path(), filename)

    def update_history_display(self):
        """更新历史记录显示"""
        # 替换原来的 history_text 为新的 history_list
        self.history_list.clear()

        if not self.conversion_history:
            self.page_info_label.setText('第 1 页 / 共 0 页')
            return

        start_idx = (self.current_page - 1) * self.RECORDS_PER_PAGE
        end_idx = start_idx + self.RECORDS_PER_PAGE
        current_records = self.conversion_history[start_idx:end_idx]

        for record in current_records:
            item = QListWidgetItem(
                f'[{record.timestamp.toString("yyyy-MM-dd hh:mm:ss")}] {record.conv_type}'
            )
            item.setData(Qt.ItemDataRole.UserRole, record) # 存储完整记录数据
            self.history_list.addItem(item)

        # 更新分页信息
        self.total_pages = max(1, (len(self.conversion_history) + self.RECORDS_PER_PAGE - 1) // self.RECORDS_PER_PAGE)
        self.page_info_label.setText(f'第 {self.current_page} 页 / 共 {self.total_pages} 页')

        # 更新按钮状态
        self.prev_page_btn.setEnabled(self.current_page > 1)
        self.next_page_btn.setEnabled(self.current_page < self.total_pages)

    def prev_page(self):
        """显示上一页"""
        if self.current_page > 1:
            self.current_page -= 1
            self.update_history_display()

    def next_page(self):
        """显示下一页"""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.update_history_display()

    def save_history_to_file(self):
        """保存历史记录到当前月份的文件"""
        try:
            current_file = self.get_current_history_file()
            history_data = []

            # 将当前月份的记录转换为字典格式
            current_date = QDateTime.currentDateTime()
            for record in self.conversion_history:
                record_date = record.timestamp
                if (record_date.date().year() == current_date.date().year() and
                        record_date.date().month() == current_date.date().month()):
                    history_data.append({
                        'timestamp': record.timestamp.toString(Qt.DateFormat.ISODate),
                        'conv_type': record.conv_type,
                        'input_msg': record.input_msg,
                        'output_msg': record.output_msg,
                        'process_info': record.process_info
                    })

            # 确保目录存在
            os.makedirs(os.path.dirname(current_file), exist_ok=True)

            # 写入文件
            with open(current_file, 'w', encoding='utf-8') as f:
                json.dump(history_data, f, ensure_ascii=False, indent=2)

            print(f"历史记录已保存到: {current_file}")

        except Exception as e:
            print(f"保存历史记录失败: {str(e)}")
            import traceback
            traceback.print_exc()

    def load_history(self):
        """加载所有历史记录"""
        try:
            self.conversion_history.clear()
            history_folder = self.get_history_folder_path()

            # 获取所有历史记录文件
            history_files = [f for f in os.listdir(history_folder) if f.startswith('history_') and f.endswith('.json')]

            # 按时间顺序排序文件
            history_files.sort(reverse=True)

            # 加载所有文件的记录
            for file in history_files:
                file_path = os.path.join(history_folder, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    history_data = json.load(f)

                    for data in history_data:
                        record = ConversionRecord(
                            timestamp=QDateTime.fromString(data['timestamp'], Qt.DateFormat.ISODate),
                            conv_type=data['conv_type'],
                            input_msg=data['input_msg'],
                            output_msg=data['output_msg'],
                            process_info=data['process_info']
                        )
                        self.conversion_history.append(record)

            # 按时间倒序排序记录
            self.conversion_history.sort(key=lambda x: x.timestamp, reverse=True)

            # 更新显示
            self.current_page = 1
            self.update_history_display()

        except Exception as e:
            print(f"加载历史记录失败: {str(e)}")





def main():
    app = QApplication(sys.argv)

    # 设置应用样式
    app.setStyle('Fusion')

    window = SwiftConverterUI()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
