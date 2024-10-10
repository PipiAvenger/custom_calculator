import sys
from PyQt5.QtWidgets import QApplication
from core.tools.file_operation import ensure_file_exists
from core.database.db_base import Database
from core.page_ui.bill_calculator import BillCalculator


def main():
    """
    账单计算器的主进程
    :return:
    """
    # qt5初始化QApplication类
    app = QApplication(sys.argv)

    # 数据句柄初始化
    db_dir = './database/data.db'
    ensure_file_exists(db_dir)
    database = Database(
        db_type='sqlite',
        database=db_dir
    )

    # 初始化账单计算器
    window = BillCalculator()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()