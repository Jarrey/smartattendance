import csv
import calendar
import io
import random
from datetime import timedelta
import constants as CS
from model.person import person, TIMESHEET_CSV_HEADER

# get all base salary information
def read_base_information():
  people = {}
  with open('data/base.data', 'r') as f:
    dialect = csv.Sniffer().sniff(f.read(1024))
    f.seek(0)
    base_data = csv.reader(f, dialect)
    for data in base_data:
      people[data[0]] = person(data[0].strip(), data[1].strip(), data[2].strip(), data[3].strip())

  return people

# check if the date is workday, including holiday checking
def is_workday(date):
  return date in CS.SHIFTDAYS or date not in CS.HOLIDAYS and date.weekday() < 5

def is_weekend(date):
  return date.weekday() >= 5 and date not in CS.HOLIDAYS and date not in CS.SHIFTDAYS

# get count of workday from date range
def get_workdays(from_date, to_date):
  days = []
  for day in [from_date + timedelta(x + 1) for x in range((to_date - from_date).days)]:
    if is_workday(day):
      days.append(day)
  return len(days), days

# get count of weekends from date range
def get_weekends(from_date, to_date):
  days = []
  for day in [from_date + timedelta(x + 1) for x in range((to_date - from_date).days)]:
    if is_weekend(day):
      days.append(day)
  return len(days), days

# get first and last day of the month
def get_month_day_range(date):
    first_day = date.replace(day=1)
    last_day = date.replace(day=calendar.monthrange(date.year, date.month)[1])
    return first_day, last_day

def random_start_end_time(during=CS.DAILY_WORKING_HOURS):
  if during > 0:
    if during == CS.HALFDAY_WORKING_HOURS:
      start_time = random.choice(CS.DAY_START_TIMES + [CS.DAY_LUNCH_END_TIME]) + timedelta(minutes=(random.choice([1, -1]) * random.randint(0, CS.TOL_RECORD_TIME)), seconds=random.randint(0, 59))
      end_time = start_time + timedelta(hours=during) + timedelta(minutes=(random.choice([1, -1]) * random.randint(0, CS.TOL_RECORD_TIME)), seconds=random.randint(0, 59))
    else:
      start_time = random.choice(CS.DAY_START_TIMES) + timedelta(minutes=(random.choice([1, -1]) * random.randint(0, CS.TOL_RECORD_TIME)), seconds=random.randint(0, 59))
      end_time = start_time + timedelta(hours=during + CS.DAILY_LUNCH_HOURS) + timedelta(minutes=(random.choice([1, -1]) * random.randint(0, CS.TOL_RECORD_TIME)), seconds=random.randint(0, 59))
    return start_time.time(), end_time.time()
  else:
    return None, None

def covert_to_timesheet(people):
  output = io.StringIO()
  writer = csv.writer(output, dialect='excel-tab', quoting=csv.QUOTE_NONNUMERIC)
  writer.writerow(TIMESHEET_CSV_HEADER)
  for p in people:
    writer.writerow(p.to_timesheet_row())
  return output.getvalue()

def covert_to_clockrecord(people):
  output = io.StringIO()
  writer = csv.writer(output, dialect='excel-tab', quoting=csv.QUOTE_NONNUMERIC)
  for p in people:
    for row in p.to_clockrecord_rows():
      writer.writerow(row)
  return output.getvalue()
