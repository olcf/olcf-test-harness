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

import sqlite3

from libraries import input_files
from libraries.status_file import StatusFile

#------------------------------------------------------------------------------

class StatusDatabase:
    """Class for accessing status information for runs."""

    #--------------------------------------------------------------------------

    def __init__(self):
        """Constructor - simple initializations."""

        #---Get some locations from harness.

        self.__input_file = input_files.rgt_input_file()
        self.__path_to_tests = self.__input_file.get_local_path_to_tests()

        self.__event_data = None
        self.__test_instance_data = None

        self.__event_names = None
        self.__event_fields = None

        self.__test_instance_fields = None

        self.__db = None
        self.__db_cursor = None

    #--------------------------------------------------------------------------

    def load(self):
        """Take a snapshot of the harness data and build database from this."""

        #---Initializations.

        stf = StatusFile #---Convenience variable.
        no_value = stf.NO_VALUE #---Convenience variable.

        #---Two python dicts that will be converted to sql databases.

        self.__event_data = {}
        self.__test_instance_data = {}

        self.__event_names = set(
            ['_'.join(stf.EVENT_DICT[event][1:3]) for event in stf.EVENT_LIST])

        self.__event_fields = set()

        self.__event_fields = set(stf.FIELDS_PER_TEST_INSTANCE +
                                  stf.FIELDS_PER_EVENT)

        per_event_fields = set(stf.FIELDS_PER_EVENT)

        #---PASS 1: loop to ingest information from disk files and compute
        #---some information.

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

                #---For every field of every event in the test instance,
                #---collect the values it can take.

                fields_values = {}

                #---Process events that were recorded for this test instance.

                for event_filename in event_filenames:

                    file_ = open(os.path.join(test_id_dir, event_filename), 'r')
                    line = file_.read()
                    file_.close()

                    line = re.sub('\n', '', line)
                    f_vs = [f_v.split('=') for f_v in line.split('\t')
                            if len(f_v.split('=')) == 2]

                    #---Record all field/value pairs for this event.

                    event_dict = {}
                    for f_v in f_vs:
                        field, value = tuple(f_v)
                        for field2 in stf.FIELDS_SPLUNK_SPECIAL:
                            if re.search('_' + field2 + '$', field):
                                continue
                        event_dict[field] = value
                        if field in fields_values:
                            fields_values[field].add(value)
                        else:
                            fields_values[field] = set([value])

                    #---ISSUE: should we check app, test,
                    #---test_id etc. for consistency.

                    #---ISSUE: should we extract event name from event filename

                    assert 'event_name' in event_dict, (
                        'Event file does not contain event name')

                    event_name = event_dict['event_name']

                    self.__event_data[app][test][test_id][event_name] = (
                        event_dict)

                    self.__event_names.add(event_name)

                    self.__event_fields.union(set(list(event_dict.keys())))

                #---Find fields that can have nonuniform values across
                #---the events of a test instance.

                for field, values in fields_values.items():
                    if len(values) > 1:
                        per_event_fields.add(field)

        #---Finish building global field lists.

        #---Test instance fields are composed of fields that have
        #---invariant values across events of a test instance,
        #---plus the others which are replicated by event name.

        self.__test_instance_fields = self.__event_fields.difference(
            per_event_fields)
        for field in per_event_fields:
            for event_name in self.__event_names:
                #---For each event-specific field, give the field a name
                #---that denotes the event name.
                new_field = event_name + '_' + field
                self.__test_instance_fields.add(new_field)

        #---Initialize sqlite database, tables.

        self.__db = sqlite3.connect(':memory:')
        self.__db_cursor = self.__db.cursor()
        self.__db_cursor.execute(
            'CREATE TABLE events(id INTEGER PRIMARY KEY, ' +
            ' TEXT, '.join(list(self.__event_fields)) + ' TEXT)')
        self.__db_cursor.execute(
            'CREATE TABLE test_instances(id INTEGER PRIMARY KEY, ' +
            ' TEXT, '.join(list(self.__test_instance_fields)) + ' TEXT)')

        #---PASS 2: form test_instance data; make all records consistent.

        for app in self.__event_data:
            for test in self.__event_data[app]:
                self.__test_instance_data.setdefault(
                    app, {}).setdefault(test, {})
                for test_id in self.__event_data[app][test]:
                    test_instance_dict = {}

                    events = self.__event_data[app][test][test_id]

                    #---Add events to event table in database.

                    for event_name in events:

                        event_dict = events[event_name]

                        for field in self.__event_fields.difference(
                                set(list(event_dict.keys()))):
                            #---Add missing fields (as empty).
                            #---WARNING: dynamic update - should be ok.
                            event_dict[field] = no_value

                        #---Add to database.

                        self.__insert_into_db('events',
                                              self.__event_fields, event_dict)

                    #---Add missing events (as having fields with (mostly)
                    #---empty values) to event table in database.

                    for event_name in self.__event_names.difference(
                            set(list(events.keys()))):
                        event_dict = {f: no_value for f in self.__event_fields}
                        #---ISSUE: should we fill more fields here.
                        event_dict['app'] = app
                        event_dict['test'] = test
                        event_dict['test_id'] = test_id
                        event_dict['test_instance'] = ','.join([app, test,
                                                                test_id])
                        #---Add to database.

                        event_dict['event_name'] = event_name
                        #---WARNING: dynamic update - should be ok.
                        events[event_name] = event_dict

                        self.__insert_into_db('events',
                                              self.__event_fields, event_dict)

                    #---Get fields, values for test instance.

                    for event_name, event_dict in events.items():

                        #---Add fields for current event.

                        for field, value in event_dict.items():

                            #---For each event-specific field, give the field a
                            #---name that denotes the event name.
                            new_field = (event_name + '_' + field
                                     if field in per_event_fields else field)

                            #---Add to dict if not yet there or there but null.
                            if not new_field in test_instance_dict:
                                test_instance_dict[new_field] = value
                            elif test_instance_dict[new_field] == no_value:
                                test_instance_dict[new_field] = value

                    #---Add any missing fields (as having empty values).

                    for field in self.__test_instance_fields:
                        if not field in test_instance_dict:
                            test_instance_dict[field] = no_value

                    #---Add test_instance data to database.

                    self.__test_instance_data[app][test][test_id] = (
                        test_instance_dict)

                    #---Add to database.

                    self.__insert_into_db('test_instances',
                                          self.__test_instance_fields,
                                          test_instance_dict)

        return self #---for chaining.

    #--------------------------------------------------------------------------

    def __insert_into_db(self, table_name, fields, values_dict):
        """Create a record in the sqlite database."""

        self.__db_cursor.execute(
            'INSERT INTO ' + table_name + '(' +
            ','.join(list(fields)) + ') ' +
            'VALUES(:' +
            ', :'.join(list(fields)) + ')',
            values_dict)
        self.__db.commit()

    #--------------------------------------------------------------------------

    def perform_query(self, query_string):
        """Execute a query against the database, return result."""

        self.__db_cursor.execute(query_string)

        result = ''

        for row in self.__db_cursor.fetchall():
            result += ' '.join([str(f) for f in row]) + '\n'

        return result

    #--------------------------------------------------------------------------

    def print_query(self, query_string):
        """Execute a query and output the result."""

        sys.stdout.write(self.perform_query(query_string))

        return self  #---for chaining.

    #--------------------------------------------------------------------------

#------------------------------------------------------------------------------
