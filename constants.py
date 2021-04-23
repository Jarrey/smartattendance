from datetime import datetime, timedelta

# get predefine holidays or shiftdays
def read_days(day_file):
  holidays = []
  with open(day_file, 'r') as f:
    holiday = f.readlines()
    for d in holiday:
      holidays.append(datetime.strptime(d.strip(), '%Y%m%d').date())
  return holidays

SPILT_LINE = '-' * 20
HOLIDAYS = read_days('data/holiday.data')
SHIFTDAYS = read_days('data/shiftday.data')
SERVER_VER = '1.0'
LOCAL_IP = '0.0.0.0'


DAILY_WORKING_HOURS = 8  # 正常每日工作时数
HALFDAY_WORKING_HOURS = DAILY_WORKING_HOURS / 2  # 正常半日工作时数
DAILY_LUNCH_HOURS = 1    # 午餐时数

# 正常上班时间
DAY_START_TIMES = [datetime.strptime("7:30", "%H:%M"), datetime.strptime("8:00", "%H:%M")]
DAY_LUNCH_START_TIME = datetime.strptime("11:30", "%H:%M")                      # 午餐开始时间
DAY_LUNCH_END_TIME = DAY_LUNCH_START_TIME + timedelta(hours=DAILY_LUNCH_HOURS)  # 午餐结束时间
TOL_RECORD_TIME = 15                # 打卡时间容差 +-15 分
WORKDAY_OVERTIME_MULTIPLIER = 1.5   # 工作日加班系数
WEEKEND_OVERTIME_MULTIPLIER = 2     # 周末加班系数

FULL_TIME_BONUS = 200               # 全勤奖金
MAX_CONTINUE_WORKING_DAYS = 20      # 最大连续工作天数
MAX_MONTHLY_OVERTIME_HOURS = 30     # 月最大加班时数, 规则是 36 小时, 实际不超过 30 小时计
MAX_DAILY_OVERTIME_HOURS = 3        # 日最大加班时数
MAX_OTHER_SALARY_MULTIPLIER = 0.6   # 其他工资最高所占总收入比例阈值系数
