from datetime import datetime, timedelta

def get_last_6_months():
    """
    返回过去12个月的字符串
    :return:
    """
    months = []
    current_date = datetime.now()
    for i in range(6):
        month = (current_date - timedelta(days=current_date.day)).strftime('%Y-%m')
        months.append(month)
        current_date = current_date.replace(day=1) - timedelta(days=1)  # Move to the last day of the previous month
    months.reverse()
    return months

