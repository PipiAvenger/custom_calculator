import copy
from copy import deepcopy
import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame, QStackedLayout, QComboBox, QWidget
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap
from readerwriterlock import rwlock
import json
import queue
from datetime import datetime
from .base_style import BaseVItem, build_line_graph, clean_figure_obj
from .task import (
CTask, UPDATE_ITEM_TASK, UPDATE_HISTORY_RECORD_TASK
)
from core.tools.com_log import Logger
from core.tools.com_thread import EventThread
from core.tools.com_time import get_last_6_months
from core.database.db_base import Database
from core.database.table_info import CalculatorConfig, CalculatorHistory

logger = Logger().get_logger()

class BillCalculator(QMainWindow):
    def __init__(self):
        super().__init__()
        # 缓存锁
        self.rw_cache_lock = rwlock.RWLockFairD()
        # 任务队列
        self.task_queue = queue.Queue()
        # 线程对象
        self.sync_thread = EventThread(
            name='sync_thread',
            target=self.thread_loop,
            event_flag=True)
        self.sync_thread.start()
        # 数据配置初始化
        self.load_config()
        # 程序界面ui初始化
        self.init_UI()
        # 计算结果
        self.calculator_result = dict()

    def thread_loop(self):
        while True:
            task = self.task_queue.get()
            logger.debug(f'收到任务类型:{task.task_type}')

            self.deal_task(task)

    def deal_task(self, task: CTask):
        if task.task_type == UPDATE_ITEM_TASK:
            self.sync_to_db(task.data_info)
        elif task.task_type == UPDATE_HISTORY_RECORD_TASK:
            self.sync_history_result_to_db(task.data_info)

    def load_config(self):
        self.config_dict = self.load_data_from_db()

    def load_data_from_db(self):
        """从数据库加载数据到字典"""
        logger.info('开始加载用户配置数据')
        session = Database().get_session()
        config_dict = {}
        with session:
            for config in session.query(CalculatorConfig).all():
                one_config = dict()
                for _k, _v in config.__dict__.items():
                    if _k != '_sa_instance_state':
                        one_config[_k] = _v
                config_dict[config.id] = one_config

        logger.info(f'成功加载数据总数:{len(config_dict.keys())}')
        return config_dict

    def update_config(self,update_info: dict):
        """更新字典中的配置并同步到数据库"""
        with self.rw_cache_lock.gen_wlock():
            k_id = update_info.get('id', None)
            if k_id is not None and k_id in self.config_dict:
                info = self.config_dict[k_id]

                # key_name, key_value, key_type, parent_id赋值
                for _key, _value in update_info.items():
                    if _key in info:
                        info[_key] = _value

    def sync_to_db(self, update_info: dict):
        """将字典中的数据同步到数据库"""
        k_id = update_info.get('id', None)
        session = Database().get_session()
        with session:
            if k_id:
                config = session.query(CalculatorConfig).filter_by(id=k_id).first()
                if config:
                    # key_name, key_value, key_type, parent_id赋值
                    for _k, _v in update_info.items():
                        if hasattr(config, _k):
                            setattr(config, _k, _v)

                    session.commit()

                logger.debug(f'同步数据:{update_info}')

    def sync_history_result_to_db(self, update_info: dict):
        months = get_last_6_months()
        # 取当前月的前一个月
        str_date = months[-1]
        # 先删除前一个月的所有记录
        self.delete_history_record_from_db_by_date(str_date)
        # 覆盖
        room_info_list = update_info['room']
        for room_info in room_info_list:
            data_info = dict()
            data_info['create_date'] = datetime.strptime(str_date, '%Y-%m').date()
            # 归属赋值
            for _key, _value in room_info.items():
                if '房间' in _key:
                    data_info['whois'] = f'{_key}:{_value}'
                    break
            data_info['last_month_use'] = room_info['上月用电度数']
            data_info['this_month_use'] = room_info['本月用电度数']
            data_info['power_rate'] = room_info['个人电费']
            data_info['public_fee'] = room_info['公摊费用']
            data_info['total_fee'] = room_info['总计费用']
            self.add_one_history_record_to_db(data_info)

        # 公摊信息
        public_ex_info = update_info['public-ex']
        data_info = dict()
        data_info['whois'] = '公摊'
        data_info['create_date'] = datetime.strptime(str_date, '%Y-%m').date()
        data_info['last_month_use'] = public_ex_info['上月用电度数']
        data_info['this_month_use'] = public_ex_info['本月用电度数']
        data_info['power_rate'] = public_ex_info['电费']
        data_info['public_fee'] = public_ex_info['公摊费用']
        data_info['total_fee'] = 0.0
        self.add_one_history_record_to_db(data_info)

    def init_UI(self):
        logger.info('开始初始化ui')
        self.setWindowTitle('账单计算器')

        # 应用主进程窗口初始化
        self.init_screen()

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        # 主布局对象
        main_layout = QVBoxLayout(central_widget)

        # 按钮居中布局
        button_layout = QHBoxLayout()
        self.calc_button = QPushButton('账单计算')
        self.history_button = QPushButton('历史账单')
        button_layout.addStretch(0)
        button_layout.addWidget(self.calc_button)
        button_layout.addWidget(self.history_button)
        button_layout.addStretch(0)

        # 页面容器
        self.pages = QStackedLayout()
        self.bill_calculator_page = self.create_bill_calculator_page()
        # self.history_page = self.create_history_page()

        self.pages.addWidget(self.bill_calculator_page)

        # 默认显示账单计算页面（这里的写法是2个静态页面布局）
        self.calc_button.clicked.connect(lambda: self.pages.setCurrentWidget(self.bill_calculator_page))
        # self.history_button.clicked.connect(lambda: self.pages.setCurrentWidget(self.history_page))
        # 动态加载历史账单数据
        self.history_button.clicked.connect(self.update_history_page)

        main_layout.addLayout(button_layout)
        main_layout.addLayout(self.pages)

        logger.info('初始化ui结束，开始工作')

    def init_screen(self):
        # 设置窗口大小为屏幕的60%
        screen = QApplication.primaryScreen().size()
        width = int(screen.width() * 0.6)
        height = int(screen.height() * 0.6)
        self.resize(width, height)

        # 居中显示窗口
        self.setGeometry(
            (screen.width() - width) // 2,
            (screen.height() - height) // 2,
            width, height
        )

        # 程序图标
        icon = QIcon()
        icon.addPixmap(QPixmap('./favicon.ico'))
        self.setWindowIcon(icon)

    def create_bill_calculator_page(self):
        """
        账单计算页的设计
        :return: page
        """
        page = QFrame()

        # 账单计算空间样式
        bill_space = QFrame()
        bill_space.setFrameShape(QFrame.Panel)
        bill_space.setFrameShadow(QFrame.Raised)
        bill_space.setLineWidth(3)
        bill_layout = QVBoxLayout()

        # 将单项计费空间添加到账单计算空间
        bill_layout.addWidget(self.create_individual_items_space())

        # 将公共项计费空间添加到账单计算空间
        bill_layout.addWidget(self.create_public_fee_items_page())

        # 费用结算空间（在用户点击之前为空）
        bill_layout.addLayout(self.init_bill_calculator_page())

        # 计算按钮
        bill_layout.addWidget(self.create_calculator_push_button_page())

        page.setLayout(bill_layout)
        return page

    def create_individual_items_space(self):
        """
        创建单项列表空间布局
        :return: individual_fee_space
        """
        # 单独项计费空间样式
        individual_fee_space = QFrame()
        individual_fee_space.setFrameShape(QFrame.Panel)
        individual_fee_space.setFrameShadow(QFrame.Raised)
        individual_fee_space.setLineWidth(2)
        # 设置圆角
        # individual_fee_space.setStyleSheet("border-radius: 10px; border: 2px solid black;")

        individual_fee_layout = QVBoxLayout()
        # 单独项计费栏
        name_label = QLabel('单独项计费')
        individual_fee_layout.addWidget(name_label)

        # 单项费用项栏
        items_space = QHBoxLayout()
        with self.rw_cache_lock.gen_rlock():
            rooms = list(filter(
                lambda item: item['key_type'] == 'room',
                self.config_dict.values()))
            for room in rooms:
                items_space.addWidget(self.create_individual_one_item_space(room))
        individual_fee_layout.addLayout(items_space)
        individual_fee_space.setLayout(individual_fee_layout)

        return individual_fee_space

    def create_individual_one_item_space(self, room: dict):
        """
        创建单项布局
        :return: item_space
        """
        item_layout = QVBoxLayout()
        item_space = QFrame()
        key_name_list = [room]
        key_name_list.extend(filter(
            lambda item: item['parent_id'] == room['id'],
            self.config_dict.values()))
        for one_item in key_name_list:
            one_frame = BaseVItem(
                key_id=one_item['id'],
                key_name=one_item['key_name'],
                default_value=one_item['key_value'],
                parent_id=one_item['parent_id'])
            one_frame.set_QLineEdit_callback(self)
            item_layout.addWidget(one_frame)
        item_space.setLayout(item_layout)
        return item_space

    def func_callback(self, frame: BaseVItem):
        data_info = {
            'id': frame.key_id,
            'key_name': frame.get_item_name(),
            'key_value': frame.get_item_value(),
            'parent_id': frame.parent_id
        }
        # 更新缓存
        self.update_config(data_info)

        #异步同步数据库任务队列
        self.task_queue.put(CTask(data_info))

    def create_public_fee_items_page(self):
        """
        创建公共项计费空间
        :return:
        """
        # 公共项计费空间样式
        public_fee_space = QFrame()
        public_fee_space.setFrameShape(QFrame.Panel)
        public_fee_space.setFrameShadow(QFrame.Raised)
        public_fee_space.setLineWidth(2)

        public_fee_layout = QVBoxLayout()
        # 公共项计费栏
        name_label = QLabel('公共项计费')
        public_fee_layout.addWidget(name_label)

        # 公共项费用栏
        items_space = QHBoxLayout()
        with self.rw_cache_lock.gen_rlock():
            public_items_list = list(
                filter(
                    lambda item: item['key_type'] == 'public',
                    self.config_dict.values()))
            for one_item in public_items_list:
                one_frame = BaseVItem(
                    key_id=one_item['id'],
                    key_name=one_item['key_name'],
                    default_value=one_item['key_value'],
                    parent_id=one_item['parent_id'])
                one_frame.set_QLineEdit_callback(self)
                items_space.addWidget(one_frame)
        public_fee_layout.addLayout(items_space)

        # 公共区域用电栏
        items_space = QHBoxLayout()
        name_label = QLabel('公摊用电情况')
        public_fee_layout.addWidget(name_label)
        with self.rw_cache_lock.gen_rlock():
            publicex_items_list = list(
                filter(
                    lambda item: item['key_type'] == 'public-ex',
                    self.config_dict.values()))
            for one_item in publicex_items_list:
                one_frame = BaseVItem(
                    key_id=one_item['id'],
                    key_name=one_item['key_name'],
                    default_value=one_item['key_value'],
                    parent_id=one_item['parent_id'])
                one_frame.set_QLineEdit_callback(self)
                items_space.addWidget(one_frame)
        public_fee_layout.addLayout(items_space)
        public_fee_space.setLayout(public_fee_layout)

        return public_fee_space

    def init_bill_calculator_page(self):
        """
        创建账单信息计算结果
        :return: stackedLayout
        """
        self.calculate_result_page = QStackedLayout()
        frame = QFrame()
        frame.setFrameShape(QFrame.Panel)
        frame.setFrameShadow(QFrame.Raised)
        frame.setLineWidth(2)

        self.init_bill_page = frame
        self.calculate_result_page.addWidget(frame)
        return self.calculate_result_page

    def create_calculator_push_button_page(self):
        """
        按钮布局
        :return: page
        """
        page = QFrame()
        button_space = QHBoxLayout()
        button_space.addStretch(0)
        self.culator_button = QPushButton('计算')

        # 触发动态布局更新
        self.culator_button.clicked.connect(self.update_calculator_callback)
        button_space.addWidget(self.culator_button, 0 , Qt.AlignCenter | Qt.AlignVCenter)
        button_space.addStretch(0)

        page.setLayout(button_space)

        return page

    def update_calculator_callback(self):
        """
        按钮触发回调函数
        :return:
        """
        update_page = self.update_bill_calculator_result_page()

        # 替换初始化的页面布局
        if hasattr(self, 'init_bill_page') and self.init_bill_page:
            self.calculate_result_page.removeWidget(self.init_bill_page)
        else:
            self.init_bill_page = update_page
        self.calculate_result_page.addWidget(update_page)
        self.calculate_result_page.setCurrentWidget(update_page)

        # 同步计算结果到历史表中
        sync_history_result = CTask(
            copy.deepcopy(self.calculator_result),
            UPDATE_HISTORY_RECORD_TASK
        )
        self.task_queue.put(sync_history_result)

    def calculate(self):
        """

        :return:
            result_info = {
                'room': [],
                'public':{},
                'public-ex':{}
        }
        """
        result_info = dict()
        with self.rw_cache_lock.gen_rlock():
            data_info = deepcopy(self.config_dict)

        public_info = dict()
        # 提取电费单价
        __per_electricity = list(filter(lambda item: item['key_name'] == '电费单价', data_info.values()))
        _per_electricity = __per_electricity.pop(0)
        # 不影响下面公共费用求和
        data_info.pop(_per_electricity['id'])
        per_electricity = float(_per_electricity['key_value'])
        public_info[_per_electricity['key_name']] = _per_electricity['key_value']

        # 公共费用处理
        __public_items = list(filter(lambda item: item['key_type'] == 'public', data_info.values()))
        public_fee = float()
        for _public_item in __public_items:
            public_fee += float(_public_item['key_value'])
            public_info[_public_item['key_name']] = _public_item['key_value']
        result_info['public'] = public_info

        public_ex_info = dict()
        # 公共用电取值
        __pub_use_electricity = list(filter(lambda item: item['key_type'] == 'public-ex', data_info.values()))
        # 公共总用电数
        __pub_use_total_ele = list(filter(lambda item: item['key_name'].find('总计') != -1, __pub_use_electricity))
        _pub_use_total_ele = __pub_use_total_ele.pop(0)
        pub_use_total_ele = float(_pub_use_total_ele['key_value'])
        public_info[_pub_use_total_ele['key_name']] = _pub_use_total_ele['key_value']
        # 公共上月用电数
        __pub_use_last_ele = list(filter(lambda item: item['key_name'].find('上月') != -1, __pub_use_electricity))
        _pub_use_last_ele = __pub_use_last_ele.pop(0)
        pub_use_last_ele = float(_pub_use_last_ele['key_value'])
        public_ex_info[_pub_use_last_ele['key_name']] = _pub_use_last_ele['key_value']
        # 公共本月用电数
        __pub_use_now_ele = list(filter(lambda item: item['key_name'].find('本月') != -1, __pub_use_electricity))
        _pub_use_now_ele = __pub_use_now_ele.pop(0)
        pub_use_now_ele = float(_pub_use_now_ele['key_value'])
        public_ex_info[_pub_use_now_ele['key_name']] = _pub_use_now_ele['key_value']
        # 公摊电费计算
        public_ex_info['电费'] = format((pub_use_now_ele - pub_use_last_ele) * per_electricity, '.3f')
        result_info['public-ex'] = public_ex_info

        actual_use_power = float()
        actual_use_power += pub_use_now_ele - pub_use_last_ele

        room_num = 0
        room_result_list = list()
        room_list = list(filter(lambda room: room['key_type'] == 'room', data_info.values()))
        for _room in room_list:
            items_list = list(filter(lambda item: item['parent_id'] == _room['id'], data_info.values()))
            # 个人上月用电度数提取
            __last_power = list(filter(lambda item: item['key_name'].find('上月') != -1, items_list))
            _last_power = __last_power.pop(0)
            last_power = float(_last_power['key_value'])

            # 个人本月用电度数提取
            __now_power = list(filter(lambda item: item['key_name'].find('本月') != -1, items_list))
            _now_power = __now_power.pop(0)
            now_power = float(_now_power['key_value'])

            one_room_info = {
                _room['key_name']: _room['key_value'],
                _last_power['key_name']: _last_power['key_value'],
                _now_power['key_name']: _now_power['key_value']
            }

            if _room['key_value'] != '无':
                room_num += 1
                # 个人电费
                one_room_info['个人电费'] = per_electricity * (now_power - last_power)
                actual_use_power += now_power - last_power
            else:
                one_room_info['个人电费'] = format(0, '.3f')
                one_room_info['公摊费用'] = format(0, '.3f')
                one_room_info['总计费用'] = format(0, '.3f')
                one_room_info['不计费'] = 1

            room_result_list.append(one_room_info)

        # 个人采集和物业采集数据金额偏差
        share_equally_power = (pub_use_total_ele - actual_use_power) * per_electricity
        public_ex_info['采集偏差'] = format(share_equally_power, '.3f')

        #平摊价格
        if room_num != 0:
            share_fee = (share_equally_power + public_fee) / room_num
        else:
            share_fee = 0

        total_fee = 0
        for one_room_result in room_result_list:
            # 跳过不计费房间
            if one_room_result.get('不计费', 0):
                one_room_result.pop('不计费')
                continue

            one_room_result['公摊费用'] = format(share_fee, '.3f')
            person_ele_fee = one_room_result['个人电费']
            one_room_result['个人电费'] = format(person_ele_fee, '.3f')
            one_room_result['总计费用'] = format(share_fee + person_ele_fee, '.3f')
            total_fee += share_fee + person_ele_fee
        result_info['room'] = room_result_list

        # 合计
        public_info['总费用合计'] = format(total_fee, '.3f')
        public_ex_info['公摊费用'] = share_fee
        logger.debug(f'计算结果如下:{json.dumps(result_info, ensure_ascii=False)}')
        return result_info

    def update_bill_calculator_result_page(self):
        frame = QFrame()
        frame.setFrameShape(QFrame.Panel)
        frame.setFrameShadow(QFrame.Raised)
        frame.setLineWidth(2)
        update_layout = QVBoxLayout()

        logger.info('用户触发计算')

        # 结果计算
        self.calculator_result = self.calculate()

        # 结果空间一栏
        # 标题
        # 名称一栏
        now_date = datetime.now()
        formatted_date = now_date.strftime('%Y-%m')
        update_layout.addWidget(QLabel(f'{formatted_date}月费用统计情况'))

        # room
        room_list = self.calculator_result['room']
        rooms_layout = QHBoxLayout()
        for room in room_list:
            rooms_layout.addWidget(
                BaseVItem.trans_dict_2_qt_frame_1(
                    room, QFrame()
                )
            )
        update_layout.addLayout(rooms_layout)

        # 备注说明栏
        note = '注：'
        public_info = self.calculator_result['public']
        note += "，".join(f'{_k}：{_v}' for _k, _v in public_info.items())
        update_layout.addWidget(QLabel(note))
        # 公摊栏详情
        note = '公摊详情：'
        public_ex_info = self.calculator_result['public-ex']
        note += "，".join(f'{_k}：{_v}' for _k, _v in public_ex_info.items())
        update_layout.addWidget(QLabel(note))
        frame.setLayout(update_layout)

        logger.info('计算结果完成')
        return frame

    def create_history_page(self):
        page = QFrame()
        page.setFrameShape(QFrame.Panel)
        page.setFrameShadow(QFrame.Raised)
        page.setLineWidth(2)
        layout = QVBoxLayout()

        # 总费用以及平均付费的折线图
        last_6months_layout = self.create_last_6months_total_fee_layout()
        layout.addWidget(last_6months_layout)

        # 个人费用折线图
        last_6months_per_room_layout = self.create_history_per_room_info_layout()
        layout.addWidget(last_6months_per_room_layout)

        page.setLayout(layout)
        return page

    def update_history_page(self):
        if hasattr(self, 'history_page') and self.history_page:
            self.pages.removeWidget(self.history_page)
            clean_figure_obj()

        self.history_page = self.create_history_page()
        self.pages.addWidget(self.history_page)
        self.pages.setCurrentWidget(self.history_page)

    def create_last_6months_total_fee_layout(self):
        page = QFrame()
        page.setFrameShape(QFrame.Panel)
        page.setFrameShadow(QFrame.Raised)
        page.setLineWidth(2)
        page_layout = QVBoxLayout()
        name_label_layout = QHBoxLayout()
        label = QLabel('最近6个月总费用和平均公详情')
        name_label_layout.addWidget(label)

        history_summary_combo_box_titles = ['总计费用', '平均公摊']
        self.history_summary_combo_box = QComboBox()
        self.history_summary_combo_box.addItems(history_summary_combo_box_titles)
        self.history_summary_combo_box.currentIndexChanged.connect(
            self.update_history_summary_combo_box_page
        )
        self.history_summary_combo_box.setCurrentIndex(0)
        name_label_layout.addWidget(self.history_summary_combo_box)
        name_label_layout.addStretch()
        page_layout.addLayout(name_label_layout)
        # 历史房间总统计
        self.history_summary_combo_box_layout = QStackedLayout()
        # 初始化历史总费用信息
        self.history_summary_combo_box_layout.addWidget(
            self.update_summary_combo_box_layout()
        )
        self.history_summary_combo_box_layout.addWidget(
            self.update_average_combo_box_layout()
        )
        self.history_summary_combo_box_layout.setCurrentWidget(self.summary_line_graph_frame)

        page_layout.addLayout(self.history_summary_combo_box_layout)
        page.setLayout(page_layout)
        return page

    def update_history_summary_combo_box_page(self):
        now_title = self.history_summary_combo_box.currentText()
        if now_title == '总计费用':
            # 先移除旧的布局再加入新布局
            self.history_summary_combo_box_layout.removeWidget(
                self.summary_line_graph_frame
            )
            self.update_summary_combo_box_layout()
            self.history_summary_combo_box_layout.addWidget(
                self.summary_line_graph_frame
            )
            self.history_summary_combo_box_layout.setCurrentWidget(
                self.summary_line_graph_frame
            )
        elif now_title == '平均公摊':
            # 先移除旧的布局再加入新布局
            self.history_summary_combo_box_layout.removeWidget(
                self.average_line_graph_frame
            )
            self.update_average_combo_box_layout()
            self.history_summary_combo_box_layout.addWidget(
                self.average_line_graph_frame
            )
            self.history_summary_combo_box_layout.setCurrentWidget(
                self.average_line_graph_frame
            )

    def update_summary_combo_box_layout(self):
        # 总费用折线图
        date_list = get_last_6_months()
        show_data = self.get_history_records_from_db_by_date(date_list[0])
        self.summary_line_graph_frame = build_line_graph(
            '最近6个月房间总支出',
            '月份',
            '金额',
            show_data
        )

        return self.summary_line_graph_frame

    def update_average_combo_box_layout(self):
        # 公共均摊折线图
        date_list = get_last_6_months()
        show_data = self.get_history_average_public_fee_from_db_by_date(date_list[0])
        self.average_line_graph_frame = build_line_graph(
            '最近6个月平均均摊',
            '月份',
            '金额',
            show_data
        )

        return self.average_line_graph_frame

    def create_history_per_room_info_layout(self):
        page = QFrame()
        page.setFrameShape(QFrame.Panel)
        page.setFrameShadow(QFrame.Raised)
        page.setLineWidth(2)
        page_layout = QVBoxLayout()
        name_label_layout = QHBoxLayout()
        label = QLabel('每个房间最近6个月的费用情况')
        name_label_layout.addWidget(label)

        months = get_last_6_months()
        rooms = self.get_history_roomers_from_db(months[0])

        self.rooms_combo_box = QComboBox()
        self.rooms_combo_box.addItems(rooms)
        self.rooms_combo_box.currentIndexChanged.connect(
            self.update_rooms_combo_box_page
        )
        self.rooms_combo_box.setCurrentIndex(0)
        name_label_layout.addWidget(self.rooms_combo_box)
        name_label_layout.addStretch()
        page_layout.addLayout(name_label_layout)
        # 个人房间信息
        self.rooms_combo_box_layout = QStackedLayout()
        self.rooms = dict()
        for room in rooms:
            one_room_record = self.get_history_records_from_db_by_whois(
                months[0],
                room
            )
            line_graph_page = build_line_graph(
                    '每月费用图', '月份','金额',
                    one_room_record
                )
            self.rooms[room] = line_graph_page
            self.rooms_combo_box_layout.addWidget(
                line_graph_page
            )
            
        self.rooms_combo_box_layout.setCurrentWidget(self.rooms[rooms[0]])

        page_layout.addLayout(self.rooms_combo_box_layout)
        page.setLayout(page_layout)
        return page

    def update_rooms_combo_box_page(self):
        now_title = self.rooms_combo_box.currentText()
        months = get_last_6_months()
        if now_title in self.rooms:
            # 先移除后添加并设置当前展示
            last_line_graph_page = self.rooms[now_title]
            self.rooms_combo_box_layout.removeWidget(last_line_graph_page)
            
            one_room_record = self.get_history_records_from_db_by_whois(
                months[0],
                now_title
            )
            new_graph_page = build_line_graph(
                    '每月费用图', '月份','金额',
                    one_room_record
                )
            self.rooms[now_title] = new_graph_page
            self.rooms_combo_box_layout.addWidget(
                new_graph_page
            )
            self.rooms_combo_box_layout.setCurrentWidget(new_graph_page)
    def get_history_records_from_db_by_date(self, start_date):
        coordinate_dict = {}
        with Database().get_session() as session:
            for record in session.query(CalculatorHistory).filter(
                CalculatorHistory.create_date >= start_date,
                CalculatorHistory.whois.notin_(['公摊'])
            ).distinct(CalculatorHistory.whois).order_by(CalculatorHistory.create_date.asc()).all():
                #总计的费用是通过累加的方式计算，公摊费用项为0
                str_date = record.create_date.strftime('%Y-%m')
                if str_date in coordinate_dict:
                    coordinate_dict[str_date] += record.total_fee
                else:
                    coordinate_dict[str_date] = record.total_fee

        return self.fill_empty_coordinate(coordinate_dict)

    def get_history_average_public_fee_from_db_by_date(self, start_date):
        coordinate_dict = {}
        with Database().get_session() as session:
            for record in session.query(CalculatorHistory).filter(CalculatorHistory.create_date >= start_date) \
                .distinct(CalculatorHistory.whois).order_by(CalculatorHistory.create_date.asc()).all():
                coordinate_dict[record.create_date.strftime('%Y-%m')] = record.public_fee

        return self.fill_empty_coordinate(coordinate_dict)

    def get_history_roomers_from_db(self, start_date:str):
        roomers_list = []
        with Database().get_session() as session:
            for room in session.query(
                    CalculatorHistory
            ).filter(
                CalculatorHistory.create_date >= start_date,
                CalculatorHistory.whois.notin_(['公摊']), CalculatorHistory.whois.notlike('%无%')
            ).distinct(CalculatorHistory.whois).group_by(CalculatorHistory.whois).all():
                roomers_list.append(room.whois)
        return roomers_list

    def get_history_records_from_db_by_whois(self, start_date: str, whois: str):
        coordinate_dict = {}
        with Database().get_session() as session:
            for record in session.query(CalculatorHistory).filter(CalculatorHistory.create_date >= start_date,
                CalculatorHistory.whois == whois).order_by(CalculatorHistory.create_date.asc()).all():
                coordinate_dict[record.create_date.strftime('%Y-%m')] = record.total_fee

        return self.fill_empty_coordinate(coordinate_dict)

    def delete_history_record_from_db_by_date(self, start_date):
        with Database().get_session() as session:
            session.query(CalculatorHistory).filter(CalculatorHistory.create_date >= start_date).delete()
            session.commit()

    def add_one_history_record_to_db(self, one_info: dict):
        one_data = CalculatorHistory()
        for _k, _v in one_info.items():
            setattr(one_data, _k, _v)

        with Database().get_session() as session:
            session.add(one_data)
            session.commit()

    def fill_empty_coordinate(self, coordinates_info: dict):
        last_6months_list = get_last_6_months()

        new_coordinates_info = dict()
        for months in last_6months_list:
            if months not in coordinates_info:
                new_coordinates_info[months] = 0.0
            else:
                new_coordinates_info[months] = coordinates_info[months]

        return new_coordinates_info