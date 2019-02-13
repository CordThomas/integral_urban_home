""" Guiding insights:
    https://programminghistorian.org/en/lessons/creating-apis-with-python-and-flask
    https://www.techcoil.com/blog/how-to-deploy-python-3-flask-application-on-raspberry-pi-3-with-raspbian-stretch-lite-nginx-supervisor-virtualenv-and-gunicorn/
    Overview:
    This RESTful API to home intelligence provides a single API interface
    to data about solar production, energy consumption, air quality, local climatalogical
    information, home occupancy, and more.  The goal is that this will frame the
    data foundation to program elements of the integral urban home 2.0.
"""

import flask
from flask import request
import sqlite3
import logging
import json, configparser, os
from datetime import datetime, timedelta

application = flask.Flask(__name__)
application.config['DEBUG'] = True

config = configparser.ConfigParser()
config.read(os.getcwd() + '/config.ini')

air_db = sqlite3.connect(config['AIRQUALITY']['DB_PATH'], check_same_thread=False)
air_cursor = air_db.cursor()
air_query_all = 'SELECT * FROM p_environ'

solar_db = sqlite3.connect(config['SOLAR']['DB_PATH'], check_same_thread=False)
solar_cursor = solar_db.cursor()
solar_query_all = 'SELECT * FROM sunpower'

darksky_db = sqlite3.connect(config['DARKSKY']['DB_PATH'], check_same_thread=False)
darksky_cursor = darksky_db.cursor()
darksky_query_all = 'SELECT * FROM darksky'

def is_valid_date_format(date_string):
  """Confirm the date conforms to the format YYYY-MM-DD"""
  if len(date_string) != 10:
    return False
  try:
    datetime.strptime(date_string, '%Y-%m-%d')
  except ValueError:
    return False

  return True

def is_valid_time_format(time_string):
  """Confirm the time conforms to the format HH:MM:00"""
  if len(time_string) != 8:
    return False
  try:
    datetime.strptime(time_string, '%H:%M:00')
  except ValueError:
    return False

  return True

def calculate_daysago_range(daysago):
  """
  Calculate the start and end date for a specified
  number of days ago from today/now.
  :param daysago: An integer value indicating the days ago number of days
  :return: the start_date and end_date calculated based on the daysago value
  """
  if (daysago > 0):
    start_date = (datetime.today() - timedelta(days=daysago)).strftime("%Y-%m-%d")
    end_date = (datetime.today() - timedelta(days=(daysago - 1))).strftime("%Y-%m-%d")
    return start_date, end_date
  else:
    return "Error: The days ago value must be a positive value", 404

def filter_query_params(request_args):
  """Create the query where clause based on request parameters

  Acceptable request arguments include sdate and edate,
  param as a comma-delimited list"""
  where_clause = ''

  # Days ago is a means to request all the data from
  # the integer value of N daysago for a 24 hour period - it supersedes
  # suggesting date ranges.
  if ('daysago' in request_args):
    if (isinstance(request_args['daysago'], int)):
      start_date, end_date = calculate_daysago_range(request_args['daysago'])
      if (start_date[:5] != 'Error'):
        where_clause = where_clause + ' AND tdate >= \'' + start_date + '\''
        where_clause = where_clause + ' AND tdate <= \'' + end_date + '\''
  else:
    if ('sdate' in request_args):
      if (is_valid_date_format(request_args['sdate'])):
        where_clause = where_clause + ' AND tdate >= \'' + request_args['sdate'] + '\''
      else:
        return 'Error: Invalid date format (start date).  Date filters must be formatted as YYYY-MM-DD'

    if ('edate' in request_args):
      if (is_valid_date_format(request_args['edate'])):
        where_clause = where_clause + ' AND tdate <= \'' + request_args['edate'] + '\''
      else:
        return 'Error: Invalid date format (end date).  Date filters must be formatted as YYYY-MM-DD'

    if ('stime' in request_args):
      if (is_valid_time_format(request_args['stime'])):
        where_clause = where_clause + ' AND ttime >= \'' + request_args['stime'] + '\''
      else:
        return 'Error: Invalid date format (start time).  Time filters must be formatted as HH:MM:00'

    if ('etime' in request_args):
      if (is_valid_time_format(request_args['etime'])):
        where_clause = where_clause + ' AND ttime <= \'' + request_args['etime'] + '\''
      else:
        return 'Error: Invalid date format (end time).  Time filters must be formatted as HH:MM:00'

  if ('param' in request_args):
    param_clause = ''
    for param in request_args['param'].split(','):
      param_clause = param_clause + ' OR param = \'' + param + '\''
    where_clause = where_clause + ' AND (' + param_clause[4:] + ')'

  if (where_clause[:4] == ' AND'):
    return ' WHERE ' + where_clause[5:]
  else:
    return ' WHERE ' + where_clause

