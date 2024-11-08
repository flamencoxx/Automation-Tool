import random
import string
from datetime import date, timedelta


def generate_random_string(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def generate_random_date(start_date, end_date):
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    return start_date + timedelta(days=random_number_of_days)


def generate_insert_statement(num_records):
    insert_statements = []

    for _ in range(num_records):
        icl_file_date = generate_random_date(date(2020, 1, 1), date(2023, 12, 31))
        icl_file_name = f"ICL_FILE_{generate_random_string(10)}.txt"
        corp_type = "MRCH"
        agent_cd = random.choice(['004', '003', '025'])
        cust_id = generate_random_string(34)
        proxy_id = generate_random_string(34)
        proxy_id_type = generate_random_string(4).upper()
        status = random.choice(['A', 'I', 'P'])

        insert_statement = f"""
        INSERT INTO ECFPS_ADR_MERCHANT_TBL (
            ICL_FILE_DATE, ICL_FILE_NAME, CORP_TYPE, AGENT_CD, CUST_ID, PROXY_ID, PROXY_ID_TYPE, STATUS
        ) VALUES (
            '{icl_file_date}', '{icl_file_name}', '{corp_type}', '{agent_cd}', '{cust_id}', '{proxy_id}', '{proxy_id_type}', '{status}'
        );
        """
        insert_statements.append(insert_statement)

    return insert_statements


# 生成10条插入语句
num_records = 10
insert_statements = generate_insert_statement(num_records)

# 将插入语句写入文件
with open('insert_statements-50000A.sql', 'w') as f:
    for statement in insert_statements:
        f.write(statement + '\n')

print(f"{num_records} 条插入语句已生成并写入 insert_statements-50000A.sql 文件")
