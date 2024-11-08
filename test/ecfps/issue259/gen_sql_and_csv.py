import csv
import random
import string
from datetime import datetime, date, timedelta

# 在脚本开始处添加这个变量
start_proxy_id = 1000079000000

# Generate data
num_records = 50000


def generate_random_string(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def generate_random_date(start_date, end_date):
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    return start_date + timedelta(days=random_number_of_days)


def generate_data(num_records):
    records = []
    global start_proxy_id
    for _ in range(num_records):
        # icl_file_date = generate_random_date(date(2020, 1, 1), date.today())
        icl_file_date = date.today()
        icl_file_name = f"ICL_FILE_{generate_random_string(10)}.txt"
        # corp_type = random.choice(['MRCH', 'CORP', 'GOVT', 'NORP'])
        corp_type = random.choice(['MRCH'])
        agent_cd = random.choice(['003', '004'])
        cust_id = f"F{generate_random_string(20)}"
        proxy_id = str(start_proxy_id)
        start_proxy_id += 1  # 每次递增 1
        proxy_id_type = random.choice(['EMAL', 'MOBN', 'SVID'])
        cust_name_en = f"Customer {generate_random_string(10)}"
        displayed_cust_name_en = f"Displayed {cust_name_en}"
        cust_name_zh = f"客户 {generate_random_string(5)}"
        displayed_cust_name_zh = f"显示 {cust_name_zh}"
        location = f"Location {generate_random_string(8)}"
        is_support_edda = random.choice([0, 1])
        is_simplified_edda = random.choice([0, 1])
        is_support_rtop = random.choice([0, 1])
        is_bank_acct_validation = random.choice([0, 1])
        is_realtime_payment_only = random.choice([0, 1])
        merchant_category = generate_random_string(4).upper()
        merchant_type = f"{random.randint(1000, 9999)}"
        merchant_name = f"Merchant {generate_random_string(10)}"
        merchant_narrative = f"Narrative for {merchant_name}"
        risk_level = random.choice(['L', 'M', 'H'])
        legal_entity_id = generate_random_string(10)
        bank_acct_ids = ','.join([generate_random_string(10) for _ in range(3)])
        # status = random.choice(['A', 'I', 'P'])
        # status = random.choice(['I'])
        # status = random.choice(['A'])
        status = random.choice(['P'])
        # status = random.choice(['A','P'])

        records.append({
            'ICL_FILE_DATE': icl_file_date,
            'ICL_FILE_NAME': icl_file_name,
            'CORP_TYPE': corp_type,
            'AGENT_CD': agent_cd,
            'CUST_ID': cust_id,
            'PROXY_ID': proxy_id,
            'PROXY_ID_TYPE': proxy_id_type,
            'CUST_NAME_EN': cust_name_en,
            'DISPLAYED_CUST_NAME_EN': displayed_cust_name_en,
            'CUST_NAME_ZH': cust_name_zh,
            'DISPLAYED_CUST_NAME_ZH': displayed_cust_name_zh,
            'LOCATION': location,
            'IS_SUPPORT_EDDA': is_support_edda,
            'IS_SIMPLIFIED_EDDA': is_simplified_edda,
            'IS_SUPPORT_RTOP': is_support_rtop,
            'IS_BANK_ACCT_VALIDATION': is_bank_acct_validation,
            'IS_REALTIME_PAYMENT_ONLY': is_realtime_payment_only,
            'MERCHANT_CATEGORY': merchant_category,
            'MERCHANT_TYPE': merchant_type,
            'MERCHANT_NAME': merchant_name,
            'MERCHANT_NARRATIVE': merchant_narrative,
            'RISK_LEVEL': risk_level,
            'LEGAL_ENTITY_ID': legal_entity_id,
            'BANK_ACCT_IDS': bank_acct_ids,
            'STATUS': status
        })
    return records


import csv
from datetime import date, datetime


def generate_csv(records, filename):
    report_date = date.today()
    report_gen_time = datetime.now()

    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)  # 修改这一行
        # Write header
        writer.writerow(["Report ID", "Report Description", "Report Generation Time", "Reporting Date", "Record Count"])
        writer.writerow(["FPSD6015", "Addressing Merchant List", report_gen_time.strftime("%Y-%m-%d %H:%M:%S"),
                         report_date.strftime("%Y-%m-%d"), len(records)])

        # Write column headers
        writer.writerow([
            "Corporate Type", "Participant Code", "Customer ID", "Proxy Identification", "Proxy Identification Type",
            "Customer Name (English)", "Displayed Customer Name (English)", "Customer Name (Chinese)",
            "Displayed Customer Name (Chinese)",
            "Location", "Supported Option - eDDA & Direct Debit", "Sub-Option - Simplified eDDA",
            "Supported Option - Request to Pay",
            "Sub-Option - Bill Account Number Validation", "Sub-Option - Real-time Payment Only", "Merchant Category",
            "Merchant Type", "Merchant Name", "Merchant Narrative", "Risk Level", "Legal Entity Identifier",
            "Bank Account Numbers"
        ])

        # Write data
        for record in records:
            writer.writerow([
                record['CORP_TYPE'], record['AGENT_CD'], record['CUST_ID'], record['PROXY_ID'], record['PROXY_ID_TYPE'],
                record['CUST_NAME_EN'] + ";updateSuccess", record['DISPLAYED_CUST_NAME_EN'], record['CUST_NAME_ZH'],
                record['DISPLAYED_CUST_NAME_ZH'],
                record['LOCATION'], 'Y' if record['IS_SUPPORT_EDDA'] else 'N',
                'Y' if record['IS_SIMPLIFIED_EDDA'] else 'N',
                'Y' if record['IS_SUPPORT_RTOP'] else 'N', 'Y' if record['IS_BANK_ACCT_VALIDATION'] else 'N',
                'Y' if record['IS_REALTIME_PAYMENT_ONLY'] else 'N', record['MERCHANT_CATEGORY'],
                record['MERCHANT_TYPE'], record['MERCHANT_NAME'], record['MERCHANT_NARRATIVE'], record['RISK_LEVEL'],
                record['LEGAL_ENTITY_ID'], record['BANK_ACCT_IDS']
            ])


