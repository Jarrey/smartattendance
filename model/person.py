from datetime import timedelta, date
import random
import math

import constants as CS
import utils

TIMESHEET_CSV_HEADER = ["姓名", "底薪", "时薪", "出勤天数", "正班工时", "正班工资", "请假小时", "请假扣款", "平日加班工时", "平日加班费", "周末加班工时", "周末加班费",
                        "法假加班工时", "法假加班费", "带薪假", "带薪假工资", "奖金/津贴", "满勤", "应发工资"]
CLOCK_RECORD_CSV_HEADER = ["姓名", "打卡时间"]


class person:
  def __init__(self, name, base_salary, real_salary):
    self.name = name
    self.base_salary = float(base_salary)
    self.real_salary = float(real_salary)
    self.from_date = None
    self.to_date = None
    self.workday_count = self.weekend_count = self.month_workday_count = 0
    self.workdays = []
    self.weekends = []
    self.__reset()

  def set_date_range(self, from_date, to_date):
    if not isinstance(from_date, date) or not isinstance(to_date, date):
      raise TypeError("Only datetime.date type is allowed.")
    if from_date.year != to_date.year or from_date.month != to_date.month:
      raise Exception("The date range should be in the same month.")
    self.from_date = from_date
    self.to_date = to_date
    self.workday_count, self.workdays = utils.get_workdays(self.from_date, self.to_date)
    self.weekend_count, self.weekends = utils.get_weekends(self.from_date, self.to_date)

    # get first and last day of this month
    frist_day, last_day = utils.get_month_day_range(from_date)
    self.month_workday_count, _ = utils.get_workdays(frist_day, last_day)

  def __reset(self):
    self.is_full_time = False
    self.has_vacation = False
    self.has_overtime = False
    self.has_weekend_overtime = False
    self.has_paid_leave = False
    self.full_time_bonus = 0
    self.real_workdays = 0
    self.workday_salary = 0
    self.vacation_salary = 0
    self.overtime_salary = 0
    self.weekend_overtime_salary = 0
    self.workday_overtime_salary = 0
    self.other_salary = 0
    self.vacation_hours = 0
    self.workday_overtime = 0
    self.weekend_overtime = 0
    self.vacation_sheet = {}
    self.workday_overtime_sheet = {}
    self.weekend_overtime_sheet = {}
    self.clock_records = {}

  def __avg_salary_hourly(self):
    return round(self.base_salary / self.month_workday_count / CS.DAILY_WORKING_HOURS, 2)

  def __avg_salary_daily(self):
    return self.__avg_salary_hourly() * CS.DAILY_WORKING_HOURS

  def __calculate_data(self):
    self.__reset()
    # get the basic information including if overtime and full time working in month
    self.__calculate_personal_properties()
    self.__calculate_salaries()
    return self.__calculate_overtime()

  def __calculate_personal_properties(self):
    if self.real_salary - CS.FULL_TIME_BONUS > self.base_salary:
      self.is_full_time = random.choice([True] * 5 + [False])
      self.has_overtime = True
      self.has_vacation = not self.is_full_time
    elif self.real_salary - CS.FULL_TIME_BONUS == self.base_salary:
      self.is_full_time = random.choice([True] * 5 + [False])
      self.has_overtime = not self.is_full_time
      self.has_vacation = not self.is_full_time
    elif self.real_salary >= self.base_salary:
      self.is_full_time = False
      self.has_overtime = True
      self.has_vacation = True
    else:
      self.is_full_time = False
      self.has_overtime = random.choice([False] * 10 + [True])
      self.has_vacation = True
    self.has_paid_leave = random.choice([False] * 50 + [True])
    self.has_weekend_overtime = random.choice([False] * 5 + [True]) if self.has_overtime else False

  def __calculate_salaries(self):
    self.full_time_bonus = CS.FULL_TIME_BONUS * (1 if self.is_full_time else 0)
    self.vacation_hours = random.randint(1, self.workday_count) * CS.DAILY_WORKING_HOURS * (1 if self.has_vacation else 0)
    self.vacation_salary = self.vacation_hours * self.__avg_salary_hourly() * -1
    self.real_workdays = self.workday_count - self.vacation_hours / CS.DAILY_WORKING_HOURS - (1 if self.has_paid_leave else 0)
    self.workday_salary = self.real_workdays * self.__avg_salary_daily()
    self.overtime_salary = (self.real_salary - self.workday_salary - (self.__avg_salary_daily() if self.has_paid_leave else 0) - self.vacation_salary - (CS.FULL_TIME_BONUS if self.is_full_time else 0)) * (1 if self.has_overtime else 0)

  def __calculate_overtime(self):
    if self.has_overtime and self.overtime_salary > 0:
      # 随机计算得出周末加班时间, 以 0.5 天为单位计
      self.weekend_overtime = random.randint(1, min(math.floor(CS.MAX_MONTHLY_WEEKEND_OVERTIME_HOURS * 2 / CS.DAILY_WORKING_HOURS), self.weekend_count * 2)) * 0.5 * CS.DAILY_WORKING_HOURS * (1 if self.has_weekend_overtime else 0)
      self.weekend_overtime_salary = self.weekend_overtime * self.__avg_salary_hourly() * CS.WEEKEND_OVERTIME_MULTIPLIER

      # 随机计算出工作日加班时数, 范围确保不超过月加班最大限制时数
      self.workday_overtime = random.randint(1, min(CS.MAX_MONTHLY_WORKDAY_OVERTIME_HOURS - self.weekend_overtime, self.workday_count * CS.DAILY_WORKING_HOURS))
      self.workday_overtime_salary = self.workday_overtime * self.__avg_salary_hourly() * CS.WORKDAY_OVERTIME_MULTIPLIER

      # 加班天数与休假天数总和大于工作天数，则方案不成立
      max_workday_overtime_day = self.workday_overtime / CS.MAX_DAILY_OVERTIME_HOURS
      max_vacation_days = self.vacation_hours / CS.DAILY_WORKING_HOURS
      if self.workday_count < max_workday_overtime_day + max_vacation_days:
        return False

      # 随机加班费大于预计值, 则回归计算
      if self.overtime_salary < self.weekend_overtime_salary + self.workday_overtime_salary:
        return False
      # 得出其他费用进行填补, 其他费用建议不大于2500
      self.other_salary = self.overtime_salary - self.weekend_overtime_salary - self.workday_overtime_salary
      if self.other_salary >= max(1000, self.real_salary) * CS.MAX_OTHER_SALARY_MULTIPLIER or self.other_salary < 0:  # 其他类别工资建议不大于实际收入的一半
        return False
      self.overtime_salary = self.weekend_overtime_salary + self.workday_overtime_salary
      return True
    elif self.has_vacation and self.vacation_salary < 0:
      self.other_salary = self.real_salary - (self.workday_salary + self.vacation_salary + (self.__avg_salary_daily() if self.has_paid_leave else 0))
      if self.other_salary >= max(1000, self.real_salary) * CS.MAX_OTHER_SALARY_MULTIPLIER or self.other_salary < 0:  # 其他类别工资建议不大于实际收入的一半
        return False
      return True
    return False

  def calculate(self):
    has_result = self.__calculate_data()
    while not has_result:
      has_result = self.__calculate_data()

  # 基于加班请假时间值生成考勤表
  def generate_timesheet(self):
    vacation_sheet = {}
    if self.has_vacation:
      vacation_days = self.vacation_hours / CS.DAILY_WORKING_HOURS
      vacation_samples = random.sample(self.workdays, math.ceil(vacation_days))
      for vacation in vacation_samples:
        vacation_sheet[vacation] = CS.DAILY_WORKING_HOURS
      # 有半天假情况
      if vacation_days != len(vacation_samples):
        vacation_sheet[random.choice(vacation_samples)] = 0.5 * CS.DAILY_WORKING_HOURS

    workday_overtime_sheet = {}
    weekend_overtime_sheet = {}
    if self.has_overtime:
      # 随机取得加班天数, 不超过每日加班 3 小时计
      total_overtime = 0
      # 抽样将加班时数分配到每日
      while total_overtime < self.workday_overtime:
        workday = random.choice(self.workdays)
        while workday in workday_overtime_sheet or workday in vacation_sheet:
          workday = random.choice(self.workdays)

        overtime = CS.MAX_DAILY_OVERTIME_HOURS
        if total_overtime + overtime >= self.workday_overtime:
          workday_overtime_sheet[workday] = self.workday_overtime - total_overtime
          break
        else:
          workday_overtime_sheet[workday] = overtime
        total_overtime += overtime

      # 抽样将周末加班天数统计到周末时间表中
      if self.has_weekend_overtime:
        weekend_overtime_days = self.weekend_overtime / CS.DAILY_WORKING_HOURS
        weekend_overtime_samples = random.sample(self.weekends, math.ceil(weekend_overtime_days))
        for weekend in weekend_overtime_samples:
          weekend_overtime_sheet[weekend] = CS.DAILY_WORKING_HOURS
        # 有半天周末加班情况
        if weekend_overtime_days != len(weekend_overtime_samples):
          weekend_overtime_sheet[random.choice(weekend_overtime_samples)] = 0.5 * CS.DAILY_WORKING_HOURS

    # sort
    self.vacation_sheet = dict(sorted(vacation_sheet.items()))
    self.workday_overtime_sheet = dict(sorted(workday_overtime_sheet.items()))
    self.weekend_overtime_sheet = dict(sorted(weekend_overtime_sheet.items()))

  # 基于月时间表生成每日打卡记录
  def generate_clock_record(self):
    clock_records = {}
    paid_leave_day = None
    if self.has_paid_leave:
      paid_leave_day = random.choice(self.workdays)
      while paid_leave_day in self.vacation_sheet or paid_leave_day in self.weekend_overtime_sheet:
        paid_leave_day = random.choice(self.workdays)
    for day in self.workdays:
      if day in self.vacation_sheet.keys():
        if CS.DAILY_WORKING_HOURS - self.vacation_sheet[day] > 0:
          clock_records[day] = utils.random_start_end_time(CS.DAILY_WORKING_HOURS - self.vacation_sheet[day])
      else:
        if day in self.workday_overtime_sheet:
          clock_records[day] = utils.random_start_end_time(CS.DAILY_WORKING_HOURS + self.workday_overtime_sheet[day])
        else:
          if day != paid_leave_day:
            clock_records[day] = utils.random_start_end_time()

    for weekend in self.weekend_overtime_sheet:
      if CS.DAILY_WORKING_HOURS - self.weekend_overtime_sheet[weekend] > 0:
        clock_records[weekend] = utils.random_start_end_time(
          CS.DAILY_WORKING_HOURS - self.weekend_overtime_sheet[weekend])
      else:
        clock_records[weekend] = utils.random_start_end_time()
    self.clock_records = dict(sorted(clock_records.items()))

  def to_timesheet_row(self):
    workdays = self.workday_count - self.vacation_hours / CS.DAILY_WORKING_HOURS + self.weekend_overtime / CS.DAILY_WORKING_HOURS
    workday_hours = (workdays - self.weekend_overtime / CS.DAILY_WORKING_HOURS) * CS.DAILY_WORKING_HOURS
    return [self.name, self.base_salary, self.__avg_salary_hourly(),
            self.real_workdays, self.real_workdays * CS.DAILY_WORKING_HOURS, round(self.workday_salary, 2),
            self.vacation_hours,
            round(self.vacation_salary, 2),
            self.workday_overtime, round(self.workday_overtime_salary, 2),
            self.weekend_overtime, round(self.weekend_overtime_salary, 2),
            0.0, 0.0,
            1 if self.has_paid_leave else 0, self.__avg_salary_daily() if self.has_paid_leave else 0,
            round(self.other_salary, 2),
            self.full_time_bonus,
            self.real_salary
            ]

  def to_clockrecord_rows(self):
    rows = []
    for date, record in self.clock_records.items():
      rows.append([self.name, f'{date.strftime("%Y-%m-%d")} {record[0].strftime("%H:%M:%S")}'])
      rows.append([self.name, f'{date.strftime("%Y-%m-%d")} {record[1].strftime("%H:%M:%S")}'])
      rows.append([self.name, f'{date.strftime("%Y-%m-%d")} {record[2].strftime("%H:%M:%S")}'])
      rows.append([self.name, f'{date.strftime("%Y-%m-%d")} {record[3].strftime("%H:%M:%S")}'])
    return rows

  def __str__(self):
    vacation_sheet = '\n\t'.join([f'{k.strftime("%Y-%m-%d")}: {v} H' for k, v in self.vacation_sheet.items()])
    workday_overtime_sheet = '\n\t'.join(
      [f'{k.strftime("%Y-%m-%d")}: {v} H' for k, v in self.workday_overtime_sheet.items()])
    weekend_overtime_sheet = '\n\t'.join(
      [f'{k.strftime("%Y-%m-%d")}: {v} H' for k, v in self.weekend_overtime_sheet.items()])
    clock_record = '\n\t'.join(
      [f'{k.strftime("%Y-%m-%d")}: {v[0].strftime("%H:%M:%S")} - {v[1].strftime("%H:%M:%S")}' for k, v in
       self.clock_records.items()])
    return f"""
Name:            {self.name}
Base Salary:     {self.base_salary}
Full Time Bonus: {self.full_time_bonus}
Other Salary:    {self.other_salary}
Real Salary:     {self.real_salary}
Avg Salary (/H): {self.__avg_salary_hourly()}
Avg Salary (/D): {self.__avg_salary_daily()}
{CS.SPILT_LINE}
Date From: {self.from_date}
Date To:   {self.to_date}
{CS.SPILT_LINE}
Is Full Time: {self.is_full_time}
Has Overtime: {self.has_overtime}
Has Vacation: {self.has_vacation}
{CS.SPILT_LINE}
Workdays: {self.workday_count - self.vacation_hours / CS.DAILY_WORKING_HOURS + self.weekend_overtime / CS.DAILY_WORKING_HOURS} D
{CS.SPILT_LINE}
Vacations (H): {self.vacation_hours} H, {self.vacation_hours / CS.DAILY_WORKING_HOURS} D
Vacation Salary: {self.vacation_salary}
{CS.SPILT_LINE}
Overtime (Workday): {self.workday_overtime} H, Salary: {self.workday_overtime_salary}
Overtime (Weekend): {self.weekend_overtime} H {self.weekend_overtime / CS.DAILY_WORKING_HOURS} D, Salary: {self.weekend_overtime_salary}
Overtime: {self.weekend_overtime + self.workday_overtime} H
Overtime Salary: {self.overtime_salary}
{CS.SPILT_LINE}
Vacation Sheet:
\t{vacation_sheet}
{CS.SPILT_LINE}
Workday Overtime Sheet:
\t{workday_overtime_sheet}
{CS.SPILT_LINE}
Weekend Overtime Sheet:
\t{weekend_overtime_sheet}
{CS.SPILT_LINE}
Monthly Clock Records:
\t{clock_record}
"""
