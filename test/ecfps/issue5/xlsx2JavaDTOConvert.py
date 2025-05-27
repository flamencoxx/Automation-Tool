import openpyxl
from dataclasses import dataclass
from typing import List, Dict, Optional
import re


@dataclass
class ExcelConfig:
    """Excel读取配置"""
    file_path: str
    header_row: int = 25
    data_start_row: int = 26  # 数据起始行
    data_end_row: Optional[int] = None  # 数据结束行(不指定则读取所有)
    column_map: Dict[str, int] = None  # 列定义映射


@dataclass
class FieldConfig:
    """字段生成配置"""
    processors: List[str]  # 要启用的处理器名称
    type_mapping: Dict[str, str] = None  # 类型映射规则


class DTOGenerator:
    def __init__(self, excel_config: ExcelConfig, field_config: FieldConfig):
        self.excel_config = excel_config
        self.field_config = field_config
        self._init_processors()

    def _init_processors(self):
        """内置处理器集合"""
        self.processors = {
            "camel_case": lambda v: re.sub(
                r'_([a-z])',
                lambda m: m.group(1).upper(),
                str(v).lower()
            ),
            "length_anno": lambda v: f"@Size(max = {v})" if str(v).isdigit() else "",
            "type_anno": lambda t: f"private {self.field_config.type_mapping.get(t, 'String')} ",
            "comment": lambda d: f"/** {d} */" if d else ""
        }

    def generate(self) -> List[str]:
        """核心生成逻辑"""
        wb = openpyxl.load_workbook(self.excel_config.file_path)
        sheet = wb.active

        # 读取配置范围内的数据行
        rows = list(sheet.iter_rows(
            min_row=self.excel_config.data_start_row,
            max_row=self.excel_config.data_end_row or sheet.max_row
        ))

        # 提取每行字段数据
        return [
            self._process_field({
                "name": row[0].value,  # Field Name
                "type": row[2].value,  # Format (Output Interface)
                "length": row[5].value,  # Length
                "desc": row[1].value  # Description
            })
            for row in rows if row[0].value  # 跳过空字段名
        ]

    def _process_field(self, field: Dict) -> str:
        """处理单个字段"""
        lines = []
        for processor_name in self.field_config.processors:
            if result := self.processors[processor_name](field.get(processor_name[0], "")):
                lines.append(result)

        return (
            f"{lines[0] if lines else ''}\n"
            f"{lines[1] if len(lines) > 1 else ''}"
            f"{self.processors['type_anno'](field['type'])}"
            f"{self.processors['camel_case'](field['name'])};\n"
        )


# 使用示例
if __name__ == "__main__":
    # 1. 配置Excel读取规则
    excel_config = ExcelConfig(
        file_path="C:\\Users\\admin\\OneDrive\\WORK\\ecfps_doc\\\mainland-crossboard\\SCB\\ISSUE-5\\FPDWPPD_v2.40_20241028.xlsx",
        header_row=25,  # 列名在第25行
        data_start_row=26,  # 数据从26行开始
        data_end_row=1400,  # 读取到1400行
        column_map={
            "name": 0,  # A列: Field Name
            "desc": 1,  # B列: Description
            "type": 2,  # C列: Format (Output)
            "length": 5  # F列: Length
        }
    )

    # 2. 配置字段处理流程
    field_config = FieldConfig(
        processors=["comment", "length_anno"],  # 需要启用的处理器
        type_mapping={
            "CHAR": "String",
            "VARCHAR": "String",
            "NUMERIC": "BigDecimal",
            "DATE": "LocalDate",
            "TIMESTAMP": "LocalDateTime"
        }
    )

    # 3. 执行生成
    generator = DTOGenerator(excel_config, field_config)
    fields = generator.generate()

    # 4. 输出结果（可直接粘贴到IDE）
    with open("RemittanceFields.java", "w", encoding="utf-8") as f:
        f.write("\n".join(fields))
    print(f"生成完成，共处理 {len(fields)} 个字段")
