#! /usr/env/python3 

# Python system imports.


# Python local imports

class ApplicationTestDictionary:

    def __init__(self):
        return

    def addAppTest(name_of_application,
                   name_of_test):
        message = "Adding Test: {}, {}\n".format(name_of_application,name_of_test)
        print(message)
