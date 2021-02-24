#---------------------------------------------
# Jaguar
# OS - suse linux
# MPI - mpich 2
#---------------------------------------------
CXX = CC
CFLAGS = -g -DMPI_PROTOCOL -DMPICH_IGNORE_CXX_SEEK
LFLAGS = -g -DMPI_PROTOCOL -DMPICH_IGNORE_CXX_SEEK
#----------------------------------------------
src = main.cpp

.cpp.o:
	$(CXX) -c $(CFLAGS) -o $@ $<

obj = ${src:.cpp=.o}

executable = helloworld.x

${executable} : ${obj}
	${CXX} ${LFLAGS} ${obj} -o ${executable}

all:
	make clean
	make ${executable}

clean :
	rm -f ${executable}
	rm -f ${obj}
