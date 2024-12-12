from PyQt5.QtWidgets import QListWidget, QListWidgetItem
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt


class HistoryListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 设置样式表
        self.setStyleSheet("""
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
        self.setSpacing(2)  # 设置项目间距


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
        item.setData(Qt.ItemDataRole.UserRole, record)  # 存储完整记录数据
        self.history_list.addItem(item)

    # 更新分页信息
    self.total_pages = max(1, (len(self.conversion_history) + self.RECORDS_PER_PAGE - 1) // self.RECORDS_PER_PAGE)
    self.page_info_label.setText(f'第 {self.current_page} 页 / 共 {self.total_pages} 页')

    # 更新按钮状态
    self.prev_page_btn.setEnabled(self.current_page > 1)
    self.next_page_btn.setEnabled(self.current_page < self.total_pages)
