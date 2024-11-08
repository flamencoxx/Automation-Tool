import csv
import random
import time
from datetime import datetime, timedelta
import uuid

# 配置
NUM_RECORDS = 100000  # 生成的记录数
START_ID = 14000000  # ID的起始值
INCREMENT_STEP = 1  # ID的递增步长
START_CLIENT_REQ_ID = 3000800000  # CLIENT_REQ_ID 的起始值
CLIENT_REQ_ID_INCREMENT = 1  # CLIENT_REQ_ID 的递增步长

# constants.py
CREDITOR_AGENT_COLUMN = "Credit Participant"
DEBTOR_AGENT_COLUMN = "Debit Participant"
DEFAULT_CLR_CD = "000"
DEFAULT_TYP = "C"
DEFAULT_BAL_STATUS = 0
DEFAULT_CREDITOR_AGENT = "000"
DEFAULT_DEBTOR_AGENT = "035"

CUST_9 = "TEST-1"
used_fps_reference_numbers = set()

# CSV字段名
CSV_FIELDS = [
    "Record Type", "Transaction Type", "Business Service", "Payment Category Purpose", "FPS Reference Number",
    "Transaction ID", "End-to-end ID", "Instruction ID", "Original FPS Reference Number", "Original Transaction ID",
    "Original End-to-end ID", "Original Instruction ID", "Credit Participant", "Creditor Name", "Creditor ID",
    "Creditor ID Type", "Creditor Account Number", "Creditor Account Number Type", "Debit Participant", "Debtor Name",
    "Debtor ID", "Debtor ID Type", "Debtor Account Number", "Debtor Account Number Type", "Currency",
    "Settlement Amount",
    "Status", "Settlement / End of Life Time", "Settlement Sequence", "Reject Code", "Reject Reason Description",
    "Return Code", "Return Reason Description", "Outward Input Source", "Outward File Name/Message Id",
    "Inward Delivery Channel", "Inward File Name/Message Id", "Real-time Counterparty Verification",
    "Counterparty Verification Turnaround Time", "Timeout Indicator"
]

# 表字段名（基于您提供的Oracle表结构）
TABLE_FIELDS = [
    "ID", "TRANSACTION_ID", "FPS_REF_NO", "ORIGINAL_FPS_REF_NO", "INSTRUCTION_ID", "END_TO_END_ID",
    "ACCT_VRF_OPTION", "CATEGORY_PURPOSE", "IS_CREDIT", "SETTLEMENT_AMT", "SETTLEMENT_CCY",
    "SETTLEMENT_DATE", "DEBTOR_NAME", "DEBTOR_AGENT", "DEBTOR_AGENT_BIC", "DEBTOR_ACCT_ID",
    "DEBTOR_ACCT_ID_TYPE", "CREDITOR_NAME", "CREDITOR_AGENT", "CREDITOR_AGENT_BIC", "CREDITOR_ACCT_ID",
    "CREDITOR_ACCT_ID_TYPE", "TRANSACTION_STATUS", "SETTLEMENT_DT", "BAL_STATUS", "CLR_CD", "TYP", "BUSINESS_SERVICE",
    "IS_OUTWARD",
    "CLIENT_SYS_ID", "CLIENT_REQ_ID", "IS_RR_REQUESTED", "IS_ONUS", "EX_TYPE", "EX_HDL_STS",
    "CREATION_DT", "LAST_UPDATE_DT", "ACCT_VRF_VAL", "CUST_9"
]

# CSV 到 TABLE 字段的映射
CSV_TO_TABLE_MAPPING = {
    "Business Service": "BUSINESS_SERVICE",
    "Payment Category Purpose": "CATEGORY_PURPOSE",
    "FPS Reference Number": "FPS_REF_NO",
    "Transaction ID": "TRANSACTION_ID",
    "End-to-end ID": "END_TO_END_ID",
    "Instruction ID": "INSTRUCTION_ID",
    "Creditor Name": "CREDITOR_NAME",
    "Creditor Account Number": "CREDITOR_ACCT_ID",
    "Creditor Account Number Type": "CREDITOR_ACCT_ID_TYPE",
    "Debtor Name": "DEBTOR_NAME",
    "Debtor Account Number": "DEBTOR_ACCT_ID",
    "Debtor Account Number Type": "DEBTOR_ACCT_ID_TYPE",
    "Currency": "SETTLEMENT_CCY",
    "Settlement Amount": "SETTLEMENT_AMT",
    "Status": "TRANSACTION_STATUS",
    "Settlement / End of Life Time": "SETTLEMENT_DT"
}


def generate_unique_id():
    return str(uuid.uuid4())


def generate_unique_id_time():
    # 获取当前时间戳（纳秒级）
    timestamp = int(time.time_ns())

    # 生成一个3位随机数
    random_num = random.randint(0, 999)

    # 组合时间戳和随机数，确保总长度为14位
    unique_id = f"{timestamp:019d}{random_num:03d}"

    return unique_id[-14:]  # 取最后14位


def generate_fps_reference_number():
    global used_fps_reference_numbers
    while True:
        fps_ref_no = f"FRN{datetime.now().strftime('%Y%m%d')}{generate_unique_id_time()}"
        if fps_ref_no not in used_fps_reference_numbers:
            used_fps_reference_numbers.add(fps_ref_no)
            return fps_ref_no


