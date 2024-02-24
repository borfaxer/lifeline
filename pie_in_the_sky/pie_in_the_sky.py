#!/usr/bin/env python3

'''
  Pie In The Sky
  Written by Jacob Sorensen
  23 September 2019

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
import sys
import time

description = "Pie In The Sky"


def main():

  parser = argparse.ArgumentParser(description=description)
  parser.add_argument('--conf', required=False, default='/etc/conf/lifeline/lifeline_conf.json', help='config file path')

  args = parser.parse_args()

  config = json.load(open(args.conf, 'r'))

  # Double check the logging path exists, create if it doesn't

  if not os.path.exists(config['logging']['path']):
    os.makedirs(config['logging']['path'])

  log_file = config['logging']['path'] + '/' + config['logging']['filename']['pie_in_the_sky']
  logging.basicConfig(filename=log_file,
                      format=config['logging']['format'],
                      level=logging.INFO)
  logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
  logging.info('Starting %s with logging level set to %s', description, logging.getLevelName(logging.getLogger().getEffectiveLevel()))
  logging.info('Read config file %s', args.conf)

  '''
    - Set up REST API
    - Respond to data posted (insert into DB)
    - Send an alert text if no data is received in more than 3 minutes
      - Don't send more than 1 alert text until:
        Data has started to come in again
        It's been more than three hours
  '''

  '''
    Connect to Pie Hole & Store the data
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



if __name__ == '__main__':
  main()
