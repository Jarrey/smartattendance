import json
import io
import traceback
import zipfile
from urllib.parse import quote
from flask import request, send_file, make_response
from flask_restful import Resource, reqparse
from datetime import datetime
import utils

class Attendance(Resource):
  def get(self):
    try:
      with open('data/base.data', 'r') as f:
        data = f.read()
        return make_response(data)
    except Exception as e:
      traceback.print_exc()
      return f"Error: {e}", 400


  def post(self):
    try:
      body = json.loads(request.data)
      from_date = datetime.strptime(body["from_date"], '%Y%m%d').date()
      to_date = datetime.strptime(body["to_date"], '%Y%m%d').date()
      data = body["data"].strip()
      with open('data/base.data', 'w') as f:
        f.write(data)

      # generate report
      people = utils.read_base_information()
      persons = []
      for name, person in people.items():
        person.set_date_range(from_date, to_date)
        has_result = person.calculate_data()
        while not has_result:
          has_result = person.calculate_data()
        person.generate_timesheet()
        person.generate_clock_record()
        persons.append(person)

      # compress files
      zip_buffer = io.BytesIO()
      with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        for file_name, data in [
          ('考勤数据表.csv', utils.covert_to_timesheet(persons).encode('utf-8')),
          ('打卡记录表.csv', utils.covert_to_clockrecord(persons).encode('utf-8'))
        ]:
          zip_file.writestr(file_name, data)
      zip_buffer.seek(0)
      filename = quote(f"{from_date.strftime('%Y%m%d')}_{to_date.strftime('%Y%m%d')}_考勤记录文件.zip")
      rv = send_file(zip_buffer, as_attachment=True, attachment_filename=filename, mimetype="application/x-zip-compressed")
      rv.headers['Content-Disposition'] += f"; filename*=utf-8''{filename}"
      return rv
    except Exception as e:
      traceback.print_exc()
      return f"Error: {e}", 400

class Date(Resource):
  def get(self):
    try:
      dates = {}
      with open('data/holiday.data', 'r') as f:
        dates['holiday'] = f.read()
      with open('data/shiftday.data', 'r') as f:
        dates['shiftday'] = f.read()
      return make_response(dates)
    except Exception as e:
      traceback.print_exc()
      return f"Error: {e}", 400

  def post(self):
    try:
      body = json.loads(request.data)
      day_type = body["type"]
      if day_type == "holiday":
        with open('data/holiday.data', 'w') as f:
          f.write(body["data"].strip())
      else:
        with open('data/shiftday.data', 'w') as f:
          f.write(body["data"].strip())
        print(day_type)
      return "OK"
    except Exception as e:
      traceback.print_exc()
      return f"Error: {e}", 400
