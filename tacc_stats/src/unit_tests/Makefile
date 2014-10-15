
CPPFLAGS= -D_GNU_SOURCE \
		  -DSTATS_PROGRAM='"unittest"' \
		  -DCGROUPS_PATH='"./fakefs/cgroup/cpuset/slurm"' \
		  -DJOBID_FILE_PATH='"./fakefs/var/spool/slurmd"' \
		  -DSTATS_VERSION='"1.0.0"' \
		  -I../monitor 

CFLAGS = -Wall -ggdb 
VPATH=../monitor

OBJS= test.o \
	  stats_file.o \
	  procdump.o \
	  slurm.o

EXEC=test

all: unittest memtest

$(EXEC): $(OBJS)

.PHONY: memtest
memtest: unittest
	valgrind --leak-check=full ./$(EXEC)

.PHONY: unittest
unittest: $(EXEC) fakefs
	./$(EXEC)


fakefs: fakefs.tar.gz
	tar -xf $<

.PHONY: clean
clean:
	rm -r fakefs
	rm $(OBJS) $(EXEC)

