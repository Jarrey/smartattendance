
import json
import io
import traceback
import zipfile
from flask import request, send_file
from flask_restful import Resource, reqparse
from datetime import datetime
import utils

class Attendance(Resource):
  def __init__(self):
    self.people = utils.read_base_information()

  def get(self):
    try:
      parser = reqparse.RequestParser()
      parser.add_argument('name', type=str)
      parser.add_argument('real_salary', type=float)
      parser.add_argument('from_date', type=lambda x: datetime.strptime(x, '%Y%m%d').date())
      parser.add_argument('to_date', type=lambda x: datetime.strptime(x, '%Y%m%d').date())
      args = parser.parse_args()

      person_name = args['name'].strip()
      if person_name in self.people:
        person = self.people[person_name]
        person.set_date_range(args['from_date'], args['to_date'])
        person.set_real_salary(args['real_salary'])
        person.generate_timesheet()
        person.generate_clock_record()
        return str(person)
    except Exception as e:
      traceback.print_exc()
      return f"Error: {e}", 400

  def post(self):
    try:
      body = json.loads(request.data)
      from_date = datetime.strptime(body["from_date"], '%Y%m%d').date()
      to_date = datetime.strptime(body["to_date"], '%Y%m%d').date()
      names_with_salary = body["people"]

      persons = []
      for name, salary in names_with_salary.items():
        if name in self.people:
          person = self.people[name]
          person.set_date_range(from_date, to_date)
          person.set_real_salary(salary)
          person.generate_timesheet()
          person.generate_clock_record()
          persons.append(person)

      # compress files
      zip_buffer = io.BytesIO()
      with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        for file_name, data in [('考勤数据表.csv', utils.covert_to_timesheet(persons).encode()), ('打卡记录表.csv', utils.covert_to_clockrecord(persons).encode())]:
          zip_file.writestr(file_name, data)
      zip_buffer.seek(0)
      return send_file(zip_buffer, as_attachment=True, attachment_filename='数据.zip', mimetype="application/zip")
    except Exception as e:
      traceback.print_exc()
      return f"Error: {e}", 400
