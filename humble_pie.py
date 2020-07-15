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
'''

import argparse
import json
import logging
import os
from pyspeedtest import SpeedTest
import sys
import time

description = "Humble Pie"
Mbps = 1024 * 1024

log_levels = {
  'CRITICAL'  : logging.CRITICAL,
  'ERORR'     : logging.ERROR,
  'WARNING'   : logging.WARNING,
  'INFO'      : logging.INFO,
  'DEBUG'     : logging.DEBUG
}

def close_handlers(logger):
  handlers = logger.handlers[:]
  for handler in handlers:
      handler.close()
      logger.removeHandler(handler)


def main():

  parser = argparse.ArgumentParser(description=description)
  parser.add_argument('--conf', required=False, default='/etc/conf/lifeline/lifeline_conf.json', help='config file path')

  args = parser.parse_args()

  config = json.load(open(args.conf, 'r'))

  # Double check the logging path exists, create if it doesn't

  if not os.path.exists(config['logging']['path']):
    os.makedirs(config['logging']['path'])

  log_file = config['logging']['path'] + '/' + config['logging']['filename']['humble_pie']
  logging.basicConfig(filename=log_file,
                      format=config['logging']['format'],
                      level=config['logging']['level'])
  logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
  logging.info('Starting %s with logging level set to %s', description, logging.getLevelName(logging.getLogger().getEffectiveLevel()))
  logging.info('Read config file %s', args.conf)

  '''
    There are two activities to perform:
    1) Do a connectivity / bandwidth check (speed test)
    2) Report the values (ping / download / upload, server, timestamp)
  '''
  stats = {}
  try:
    st = SpeedTest()
    stats['test_server'] = st.host
    stats['ping']        = st.ping()
    stats['downwidth']   = st.download() / Mbps
    stats['upwidth']     = st.upload() / Mbps
  except Exception as e:
    error_message = str(e)
    logging.error('Error: %s', error_message)
    stats['test_server'] = getattr(st, 'host', error_message.split('\'')[1])
    stats['ping']        = -1.0
    stats['downwidth']   = -1.0
    stats['upwidth']     = -1.0

  stats['timestamp']     = time.time()
  stats['source_machine']= config['source_machine']

  '''
    Connect to Pie In The Sky (PITS) & Report
  '''
  connected = False
  if 'pits_host' in config.keys():
    # TODO: connect and report
    logging.info('No PITS host to connect to.')
  else:
    config['pits_host'] = 'Missing PITS Host'

  '''
    Format the data in json so it'll be easy to pick out of the
    log if we need that and easy to pass to Pie In The Sky
  '''
  announce_results_string = 'Reported to {}'.format(config['pits_host'])
  if not connected:
    announce_results_string = 'Could not report to {}'.format(config['pits_host'])

  logging.info('%s: %s', announce_results_string, json.dumps(stats))

  close_handlers(logging)


if __name__ == '__main__':
  main()
