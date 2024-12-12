from PyQt6.QtCore import QDateTime
from dataclasses import dataclass
from typing import List, Dict, Any
import json

@dataclass
class ConversionRecord:
    """转换记录类，用于存储每次转换的详细信息"""
    timestamp: QDateTime      # 转换时间戳
    conv_type: str           # 转换类型
    input_msg: str          # 输入的原始内容
    output_msg: str         # 转换后的内容
    process_info: List[str]  # 处理过程中的信息（如警告、错误等）

    def __init__(self, timestamp: QDateTime, conv_type: str, input_msg: str,
                 output_msg: str, process_info: List[str]):
        self.timestamp = timestamp
        self.conv_type = conv_type
        self.input_msg = input_msg
        self.output_msg = output_msg
        self.process_info = process_info

    def to_dict(self) -> Dict[str, Any]:
        """将记录转换为字典格式，用于 JSON 序列化"""
        return {
            'timestamp': self.timestamp.toString('yyyy-MM-dd hh:mm:ss'),
            'conv_type': self.conv_type,
            'input_msg': self.input_msg,
            'output_msg': self.output_msg,
            'process_info': self.process_info
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversionRecord':
        """从字典创建记录对象，用于从 JSON 反序列化"""
        return cls(
            timestamp=QDateTime.fromString(data['timestamp'], 'yyyy-MM-dd hh:mm:ss'),
            conv_type=data['conv_type'],
            input_msg=data['input_msg'],
            output_msg=data['output_msg'],
            process_info=data['process_info']
        )

    def __str__(self) -> str:
        """返回记录的字符串表示"""
        return (f"[{self.timestamp.toString('yyyy-MM-dd hh:mm:ss')}] "
                f"{self.conv_type}: {self.input_msg[:30]}...")

    def __lt__(self, other: 'ConversionRecord') -> bool:
        """用于排序，按时间戳比较"""
        return self.timestamp < other.timestamp
