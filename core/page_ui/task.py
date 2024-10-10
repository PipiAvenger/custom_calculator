# 任务枚举值
ADD_ITEM_TASK = 1
UPDATE_ITEM_TASK = 2
DELETE_ITEM_TASK = 3

#历史枚举值
UPDATE_HISTORY_RECORD_TASK = 11
class CTask:

    def __init__(self, data_info: dict, task_type = UPDATE_ITEM_TASK):
        self.data_info = data_info
        self.task_type = task_type