def generate_transaction_id():
    return f"TRX{datetime.now().strftime('%Y%m%d')}{generate_unique_id()[:20]}"


def generate_settlement_date():
    return (datetime.now() + timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d")


def generate_csv_record(current_id):
    record = {field: "" for field in CSV_FIELDS}

    record["Record Type"] = "DTL"
    record["Transaction Type"] = "CRTXFR"
    record["Business Service"] = "PAYC02"
    record["Payment Category Purpose"] = random.choice(["SALA"])
    record["FPS Reference Number"] = generate_fps_reference_number()
    record["Transaction ID"] = generate_transaction_id()
    record["End-to-end ID"] = generate_unique_id()[:35]
    record["Instruction ID"] = generate_unique_id()[:35]
    record["Creditor Name"] = f"Creditor {current_id}"
    record["Creditor Account Number"] = f"ACCT{current_id + 1:010d}"
    record["Creditor Account Number Type"] = "BBAN"
    record["Debtor Name"] = f"Debtor {current_id}"
    record["Debtor Account Number"] = f"ACCT{current_id:010d}"
    record["Debtor Account Number Type"] = "BBAN"
    record["Currency"] = random.choice(["HKD"])
    record["Settlement Amount"] = f"{round(random.uniform(1, 10000), 2):.2f}"
    # record["Status"] = random.choice(["PDNG"])
    # record["Status"] = random.choice(["RJCT"])
    record["Status"] = random.choice(["ACSC"])
    record["Settlement / End of Life Time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    record["Credit Participant"] = DEFAULT_CREDITOR_AGENT
    record["Debit Participant"] = DEFAULT_DEBTOR_AGENT

    return record


def generate_data(num_records, start_id, increment_step):
    data = []
    current_id = start_id
    for _ in range(num_records):
        record = generate_csv_record(current_id)
        data.append(record)
        current_id += increment_step
    return data


def write_csv(filename, data):
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=CSV_FIELDS, quotechar='\"', doublequote=True, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for row in data:
            writer.writerow(row)


def generate_sql_insert(record, id, client_req_id):
    table_record = {TABLE_FIELDS[i]: None for i in range(len(TABLE_FIELDS))}

    for csv_field, table_field in CSV_TO_TABLE_MAPPING.items():
        if csv_field in record:
            table_record[table_field] = record[csv_field]

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    settlementDate = datetime.now().strftime("%Y-%m-%d")
    yesteday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    # 昨天下午三点
    yesteday_af = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d 15:00:00.%f")
    table_record["ID"] = id
    table_record["CLIENT_REQ_ID"] = client_req_id
    table_record["IS_CREDIT"] = 1
    table_record["IS_OUTWARD"] = 0
    table_record["CLIENT_SYS_ID"] = "SYS001"
    table_record["IS_RR_REQUESTED"] = 0
    table_record["IS_ONUS"] = 0
    table_record["EX_TYPE"] = 0
    table_record["EX_HDL_STS"] = 0
    table_record["CREATION_DT"] = f"TO_TIMESTAMP('{current_time}', 'YYYY-MM-DD HH24:MI:SS.FF6')"
    table_record["LAST_UPDATE_DT"] = f"TO_TIMESTAMP('{current_time}', 'YYYY-MM-DD HH24:MI:SS.FF6')"
    table_record["CLR_CD"] = DEFAULT_CLR_CD
    table_record["TYP"] = DEFAULT_TYP
    table_record["BAL_STATUS"] = DEFAULT_BAL_STATUS
    table_record["CREDITOR_AGENT"] = record["Credit Participant"]
    table_record["DEBTOR_AGENT"] = record["Debit Participant"]
    table_record["SETTLEMENT_DT"] = f"TO_TIMESTAMP('{yesteday_af}', 'YYYY-MM-DD HH24:MI:SS.FF6')"
    table_record["ACCT_VRF_VAL"] = 0
    table_record["CUST_9"] = CUST_9
    table_record["SETTLEMENT_DATE"] = f"TO_TIMESTAMP('{yesteday}', 'YYYY-MM-DD')"

    fields = []
    values = []
    for field in TABLE_FIELDS:
        value = table_record.get(field)
        if value is not None:
            fields.append(field)
            if isinstance(value, str):
                if value.startswith("TO_TIMESTAMP") or value.startswith("DATE"):
                    values.append(value)
                else:
                    values.append(f"'{value}'")
            elif isinstance(value, (int, float)):
                values.append(str(value))
            else:
                values.append("NULL")
    return f"INSERT INTO ECFPS_PAYMENT_TBL ({', '.join(fields)}) VALUES ({', '.join(values)});"


def write_sql(filename, data, start_id, start_client_req_id):
    with open(filename, 'w') as sqlfile:
        current_id = start_id
        client_req_id = start_client_req_id
        for record in data:
            sqlfile.write(generate_sql_insert(record, current_id, client_req_id) + "\n")
            current_id += INCREMENT_STEP
            client_req_id += CLIENT_REQ_ID_INCREMENT


def main():
    data = generate_data(NUM_RECORDS, START_ID, INCREMENT_STEP)
    write_csv('output.csv', data)
    write_sql('output.sql', data, START_ID, START_CLIENT_REQ_ID)


def xb_payment(table_record):
    table_record["CRL_CD"] = 0
    table_record["AML_STS"] = 6


if __name__ == "__main__":
    main()
