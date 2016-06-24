#! /usr/bin/env python
"""
-------------------------------------------------------------------------------
File:   status_database.py
Author: Wayne Joubert (joubert@ornl.gov)
National Center for Computational Sciences, Scientific Computing Group.
Oak Ridge National Laboratory
Copyright (C) 2016 Oak Ridge National Laboratory, UT-Battelle, LLC.
-------------------------------------------------------------------------------
"""

import os
import sys
import re
import pprint

import sqlite3

from libraries import input_files
from libraries.status_file import StatusFile

#------------------------------------------------------------------------------

class StatusDatabase:
    """Class for accessing status information for runs."""

    #--------------------------------------------------------------------------

    def __init__(self):
        """Constructor."""

        self.__input_file = input_files.rgt_input_file()
        self.__path_to_tests = self.__input_file.get_local_path_to_tests()

        self.__event_data = None
        self.__test_instance_data = None

        self.__event_names = None
        self.__event_fields = None

    #--------------------------------------------------------------------------

    def load(self):
        """Take a snapshot of the harness data and build database form this."""

        #---Initializations.

        SF = StatusFile #---Convenience.
        NO_VALUE = SF.NO_VALUE #---Convenience

        self.__event_data = {}
        self.__test_instance_data = {}

        self.__event_names = set(
            ['_'.join(SF.EVENT_DICT[event][1:3]) for event in SF.EVENT_LIST])

        self.__event_fields = set()

        self.__event_fields = set(SF.FIELDS_PER_TEST_INSTANCE +
                                  SF.FIELDS_PER_EVENT)

        per_event_fields = set(SF.FIELDS_PER_EVENT)

        #---Loop to ingest information from disk files.

        for test_info in self.__input_file.get_tests():
            app, test = test_info[0:2]

            self.__event_data.setdefault(app, {}).setdefault(test, {})

            status_dir = os.path.join(self.__path_to_tests, app, test, 'Status')
            test_ids = ([d for d in os.listdir(status_dir)
                         if re.search(r'^[0-9.]+$', d)
                         and os.path.isdir(os.path.join(status_dir, d))]
                        if os.path.exists(status_dir) else [])

            #---Loop over test instances for this app and test.

            for test_id in test_ids:
                self.__event_data[app][test][test_id] = {}

                test_id_dir = os.path.join(status_dir, test_id)

                event_filenames = [f for f in os.listdir(test_id_dir) if
                                   os.path.isfile(os.path.join(test_id_dir, f))
                                   and re.search(r'^Event_[0-9]+_', f)]

                fields_values = {}

                #---Process events that were recorded for this test instance.

                for event_filename in event_filenames:

                    file_ = open(os.path.join(test_id_dir, event_filename), 'r')
                    line = file_.read()
                    file_.close()

                    line = re.sub('\n', '', line)
                    fvs = [fv.split('=') for fv in line.split('\t') 
                                         if len(fv.split('=')) == 2]

                    event_dict = {}
                    for fv in fvs:
                        f, v = tuple(fv)
                        for f2 in SF.FIELDS_SPLUNK_SPECIAL:
                            if re.search('_' + f2 + '$', f):
                                continue
                        event_dict[f] = v
                        if f in fields_values:
                            fields_values[f].add(v)
                        else:
                            fields_values[f] = set([v])

                    event_name = event_dict['event_name']

                    self.__event_data[app][test][test_id][event_name] = (
                        event_dict)

                    self.__event_names.add(event_name)

                    self.__event_fields.union(set(list(event_dict.keys())))

                #---Collect fields that can have nonuniform values across
                #---the events of a test instance.

                for f, vs in fields_values.items():
                    if len(vs) > 1:
                        per_event_fields.add(f)

        #---Finish building global field lists.

        self.__test_instance_fields = self.__event_fields.difference(
                                          per_event_fields)
        for f in per_event_fields:
            for event_name in self.__event_names:
                #---For each event-specific field, give the field a name
                #---that denotes the event name.
                self.__test_instance_fields.add(event_name+'_'+f)

        #---Initialize sqlite database, tables.

        self.db = sqlite3.connect(':memory:')
        self.db_cursor = self.db.cursor()
        self.db_cursor.execute(
            'CREATE TABLE events(id INTEGER PRIMARY KEY, ' +
            ' TEXT, '.join(list(self.__event_fields)) + ' TEXT)')
        self.db_cursor.execute(
            'CREATE TABLE test_instances(id INTEGER PRIMARY KEY, ' +
            ' TEXT, '.join(list(self.__test_instance_fields)) + ' TEXT)')

        #---Second loop through data.

        for app in self.__event_data:
            for test in self.__event_data[app]:
                self.__test_instance_data.setdefault(
                    app, {}).setdefault(test, {})
                for test_id in self.__event_data[app][test]:
                    test_instance_dict = {}

                    events = self.__event_data[app][test][test_id]

                    #---Add events to database.

                    for event_name in events:

                        event_dict = events[event_name]

                        for f in self.__event_fields.difference(
                              set(list(event_dict.keys()))):
                            #---Add missing fields (as empty).
                            #---WARNING: dynamic update.
                            event_dict[f] = NO_VALUE

                        self.__insert_into_db('events',
                            self.__event_fields, event_dict)

                    #---Add missing events (as having (mostly) empty fields).

                    for event_name in self.__event_names.difference(
                          set(list(events.keys()))):
                        event_dict = {f: NO_VALUE for f in self.__event_fields}
                        #---ISSUE: not exactly clear what is best strategy here.
                        event_dict['app'] = app
                        event_dict['test'] = test
                        event_dict['test_id'] = test_id
                        event_dict['test_instance'] = ','.join([app, test,
                                                                test_id])
                        event_dict['event_name'] = event_name
                        #---WARNING: dynamic update.
                        events[event_name] = event_dict

                        self.__insert_into_db('events',
                            self.__event_fields, event_dict)

                    #---Get fields, values for test instance.

                    for event_name, event_dict in events.items():
                        for f, v in event_dict.items():

                            #---For each event-specific field, give the field a
                            #---name that denotes the event name.
                            f_alt = (event_name + '_' + f 
                                  if f in per_event_fields else f)

                            #---Add to dict if not there or is there but null.
                            if not f_alt in test_instance_dict:
                                test_instance_dict[f_alt] = v
                            elif test_instance_dict[f_alt] == NO_VALUE:
                                test_instance_dict[f_alt] = v

                    #---Add test_instance data to database.

                    self.__test_instance_data[app][test][test_id] = (
                        test_instance_dict)

                    self.__insert_into_db('test_instances',
                        self.__test_instance_fields, test_instance_dict)

        return self  #---for chaining.

    #--------------------------------------------------------------------------

    def __insert_into_db(self, table_name, fields, values_dict):
        """Create a record in the sqlite database."""
        self.db_cursor.execute(
            'INSERT INTO ' + table_name + '(' +
            ','.join(list(fields)) + ') ' +
            'VALUES(:' +
            ', :'.join(list(fields)) + ')',
            values_dict)
        self.db.commit()

    #--------------------------------------------------------------------------

    def perform_query(self, query_string):
        """Execute a query."""

        self.db_cursor.execute(query_string)

        result = ''

        for row in self.db_cursor.fetchall():
            result += ' '.join([str(f) for f in row]) + '\n'

        return result

    #--------------------------------------------------------------------------

    def print_query(self, query_string):
        """Execute a query and output the result."""

        sys.stdout.write(self.perform_query(query_string))

        return self  #---for chaining.

    #--------------------------------------------------------------------------

#------------------------------------------------------------------------------
