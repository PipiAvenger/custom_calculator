import pandas as pd
import openpyxl
from core.database.table_info import CalculatorHistory
from core.database.db_base import Database
from core.tools.com_time import get_last_6_months
from datetime import datetime, date

excel_file_path_dir = "E:\\code\\work\\code\\billHistory\\"

excel_file_path = excel_file_path_dir + '2024-03.xlsx'

def get_data_from_excel(file_path: str, months: str):
    history_list = []
    df = pd.read_excel(excel_file_path, header=None)
    date = datetime.strptime(df.iat[0,0][:7], '%Y-%m').date()
    print(date)
    for col in range(1, 7):
        one_history = CalculatorHistory()
        one_history.create_date = date
        one_history.total_fee = df.iat[7, 0][8:14]
        for row in range(0, 6):
            if row == 0:
                if col == 6:
                    room = df.iat[row, col]
                    print(room)
                    one_history.whois = room
                else:
                    room = f'房间{col}:' + df.iat[row, col][2]
                    one_history.whois = room
                    print(room)
            elif row == 1:
                last_month_use = int(df.iat[row, col])
                one_history.last_month_use = last_month_use
                print(last_month_use)
            elif row == 2:
                this_month_use = int(df.iat[row, col])
                one_history.this_month_use = this_month_use
                print(this_month_use)
            elif row == 3:
                power_rate = format(float(df.iat[row, col]), '.2f')
                one_history.power_rate = power_rate
                print(power_rate)
            elif row == 4:
                public_fee = format(float(df.iat[row, col]), '.2f')
                one_history.public_fee = public_fee
                print(public_fee)
            elif row == 5:
                total_fee = format(float(df.iat[row, col]), '.2f')
                one_history.total_fee = total_fee
                print(total_fee)

        history_list.append(one_history)

    with Database().get_session() as session:
        session.add_all(history_list)
        session.commit()


db = Database(database='E:\\code\\custom_calculator\\database\\data.db')

import_months_list = get_last_6_months()
for month in import_months_list:
    excel_file_path = f'{excel_file_path_dir}{month}.xlsx'
    print(f'开始导入:excel_file_path')
    get_data_from_excel(excel_file_path, month)
    print(f'完成导入:excel_file_path')