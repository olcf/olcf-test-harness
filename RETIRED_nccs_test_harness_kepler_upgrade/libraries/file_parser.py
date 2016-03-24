class a_file_parser:
    def __init__(self,finalfile,originalfile,rg_array):
        self.__finalfile = finalfile
        self.__originalfile = originalfile
        self.__originalfilelines = ''
        self.__rg_array = rg_array

        #
        # Read the lines of the original file.
        #
        templatefileobject = open(self.__originalfile,"r")
        self.__originalfilelines = templatefileobject.readlines()
        templatefileobject.close()


    def parse_file(self):
        #
        # Here is where we actually parse the file.
        #
        fileobject = open(self.__finalfile,"w")
        for record1 in self.__originalfilelines:
            for (regexp,text1) in self.__rg_array:
                record1 = regexp.sub(text1,record1)
            fileobject.write(record1)
        fileobject.close()

    def parseForRegularExpressions(self):
        FOUND_PATTERN = False
        matching_records  = []
        for record1 in self.__originalfilelines:
            for (regexp,text1) in self.__rg_array:
                if regexp.search(record1) :
                   matching_records = matching_records + [text1]
        return matching_records
