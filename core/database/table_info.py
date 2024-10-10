# 配置表
from sqlalchemy import create_engine, Column, Integer, String, Float, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
'''
class MyBase(Base):
    def to_dict(self):
        info_dict = dict()
        for _k, _v in self.__dict__.items():
            if _k != '_sa_instance_state':
                info_dict[_k] = _v
        return info_dict
'''

class CalculatorConfig(Base):
    __tablename__ = 'calculator_config'

    id = Column(Integer, primary_key=True)
    key_name = Column(String, nullable=False)
    key_value = Column(String, nullable=False)
    key_type = Column(String, nullable=False)
    parent_id = Column(Integer, default=0)

# 数据历史表
class CalculatorHistory(Base):
    __tablename__ = 'calculator_history'

    id = Column(Integer, primary_key=True, autoincrement=True)
    last_month_use = Column(Integer, nullable=False)
    this_month_use = Column(Integer, nullable=False)
    power_rate = Column(Float, nullable=False)
    public_fee = Column(Float, nullable=False)
    total_fee = Column(Float, nullable=False)
    whois = Column(String)
    create_date = Column(Date, nullable=False)

