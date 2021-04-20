#!/usr/bin/python3

import argparse
from flask import Flask
from flask_restful import Api, Resource

from attendance import Attendance
from constants import *


desc = f"Smart Attendance System {SERVER_VER}"
class Version(Resource):
  def get(self):
    return desc

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description=desc)
  parser.add_argument('--host', '-H', help='Host(IP) of server', default=LOCAL_IP)
  parser.add_argument('--port', '-p', help='Port of server', default=18088, type=int)
  parser.add_argument('--debug', '-d', help='Enable debug mode', default=False, action='store_true')

  args = parser.parse_args()

  app = Flask(__name__)
  api = Api(app)
  api.add_resource(Version, '/version')
  api.add_resource(Attendance, '/attendance')
  app.run(host=args.host, port=args.port, debug=args.debug)
