import inspect

import matplotlib
from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QFrame, QComboBox, QStackedLayout
)
from functools import partial

#qt5折线图包
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import logging
logging.getLogger('matplotlib').setLevel(logging.WARNING)
# 预设置折线图的字体否则折线图会显示'口口'缺少字体的特征
matplotlib.rcParams['font.sans-serif'] = ['SimHei']  # 黑体
matplotlib.rcParams['axes.unicode_minus'] = False  # 显示负号

class BaseVItem(QFrame):
    def __init__(self, key_id: int = -1, key_name: str = '键名', default_value: str = '', parent_id = -1):
        super().__init__()
        self.key_id = key_id
        self.key_name = QLabel(key_name)
        self.key_value = QLineEdit(default_value)
        self.parent_id = parent_id
        one_item = QHBoxLayout()
        one_item.addWidget(self.key_name)
        one_item.addWidget(self.key_value)
        # 伸缩比5:4
        one_item.setStretch(0, 5)
        one_item.setStretch(1, 4)
        self.setLayout(one_item)

    def set_QLineEdit_callback(self, obj: object):
        # 回调函数存在方法则调用，没有则忽略
        if obj and hasattr(obj, 'func_callback'):
            # 不使用编辑完手动回车，
            self.key_value.textChanged.connect(partial(obj.func_callback, self))

    def get_item_name(self):
        """获取键名"""
        return self.key_name.text()

    def get_item_value(self):
        """获取键值"""
        return self.key_value.text()

    def set_item_value(self, value: str):
        """设置键值"""
        self.item_value.setText(value)

    @staticmethod
    def trans_dict_2_qt_frame_1(trans_dict: dict, frame: QFrame):
        """
        +-------------------------+
        | 上月用电度数: [值]         |
        | 本月用电度数: [值]         |
        | 公式:       [值]         |
        +-------------------------+
        根据字典
        :param trans_dict:带数据转换的键值对字典转换成上述布局框
        :param frame:
        :return:frame
        """
        frame_layout = QVBoxLayout()
        if not isinstance(trans_dict, dict):
            return frame

        for key_name, key_value in trans_dict.items():
            if not isinstance(key_name, str):
                continue

            if isinstance(key_value, dict):
                temp = QHBoxLayout()
                temp.addWidget(QLabel(key_name))
                temp.addWidget(BaseVItem.trans_dict_2_qt_frame_1(key_value, None))
                frame_layout.addWidget(temp)
                continue

            frame_layout.addWidget(BaseVItem(key_name=key_name, default_value=key_value))

        frame.setLayout(frame_layout)
        return frame

'''
class BaseComboBox:
    """
    下来选项框对应空间处理逻辑
    根据入参字典{
        "title1": {
            "func": function1,
            "stack_layout": stack_layout_obj
        }
    }
    pass
    :param trans_dict:带数据转换的键值对字典转换成上述布局框
    :param frame:
    :return:frame
    """
    def __init__(self, callback_dict: dict):
        self.combo_box = QComboBox()
        if callback_dict:
            self.combo_box.addItems(callback_dict.keys())
        for info in callback_dict.values():
            if isinstance(info, dict):
                func = info.get('func', None)
                stack_layout = info.get('stack_layout', None)
                if func and stack_layout:
                    self.combo_box.currentIndexChanged.connect(func)
'''


def build_line_graph(title_name: str, x_label_name: str, y_label_name: str, show_data: dict):
    """
    生成一个按照x月份y金额的折现图布局
    :param x_label_name:
    :param title_name: 标题
    :param x_label_name: y轴标题
    :param y_label_name: x轴标题
    :param show_data: 坐标组
    {
        "2024-09": "100.0",
        "2024-08": "125.0"
    }
    :return: frame
    """
    # Create a QFrame
    frame = QFrame()
    layout = QVBoxLayout()

    # Create a canvas and add it to the layout
    fig, ax = plt.subplots()

    # Prepare data for plotting
    x_labels = [x for x in show_data.keys()]
    y_values = [x for x in show_data.values()]

    # Plot the line chart
    ax.set_title(title_name)
    ax.set_xlabel(x_label_name)
    ax.set_ylabel(y_label_name, labelpad=-30, rotation=0, verticalalignment='bottom', y=1.02, x=3)
    ax.grid(False)
    ax.plot(x_labels, y_values, marker='o')

    for x, y in zip(x_labels, y_values):
        ax.annotate(f'{y}', (x, y), textcoords="offset points", xytext=(0, 5), ha='center')

    # Remove the top and right spines (the lines)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    canvas = FigureCanvas(fig)
    layout.addWidget(canvas)
    # Set layout to the widget
    frame.setLayout(layout)

    canvas.draw()
    return frame

def clean_figure_obj():
    plt.cla()
    plt.close("all")