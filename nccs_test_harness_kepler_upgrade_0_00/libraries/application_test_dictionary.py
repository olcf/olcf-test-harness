#! /usr/env/python3 

# Python system imports.
import collections

# Python local imports

class ApplicationSubtestDictionary:

    """ 
    application_name : String variable
                       The name of the application.
    """

    @property
    def Tests(self):
        my_applications = []
        for key in  self.__myCollection.keys():
            my_applications.append(key)

        my_tests = []
        for app in my_applications:
            for subtest in self.__myCollection[app]:
                my_tests.append([app,subtest])

        return my_tests

    def __init__(self,
                 application_name=None):

        self.__myCollection  = collections.OrderedDict()

        if application_name != None:
            self.__myCollection[application_name] = []
        
        return

    def addAppSubtest(self,
                   name_of_application,
                   name_of_subtest):
        """ Adds an application and its subtest to the collection.


        Keyword arguments:
        name_of_application -- String variable, the name of the application.
        name_of_subtest -- String variable, the name of the subtest with respect to the application.
        """
        # Check if the application is not already in dictionary as a key,
        # otherwise add new key.
        if name_of_application not in self.__myCollection:
            self.__myCollection[name_of_application] = []

        # Check if the subtest is not already in the application list,
        # otherwise add a new subtest for that application.
        if name_of_subtest not in self.__myCollection[name_of_application]:
            (self.__myCollection[name_of_application]).append(name_of_subtest)

