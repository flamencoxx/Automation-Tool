import pandas as pd

# 创建MT101到pain.001.001.09的映射数据
data = {
    'MT101 Tag': [
        ':20:',
        ':21:',
        ':28D:',
        ':50H:/:50L:',
        ':52A:',
        ':30:',
        ':21R:',
        ':23E:',
        ':32B:',
        ':50a:',
        ':57a:',
        ':59a:',
        ':70:',
        ':71A:',
        ':71F:',
        ':77B:'
    ],
    'MT101 Name': [
        'Sender\'s Reference',
        'Related Reference',
        'Message Index/Total',
        'Ordering Customer',
        'Account Servicing Institution',
        'Requested Execution Date',
        'Customer Specified Reference',
        'Instruction Code',
        'Transaction Amount',
        'Ordering Customer',
        'Account With Institution',
        'Beneficiary',
        'Remittance Information',
        'Details of Charges',
        'Sender\'s Charges',
        'Regulatory Reporting'
    ],
    'pain.001.001.09 XML Path': [
        'GrpHdr/MsgId',
        'PmtInf/PmtInfId',
        'N/A',
        'PmtInf/Dbtr',
        'PmtInf/DbtrAgt',
        'PmtInf/ReqdExctnDt',
        'PmtInf/PmtInfId',
        'CdtTrfTxInf/InstrForDbtrAgt',
        'CdtTrfTxInf/Amt/InstdAmt',
        'PmtInf/Dbtr',
        'CdtTrfTxInf/CdtrAgt',
        'CdtTrfTxInf/Cdtr',
        'CdtTrfTxInf/RmtInf',
        'CdtTrfTxInf/ChrgBr',
        'CdtTrfTxInf/ChrgsInf',
        'CdtTrfTxInf/RgltryRptg'
    ],
    'Mandatory': [
        'M',
        'O',
        'M',
        'M',
        'O',
        'M',
        'O',
        'O',
        'M',
        'M',
        'O',
        'M',
        'O',
        'M',
        'O',
        'O'
    ],
    'Format': [
        '16x',
        '16x',
        '5n/5n',
        '格式见SWIFT标准',
        'BIC',
        'YYYYMMDD',
        '16x',
        '4!c/30x',
        '3!a15d',
        '格式见SWIFT标准',
        'BIC/清算代码',
        '格式见SWIFT标准',
        '4*35x',
        'OUR/SHA/BEN',
        '3!a15d',
        '3*35x'
    ]
}

# 创建DataFrame
df = pd.DataFrame(data)

# 设置表格样式
pd.set_option('display.max_colwidth', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', None)

if __name__ == '__main__':
    print(df.to_string(index=False))
