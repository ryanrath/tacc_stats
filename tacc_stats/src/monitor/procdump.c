#include "procdump.h"

#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <dirent.h>
#include <stdlib.h>
#include <ctype.h>
#include <string.h>

#define MAX_PROCDUMP_SIZE (16*1024)

static void dumpProcFile( FILE *f, const char *filename ) {
    static char tbuf[MAX_PROCDUMP_SIZE];
    int d = open( filename, O_RDONLY, 0 );
    int siz = 0;
    int ret;
    if ( 0 > d ) return;

    while ( siz <= sizeof( tbuf ) - 1 && 0 < ( ret = read( d, tbuf + siz, sizeof( tbuf ) - 1 - siz ) )  ) {
        siz += ret;
    }
    close( d );
    if ( 0 >= siz ) return;

    fprintf( f, "%s\n%d\n", filename, siz );
    fwrite( tbuf, sizeof( char ), siz, f );
    fprintf( f, "\n\n" );
}


void collect_proc(struct stats_file *sf)
{
    /* added by charngda */
    /* archive stats & accounting info of processes of interest
       from /proc/<pid>/ */
    /* most of the code is from sysinfo.c of http://procps.sf.net */
    DIR *proc;
    if ( NULL != ( proc = opendir( "/proc" ) ) ) {
        struct dirent *ent;
        int ret;
        char *tbuf = malloc( MAX_PROCDUMP_SIZE );
        char tmpFileName[] = "/tmp/tacc_stats_XXXXXX";
        mktemp( tmpFileName );

        /* pipe the result to gzip + base64 */
        sprintf( tbuf, "/bin/gzip - | /usr/bin/base64 -w 0 > %s", tmpFileName );
        FILE *f = popen( tbuf, "w" );
        if ( f ) {
            while( ( ent = readdir( proc ) ) ) {
                char *cp;
                int fd, nthreads = 0;
                if ( !isdigit( ent->d_name[0] ) ) continue; /* not a process */

                /* get the uid and #threads of the process, and ignore
                   processes owned by uid < 1000 */
                sprintf( tbuf, "/proc/%s/status", ent->d_name );
                fd = open( tbuf, O_RDONLY, 0 );
                if ( fd < 0 ) continue;
                ret = read( fd, tbuf, MAX_PROCDUMP_SIZE - 1 );
                close( fd );
                if ( 0 >= ret ) continue;

                tbuf[ret] = '\0';
                cp = strstr( tbuf, "Threads:" );
                if ( cp ) {
                    if ( 1 != sscanf( cp + 8, "%d", &nthreads ) )
                        nthreads = 1;
                }

                cp = strstr( tbuf, "Uid:" );
                if ( !cp ) continue;
                if ( 1 == sscanf( cp + 4, "%d", &fd ) && 1000 < fd ) {
                    /* 1000 < fd  is a quick and dirty way to tell if a userId
                       in our CCR environment is a pseudo system user or a
                       human user. We do not capture system users' activities.
                     */
                    /* archive /proc/<pid>/status */
                    fprintf( f, "/proc/%s/status\n%d\n%s\n\n", ent->d_name, ret, tbuf );

                    /* if a process is NOT in disk sleep state */
                    if ( !strstr( tbuf, "(disk sleep)" ) ) {
                        /* then archive the following files under /proc */
                        const char *procfiles[] = {"cmdline", "environ", "numa_maps", "maps"};
                        for ( fd = 0; fd < sizeof( procfiles ) / sizeof( procfiles[0] ); ++fd ) {
                            sprintf( tbuf, "/proc/%s/%s", ent->d_name, procfiles[fd] );
                            dumpProcFile( f, tbuf );
                        }
                        /* if a process is in disk sleep state, trying to read
                           above files can end up in "disk sleep" limbo as well
                         */
                    }

                    const char *procfiles[] = {  "io", "stat", "stack"};
                    for ( fd = 0; fd < sizeof( procfiles ) / sizeof( procfiles[0] ); ++fd ) {
                        /* archive other files under /proc/<pid> */
                        sprintf( tbuf, "/proc/%s/%s", ent->d_name, procfiles[fd] );
                        dumpProcFile( f, tbuf );
                    }

                    if ( 1 < nthreads ) {
                        DIR *tasks;
                        sprintf( tbuf, "/proc/%s/task", ent->d_name );
                        if ( NULL != ( tasks = opendir( tbuf ) ) ) {
                            struct dirent *ent2;
                            const char *taskfiles[] = { "stat", "status", "sched", "stack"};
                            while( ( ent2 = readdir( tasks ) ) ) {
                                if ( !isdigit( ent2->d_name[0] ) ) continue; /* not a task */
                                for ( fd = 0; fd < sizeof( taskfiles ) / sizeof( taskfiles[0] ); ++fd ) {
                                    sprintf( tbuf, "/proc/%s/task/%s/%s", ent->d_name, ent2->d_name, taskfiles[fd] );
                                    dumpProcFile( f, tbuf );
                                }
                            }
                            closedir( tasks );
                        }
                    }
                }
            }
            pclose( f );
        }
        /* clean up */
        closedir( proc );
        free( tbuf );

        /* get the result of gzip + base64 */
        f = fopen( tmpFileName, "r" );
        if ( f ) {
            char *s = NULL;
            size_t n;
            if ( 0 < getline( &s, &n, f ) ) {
                /* and store them in the tacc_stats log */
                stats_file_mark( sf, "procdump %.*s", (int) strlen(s) - 1, s );
                free( s );
            }
            fclose( f );
        }
        unlink( tmpFileName );
    }
}
