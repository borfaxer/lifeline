#!/usr/bin/env python

'''
  Humble Pie
  Written by Jacob Sorensen
  22 September 2019

  I wanted to write this in Python 3, but
  got stopped by two things:
  1) I used pyspeedtest as a shortcut, and it's only for Python 2
     (I will either write my own or update the code to work in
      Python 3)
  2) My hosting provider, Bluehost, only has Python 2 available.
     They should have Python 3 available before too long, at
     which point I can update.

  TODO: shove most of the settings into a config file and read
  that instead of getting parameters.
'''

import argparse
import json
import logging
import os
import pyspeedtest
import sys
import time

description = 'Humble Pie'
log_path = '/var/log/lifeline'
log_file = log_path + '/humble_pie.log'
default_log_level = logging.INFO
log_format = '%(asctime)s %(levelname)s: %(message)s'
Mbps = 1024 * 1024


def main():

  # Double check the logging path exists, create if it doesn't
  log_path
  if not os.path.exists(log_path):
    os.makedirs(log_path)

  parser = argparse.ArgumentParser(description=description)
  parser.add_argument('--pits_host', required=False, default = None, help='Host to report results to')
  parser.add_argument('--log_level', required=False, default=default_log_level, help='Log level to record')

  args = parser.parse_args()

  logging.basicConfig(filename=log_file, format=log_format, level=default_log_level)
  logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
  logging.info('Starting %s with logging level set to %s', description, default_log_level)

  '''
    There are two activities to perform:
    1) Do a connectivity / bandwidth check (speed test)
    2) Report the values (ping / download / upload, server, timestamp)
  '''
  st = pyspeedtest.SpeedTest()
  stats = dict(test_server = st.host)
  stats['ping']      = st.ping()
  stats['downwidth'] = st.download() / Mbps
  stats['upwidth']   = st.upload() / Mbps
  stats['timestamp'] = time.time()

  '''
    Connect to Pie In The Sky (PITS) & Report
  '''
  connected = False
  if args.pits_host:
    # TODO: connect and report
    logging.info('No PITS host to connect to.')
  else:
    args.pits_host = 'Missing PITS Host'

  '''
    Format the data in json so it'll be easy to pick out of the
    log if we need that and easy to pass to Pie In The Sky
  '''
  announce_results_string = 'Reported to {}'.format(args.pits_host)
  if not connected:
    announce_results_string = 'Could not report to {}'.format(args.pits_host)

  logging.info('%s: %s', announce_results_string, json.dumps(stats))



if __name__ == '__main__':
  main()
