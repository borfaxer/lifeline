#!/usr/bin/env python3

'''
  Log Loader
  Written by Jacob Sorensen
  05 November 2019

  A quick tool to load Humble Pie stats from its log into the
  MySQL DB on borfaxer.com
'''

import argparse
from datetime import datetime
import json
import logging
import mysql.connector
import os
import sys
#import time

description = "Log Loader"


def main():

  parser = argparse.ArgumentParser(description=description)
  parser.add_argument('--conf', required=False, default='/etc/conf/lifeline/lifeline_conf.json', help='config file path')

  args = parser.parse_args()

  config = json.load(open(args.conf, 'r'))

  # Double check the logging path exists, create if it doesn't

  if not os.path.exists(config['logging']['path']):
    os.makedirs(config['logging']['path'])

  log_file = config['logging']['path'] + '/' + config['logging']['filename']['log_loader']
  logging.basicConfig(filename=log_file,
                      format=config['logging']['format'],
                      level=logging.INFO)
  logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
  logging.info('Starting %s with logging level set to %s', description, logging.getLevelName(logging.getLogger().getEffectiveLevel()))
  logging.info('Read config file %s', args.conf)

  '''
    There are two activities to perform:
    1) Dig through the log and extract the data that
       should be in the DB
    2) Insert the values (ignoring duplicates)
  '''

  # Stage 1: Collect the data from logs
  hp_log_filename = log_file = config['logging']['path'] + '/' + config['logging']['filename']['humble_pie']

  # Stage 2: Insert the data
  db = mysql.connector.connect(user = config['mysql']['user'],
                               host = config['mysql']['host'],
                               password = config['mysql']['password'],
                               database = config['mysql']['database'])
  db_cursor = db.cursor()

  # IGNORE tells MySQL to skip duplicate rows without erroring

  insert_sql = ("INSERT IGNORE INTO lifeline_data"
                "(timestamp, ping, downwidth, upwidth, source_ip, source_machine, test_server)"
                "VALUES (%s, %s, %s, %s, %s, %s, %s)")

  source_ip = ''
  source_machine = config['source_machine']
  logging.info('Using \'%s\' as the source machine', source_machine)

  log_data = []

  with open(hp_log_filename, 'r') as hp_log:
    for line in hp_log:
      if 'Your IP: ' in line:
        old_source_ip = source_ip
        source_ip = line.split(':')[4].strip()
        if old_source_ip != source_ip:
          logging.info('Changing source_ip from %s to %s', old_source_ip, source_ip)
      elif "Could not report to " in line:
        logging.info('Parsing data: \'%s\'', '{' + line.split('{')[1])
        jd = json.loads('{' + line.split('{')[1])
        timestamp_object = datetime.fromtimestamp(jd['timestamp'])
        formatted_time = timestamp_object.strftime('%Y-%m-%d %H:%M:%S')
        data_tuple = (formatted_time,
                      jd['ping'],
                      jd['downwidth'],
                      jd['upwidth'],
                      source_ip,
                      source_machine,
                      jd['test_server'])
        logging.info('Inserting data for timestamp %s into %s:%s:%s', jd['timestamp'], config['mysql']['host'], config['mysql']['database'], 'lifeline_data')
        db_cursor.execute(insert_sql, data_tuple)

  db.commit()
  db_cursor.close()
  db.close()


if __name__ == '__main__':
  main()
