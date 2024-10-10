from sqlalchemy import create_engine, Column, Integer, String, Float, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class Database:
    """
    数据库连接池单例
    """
    _instance = None

    def __new__(cls, db_type='sqlite', username=None, password=None, host=None, port=None, database=None):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance.__init__(db_type, username, password, host, port, database)
        return cls._instance

    def __init__(self, db_type='sqlite', username=None, password=None, host=None, port=None, database=None):
        if not hasattr(self, 'engine'):  # 防止重复初始化
            self.db_type = db_type
            self.username = username
            self.password = password
            self.host = host
            self.port = port
            self.database = database
            self.engine = self.create_engine()
            self.Session = sessionmaker(bind=self.engine)

            #如果表格数据不存在则创建
            self.create_tables()
    def create_engine(self):
        if self.db_type == 'sqlite':
            return create_engine('sqlite:///{}'.format(self.database))
        elif self.db_type == 'mysql':
            return create_engine(
                f'mysql+pymysql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}')
        else:
            raise ValueError("Unsupported database type")

    def create_tables(self):
        Base.metadata.create_all(self.engine)

    def get_session(self):
        return self.Session()

# 使用示例
if __name__ == "__main__":
    # 创建 SQLite 数据库
    db = Database(db_type='sqlite', database='my_database.db')
    db.create_tables()

    # 创建 MySQL 数据库
    # db = Database(db_type='mysql', username='your_username', password='your_password', host='localhost', port=3306, database='your_database')
    # db.create_tables()
