#include "slurm.h"

#include <string.h>
#include <sys/types.h>
#include <dirent.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

#ifndef CGROUPS_PATH
#define CGROUPS_PATH "/cgroup/cpuset/slurm"
#endif 

#define PATH_BUFLEN 10240

int parse_slurm_cgroups(struct stats_file *sf)
{
    struct dirent *ent, *sub;
    char path[PATH_BUFLEN];
    DIR *cgroupdir, *jobdir;
    FILE *fd;

    unsigned int uid, jobid;
    char *cpuset;
    size_t cpusetlen;

    cgroupdir = opendir(CGROUPS_PATH);

    if(!cgroupdir) 
    {
        return -1;
    }

    cpuset = NULL;
    cpusetlen = 0;

    while( (ent = readdir(cgroupdir) ) != NULL ) 
    {
        if(sscanf( ent->d_name, "uid_%u", &uid) == 1 )
        {
            snprintf(path, PATH_BUFLEN, CGROUPS_PATH "/%s", ent->d_name);

            jobdir = opendir(path);
            if(jobdir) 
            {
                while( ( sub = readdir(jobdir) ) != NULL ) 
                {
                    if( sscanf( sub->d_name, "job_%u", &jobid ) == 1 ) 
                    {
                        snprintf(path, PATH_BUFLEN, CGROUPS_PATH "/%s/%s/cpuset.cpus", ent->d_name, sub->d_name);
                        fd = fopen(path, "r");
                        if(fd)
                        {
                            if( getline(&cpuset, &cpusetlen, fd) != -1 ) {
                                // Note the trailing line feed on the cpuset string is not outputted
                                stats_file_mark(sf, "slurm %u %u %.*s", uid, jobid, strlen(cpuset)-1, cpuset);
                            }
                            fclose(fd);
                        }
                    }
                }
                closedir(jobdir);
            }
        }
    }

    closedir(cgroupdir);
    free(cpuset);

    return (cpusetlen == 0);
}

/* Gets the current job ids that are running based on the files provided by
 * Slurm in a specific directory */
int get_slurm_jobids(char *current_jobid)
{
    // setup directory structs
    struct dirent *ent;
    DIR *dir = opendir( JOBID_FILE_PATH );

    // get the hostname
    char formatStr[64];
    gethostname( formatStr, sizeof formatStr );

    // setup format string
    strcat( formatStr, "_%d.%*d" );

    // tmp vars
    int tmpId = 0;
    char tmpStr[16];

    // zero the jobid string
    current_jobid[0] = 0;

    if ( dir ) {

        // read all files in the directory
        while ( ( ent = readdir( dir ) ) != NULL ) {

            // check if filename matches the format, store id
            if ( sscanf( ent->d_name, formatStr, &tmpId ) ) {

                sprintf( tmpStr, "%d", tmpId );
                strcat( current_jobid, tmpStr );
                strcat( current_jobid, "," );

            }

        }

        closedir(dir);
    }

    if ( 0 == current_jobid[0] )
        strcpy( current_jobid, "0" );
    else
        current_jobid[strlen( current_jobid ) - 1] = 0;


    return 0;
}


