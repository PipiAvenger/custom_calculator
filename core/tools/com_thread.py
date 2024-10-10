import threading
import time
import logging

class EventThread(threading.Thread):
    def __init__(self, name='eventThread', target=None, event_flag=False, daemon = True, *args, **kwargs):
        """
        :param name: 线程名
        :param target: 线程中要执行的目标函数
        :param event_flag: 是否持续调用目标函数直到事件终止
        :param daemon: 是否启用守护线程，默认设置为守护线程
        :param args: 目标函数的参数
        :param kwargs: 目标函数的关键词参数
        """
        super(EventThread, self).__init__()
        self.name = name
        self.target = target
        # 守护线程
        self.daemon = daemon
        self.args = args
        self.kwargs = kwargs
        self.event_flag = event_flag  # 是否持续调用函数的标志
        self.stop_event = threading.Event()  # 用于控制线程退出的事件

    def run(self):
        """线程启动时执行的函数"""
        if not self.target:
            raise ValueError("target function must be provided")

        try:
            if self.event_flag:
                # 持续调用函数，直到 stop_event 被设置
                while not self.stop_event.is_set():
                    self.target(*self.args, **self.kwargs)
            else:
                # 仅调用一次目标函数
                self.target(*self.args, **self.kwargs)
        except Exception as e:
            logger = logging.getLogger()
            logger.critical(f'{self.name}线程捕捉到异常:{e}')

    def slow_stop(self):
        """触发事件标志，用于停止线程"""
        self.stop_event.set()
        self.join()


# 示例任务函数
def example_task():
    print("Task running...")
    time.sleep(1)


if __name__ == "__main__":
    # 场景1：仅调用函数一次
    print("---- Scenario 1: Single Execution ----")
    single_thread = EventThread(target=example_task)
    single_thread.start()
    single_thread.join()

    # 场景2：持续调用函数，直到触发退出事件
    print("\n---- Scenario 2: Continuous Execution with Event ----")
    continuous_thread = EventThread(target=example_task, event_flag=True)
    continuous_thread.start()

    # 让函数执行一段时间
    time.sleep(5)

    # 触发停止事件
    continuous_thread.stop()
    continuous_thread.join()  # 等待线程安全退出
