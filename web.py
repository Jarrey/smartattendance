import traceback
from flask import make_response, render_template
from flask_restful import Resource

class Web(Resource):
  def get(self):
    try:
      headers = {'Content-Type': 'text/html'}
      return make_response(render_template("index.html"), 200, headers)
    except Exception as e:
      traceback.print_exc()
      return f"Error: {e}", 400

class MDate(Resource):
  def get(self):
    try:
      headers = {'Content-Type': 'text/html'}
      return make_response(render_template("m_date.html"), 200, headers)
    except Exception as e:
      traceback.print_exc()
      return f"Error: {e}", 400