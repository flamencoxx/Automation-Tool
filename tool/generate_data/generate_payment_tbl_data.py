import random
import string
from datetime import datetime, timedelta
from decimal import Decimal
import uuid
import argparse


def random_string(length, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(length))


def random_amount():
    return round(random.uniform(1, 1000000), 2)


def random_date(start_date, end_date):
    time_between = end_date - start_date
    days_between = time_between.days
    random_days = random.randrange(days_between)
    random_seconds = random.randrange(24 * 60 * 60)
    return start_date + timedelta(days=random_days, seconds=random_seconds)


def generate_value_string(i, start_datetime, end_datetime):
    transaction_id = f"TXN{str(i).zfill(10)}"
    fps_ref_no = f"FPS{str(i).zfill(10)}"
    category_purpose = random.choice(['CASH', 'CXBSNS', 'CXECNY', 'CXGOVT', 'CXMRCH', 'CXOTHS'])
    settlement_amt = random_amount()
    settlement_ccy = random.choice(['HKD', 'USD', 'EUR'])
    settlement_date = random_date(start_datetime, end_datetime).strftime('%Y-%m-%d')
    debtor_agent = random.choice(['001', '025', '012'])
    debtor_acct_id = f"ACCT{random_string(16)}"
    debtor_acct_id_type = random.choice(['BBAN', 'AIIN'])
    creditor_agent = random.choice(['001', '025', '012'])
    creditor_acct_id = f"ACCT{random_string(16)}"
    creditor_acct_id_type = random.choice(['BBAN', 'AIIN'])
    transaction_status = random.choice(['RCVD', 'CNCL', 'ACSC', 'ACCP'])
    bal_status = random.randint(0, 3)
    clr_cd = random.choice(['001', '025', '012'])
    business_service = random.choice(['PAYC01', 'PAYC02'])
    client_sys_id = f"SYS{random_string(8)}"
    client_req_id = f"REQ{str(uuid.uuid4())[:30]}"

    start_time = datetime.strptime('2025-01-11 00:00:00', '%Y-%m-%d %H:%M:%S')
    end_time = datetime.strptime('2025-01-12 23:59:59', '%Y-%m-%d %H:%M:%S')
    creation_dt = random_date(start_time, end_time).strftime('%Y-%m-%d %H:%M:%S')

    typ = random.choice(['N', 'R', 'C', 'P'])  # 根据实际业务含义调整这些值

    acct_vrf_option = 'PERFORM_PYE_VRF'

    return f"""(
        '{transaction_id}', '{fps_ref_no}', '{category_purpose}', {random.choice([0, 1])},
        {settlement_amt}, '{settlement_ccy}', '{settlement_date}',
        '{debtor_agent}', '{debtor_acct_id}', '{debtor_acct_id_type}',
        '{creditor_agent}', '{creditor_acct_id}', '{creditor_acct_id_type}',
        '{transaction_status}', {bal_status}, '{clr_cd}', '{business_service}',
        {random.choice([0, 1])}, '{client_sys_id}', '{client_req_id}', {random.choice([0, 1])},
        {random.choice([0, 1])}, {random.randint(0, 9)}, {random.randint(0, 9)},
        '{creation_dt}', '{typ}', '{acct_vrf_option}', 0
    )"""


def parse_datetime(datetime_str):
    try:
        return datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        raise argparse.ArgumentTypeError(f'Invalid datetime format. Use YYYY-MM-DD HH:MM:SS')


def main():
    parser = argparse.ArgumentParser(description='Generate test data for ECFPS_PAYMENT_TBL')
    parser.add_argument('--total', type=int, default=700000,
                        help='Total number of records to generate (default: 700000)')
    parser.add_argument('--batch-size', type=int, default=1000,
                        help='Number of records per INSERT statement (default: 1000)')
    parser.add_argument('--block-size', type=int, default=10000,
                        help='Number of records per execution block (default: 10000)')
    parser.add_argument('--start-date', type=parse_datetime,
                        default=datetime(2023, 1, 1),
                        help='Start datetime for CREATION_DT (format: YYYY-MM-DD HH:MM:SS)')
    parser.add_argument('--end-date', type=parse_datetime,
                        default=datetime(2024, 12, 31, 23, 59, 59),
                        help='End datetime for CREATION_DT (format: YYYY-MM-DD HH:MM:SS)')
    parser.add_argument('--output', type=str, default='payment_insert.sql',
                        help='Output SQL file name (default: payment_insert.sql)')

    args = parser.parse_args()

    columns = """
        TRANSACTION_ID, FPS_REF_NO, CATEGORY_PURPOSE, IS_CREDIT, 
        SETTLEMENT_AMT, SETTLEMENT_CCY, SETTLEMENT_DATE,
        DEBTOR_AGENT, DEBTOR_ACCT_ID, DEBTOR_ACCT_ID_TYPE,
        CREDITOR_AGENT, CREDITOR_ACCT_ID, CREDITOR_ACCT_ID_TYPE,
        TRANSACTION_STATUS, BAL_STATUS, CLR_CD, BUSINESS_SERVICE,
        IS_OUTWARD, CLIENT_SYS_ID, CLIENT_REQ_ID, IS_RR_REQUESTED,
        IS_ONUS, EX_TYPE, EX_HDL_STS, CREATION_DT, TYP, ACCT_VRF_OPTION, ACCT_VRF_VAL
    """

    with open(args.output, 'w', encoding='utf-8') as f:
        f.write('SET NOCOUNT ON;\n\n')

        # 添加GO语句的计数器
        block_count = 0

        # Generate data in batches
        batch_values = []
        for i in range(args.total):
            batch_values.append(generate_value_string(i, args.start_date, args.end_date))

            # 当批次满了或是最后一条记录时写入文件
            if len(batch_values) == args.batch_size or i == args.total - 1:
                # 如果是新块的开始，添加注释
                if i % args.block_size == 0:
                    block_count += 1
                    f.write(
                        f'\n-- Block {block_count}: Records {i + 1 - len(batch_values)} to {min(i + args.block_size, args.total)}\n')

                f.write('BEGIN TRANSACTION;\n')
                f.write(f'INSERT INTO ECFPS_PAYMENT_TBL (\n{columns}\n) VALUES\n')
                f.write(',\n'.join(batch_values))
                f.write(';\n')
                f.write('COMMIT;\n')
                batch_values = []

                # 每个块结束时添加GO
                if (i + 1) % args.block_size == 0 or i == args.total - 1:
                    f.write('\nGO\n\n')

                # 打印进度
                print(f'Generated {i + 1} of {args.total} records')

        f.write('SET NOCOUNT OFF;\n')


if __name__ == '__main__':
    main()
