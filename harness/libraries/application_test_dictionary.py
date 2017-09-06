#! /usr/env/python3 

# Python system imports.
import collections

# Python local imports

class ApplicationSubtestDictionary:

    """ 
    application_name : String variable
                       The name of the application.
    """

    MAX_NUMBER_OF_APPLICATIONS=1

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

    @property
    def ApplicationName(self):
        application_name = None
        if len(self.__myCollection) > 0:
            view_of_keys = self.__myCollection.keys()
            # The view_of_keys shpuld only have 1 key.
            for tmp_application_name in view_of_keys: 
                application_name = tmp_application_name
        return application_name

    def __init__(self,
                 application_name=None):

        self.__myCollection  = collections.OrderedDict()
        self.__numberOfApplications = 0

        if application_name != None:
            self.__addApplication(application_name)
            self.__myCollection[application_name] = []
        
        return

    def addAppSubtest(self,
                      name_of_application,
                      name_of_subtest):
        """ Adds an application and its subtest to the collection. Each
            collection can have at most 1 application.


        Keyword arguments:
        name_of_application -- String variable, the name of the application.
        name_of_subtest -- String variable, the name of the subtest with respect to the application.
        """

        # Check if the application is not already in dictionary as a key,
        # otherwise add new key.
        if name_of_application not in self.__myCollection:
            if self.__full:
                pass
            else:
                self.__myCollection[name_of_application] = []
                self.__numberOfApplications += 1

        # Check if the subtest is not already in the application list,
        # otherwise add a new subtest for that application.
        if name_of_subtest not in self.__myCollection[name_of_application]:
            (self.__myCollection[name_of_application]).append(name_of_subtest)

    def __full(self):
        full = False
        if self.__numberOfApplications >= self.MAX_NUMBER_OF_APPLICATIONS:
            full = True
        else:
            full = False
        return full

    def __addApplication(self,
                         name_of_application):
        if name_of_application not in self.__myCollection:
            if self.__full():
                pass
            else:
                self.__myCollection[name_of_application] = []
                self.__numberOfApplications += 1
        return