def generate_sql(records, filename):
    batch_size = 1000  # 每批插入的最大行数

    with open(filename, 'w', encoding='utf-8') as sqlfile:
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]

            # 写入INSERT语句的开头部分
            sqlfile.write("""
INSERT INTO ECFPS_ADR_MERCHANT_TBL (
    ICL_FILE_DATE, ICL_FILE_NAME, CORP_TYPE, AGENT_CD, CUST_ID, PROXY_ID, PROXY_ID_TYPE,
    CUST_NAME_EN, DISPLAYED_CUST_NAME_EN, CUST_NAME_ZH, DISPLAYED_CUST_NAME_ZH, LOCATION,
    IS_SUPPORT_EDDA, IS_SIMPLIFIED_EDDA, IS_SUPPORT_RTOP, IS_BANK_ACCT_VALIDATION,
    IS_REALTIME_PAYMENT_ONLY, MERCHANT_CATEGORY, MERCHANT_TYPE, MERCHANT_NAME,
    MERCHANT_NARRATIVE, RISK_LEVEL, LEGAL_ENTITY_ID, BANK_ACCT_IDS, STATUS
) VALUES
""")

            # 批量写入值
            for j, record in enumerate(batch):
                values = f"""(
    '{record['ICL_FILE_DATE']}', '{record['ICL_FILE_NAME']}', '{record['CORP_TYPE']}', '{record['AGENT_CD']}',
    '{record['CUST_ID']}', '{record['PROXY_ID']}', '{record['PROXY_ID_TYPE']}', '{record['CUST_NAME_EN']}',
    '{record['DISPLAYED_CUST_NAME_EN']}', N'{record['CUST_NAME_ZH']}', N'{record['DISPLAYED_CUST_NAME_ZH']}',
    '{record['LOCATION']}', {record['IS_SUPPORT_EDDA']}, {record['IS_SIMPLIFIED_EDDA']},
    {record['IS_SUPPORT_RTOP']}, {record['IS_BANK_ACCT_VALIDATION']}, {record['IS_REALTIME_PAYMENT_ONLY']},
    '{record['MERCHANT_CATEGORY']}', '{record['MERCHANT_TYPE']}', '{record['MERCHANT_NAME']}',
    '{record['MERCHANT_NARRATIVE']}', '{record['RISK_LEVEL']}', '{record['LEGAL_ENTITY_ID']}',
    '{record['BANK_ACCT_IDS']}', '{record['STATUS']}'
)"""
                if j < len(batch) - 1:
                    values += ','
                else:
                    values += ';'
                sqlfile.write(values + '\n')

            # 每个批次后添加一个空行，提高可读性
            sqlfile.write('\n')


if __name__ == '__main__':
    records = generate_data(num_records)

    # Generate CSV
    generate_csv(records, 'merchant_data.csv')

    # Generate SQL
    generate_sql(records, 'insert_statements-50000P.sql')

    print(f"{num_records} records have been generated.")
    print("CSV file 'merchant_data.csv' and SQL file 'insert_statements-50000A.sql' have been created.")
