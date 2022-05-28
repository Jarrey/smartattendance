from datetime import datetime, timedelta


# get predefine holidays or shift-days
def read_days(day_file):
  days = []
  with open(day_file, 'r') as f:
    lines = f.readlines()
    for d in lines:
      if not d.startswith('#'):
        days.append(datetime.strptime(d.strip(), '%Y%m%d').date())
  return days


SPILT_LINE = '-' * 20
HOLIDAYS = read_days('data/holiday.data')
SHIFTDAYS = read_days('data/shiftday.data')
SERVER_VER = '1.0'
LOCAL_IP = '0.0.0.0'

DAILY_WORKING_HOURS = 8  # 正常每日工作时数
HALFDAY_WORKING_HOURS = DAILY_WORKING_HOURS / 2  # 正常半日工作时数
DAILY_LUNCH_HOURS = 1  # 午餐时数

DAY_START_TIME = datetime.strptime("8:00", "%H:%M")
DAY_START_OPTION_TIMES = [datetime.strptime("7:30", "%H:%M"), DAY_START_TIME]  # 正班上班时间
DAY_END_TIME = datetime.strptime("17:00", "%H:%M")  # 正班下班时间
DAY_OVERTIME_START_TIME = datetime.strptime("17:30", "%H:%M")  # 正班加班班时间
DAY_LUNCH_START_TIME = datetime.strptime("11:30", "%H:%M")  # 午餐开始时间
DAY_LUNCH_END_TIME = DAY_LUNCH_START_TIME + timedelta(hours=DAILY_LUNCH_HOURS)  # 午餐结束时间
TOL_RECORD_TIME = 15  # 打卡时间容差 +-15 分
WORKDAY_OVERTIME_MULTIPLIER = 1.5  # 工作日加班费系数
WEEKEND_OVERTIME_MULTIPLIER = 2  # 周末加班费系数

FULL_TIME_BONUS = 200  # 全勤奖金
MAX_CONTINUE_WORKING_DAYS = 20  # 最大连续工作天数
MAX_MONTHLY_WEEKEND_OVERTIME_HOURS = 30  # 月周末最大加班时数 32 小时, 实际控制在 30 小时内
MAX_MONTHLY_WORKDAY_OVERTIME_HOURS = 32  # 月工作日最大加班时数 36 小时, 实际控制在 32 小时内
MAX_DAILY_OVERTIME_HOURS = 3  # 日最大加班时数
MAX_OTHER_SALARY_MULTIPLIER = 1.5  # 其他工资最高所占总收入比例阈值系数
MIN_ATTENDANCE_RATE = 0.75  # 最少出勤人数比例
