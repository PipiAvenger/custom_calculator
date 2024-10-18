import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QLabel, QVBoxLayout, QWidget

class MyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 设置窗口标题和几何形状
        self.setWindowTitle('My QMainWindow Example')
        self.setGeometry(100, 100, 800, 600)

        # 创建中央小部件
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # 设置布局
        layout = QVBoxLayout(central_widget)
        layout.addWidget(QLabel('欢迎使用 QMainWindow'))

        # 创建菜单栏
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('文件')

        # 创建菜单项
        exit_action = QAction('退出', self)
        exit_action.triggered.connect(self.close)  # 连接退出动作
        file_menu.addAction(exit_action)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MyMainWindow()
    main_window.show()
    sys.exit(app.exec_())
