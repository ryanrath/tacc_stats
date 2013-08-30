#include "slurm.h"

#include <string.h>
#include <sys/types.h>
#include <dirent.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

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