@application.route('/', methods=['GET'])
def home():
  return '<h1>The Integral Urban Home API</h1>'

@application.route('/api/v1/resources/air-quality/all', methods=['GET'])
def api_air_all():
  """
  get:
  Returns the complete set of air quality data collected at this location.
  :return: JOSN formatted list of air quality data including PM2.5, pressure and humidity
  """
  result = air_cursor.execute(air_query_all)
  items = [dict(zip([key[0] for key in air_cursor.description], row)) for row in result]
  return json.dumps(items)

@application.route('/api/v1/resources/air-quality/filtered', methods=['GET'])
def api_air_filtered():
  """
  get:
  Returns the filtered list of air quality data.  Filter options include
  sdate, edate, stime and etime for start and end dates and times - inclusive
  param to filter on the parameters returned including temp, humidity, pm25 and pressure
  :return: JSON formatted list of air quality data including PM2.5, pressure and humidity
  """
  query_clause = filter_query_params(request.args)
  if (query_clause[:6] == 'Error:'):
    return json.dumps(query_clause)
  result = air_cursor.execute(air_query_all + query_clause)
  items = [dict(zip([key[0] for key in air_cursor.description], row)) for row in result]
  return json.dumps(items)

@application.route('/api/v1/resources/solar/all', methods=['GET'])
def api_solar_all():
  """
  Returns the complete set of solar data collected at this location.
  :return: JSON formatted list of solar data including ep (produced),
  eu (used) and mp (mean or maybe max?).
  """
  result = solar_cursor.execute(solar_query_all)
  items = [dict(zip([key[0] for key in solar_cursor.description], row)) for row in result]
  return json.dumps(items)

@application.route('/api/v1/resources/solar/filtered', methods=['GET'])
def api_solar_filtered():
  """
  Returns the filtered list of solar data collected at this location.  Filter options include
  sdate, edate, stime and etime for start and end dates and times - inclusive
  :return: JSON formatted list of solar data including ep, eu and mp.
  """
  query_clause = filter_query_params(request.args)
  if (query_clause[:6] == 'Error:'):
    return json.dumps(query_clause)
  result = solar_cursor.execute(solar_query_all + query_clause)
  items = [dict(zip([key[0] for key in solar_cursor.description], row)) for row in result]
  return json.dumps(items)

@application.route('/api/v1/resources/darksky/all', methods=['GET'])
def api_darksky_all():
  """
  Returns the complete set of darksky data collected at this location.
  :return:  JSON formatted list of darksky data including for_visibility, for_uv_index,
  for_temperature, for_humidity, for_precip_intensity, etc.
  """
  result = darksky_cursor.execute(darksky_query_all)
  items = [dict(zip([key[0] for key in darksky_cursor.description], row)) for row in result]
  return json.dumps(items)

@application.route('/api/v1/resources/darksky/filtered', methods=['GET'])
def api_darksky_filtered():
  """
  Returns the filtered list of darksky data collected at this location.  Filter options include
  sdate, edate, stime and etime for start and end dates and times - inclusive
  param to filter on the parameters returned including all the atmospheric parameters
  like for_ozone, for_temperature, for_uv_index, etc.
  :return:  JSON formatted list of darksky data including those parameters listed above.
  """
  query_clause = filter_query_params(request.args)
  if (query_clause[:6] == 'Error:'):
    return json.dumps(query_clause)
  result = darksky_cursor.execute(darksky_query_all + query_clause)
  items = [dict(zip([key[0] for key in darksky_cursor.description], row)) for row in result]
  return json.dumps(items)

@application.errorhandler(404)
def page_not_found(e):
  return "<h1>404</h1><p>The resource could not be found.</p>", 404

if __name__ == "__main__":
  application.run(host='0.0.0.0')
