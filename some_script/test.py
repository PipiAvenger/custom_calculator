import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QComboBox


class ExampleApp(QWidget):
    def __init__(self):
        super().__init__()

        # 设置窗口标题和大小
        self.setWindowTitle('下拉框示例')
        self.setGeometry(100, 100, 300, 200)

        # 创建布局
        layout = QVBoxLayout()

        # 创建下拉框
        self.combo_box = QComboBox(self)
        self.combo_box.addItems(['1', '2'])
        self.combo_box.currentIndexChanged.connect(self.update_content)

        # 创建默认显示1的内容
        self.content_label = QLabel('', self)
        self.update_content()

        # 添加控件到布局
        layout.addWidget(self.combo_box)
        layout.addWidget(self.content_label)

        # 设置布局
        self.setLayout(layout)

    def update_content(self):
        # 根据选择更新内容
        choice = self.combo_box.currentText()
        if choice == '1':
            self.content_label.setText("这是选项1")
        elif choice == '2':
            self.content_label.setText("这是选项2")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    example = ExampleApp()
    example.show()
    sys.exit(app.exec_())
