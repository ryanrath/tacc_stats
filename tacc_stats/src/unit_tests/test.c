#include "stats_file.h"
#include "dict.h"
#include "procdump.h"
#include "slurm.h"

#include <assert.h>
#include <string.h>
#include <stdlib.h>

/*
 * Overrides for system libary functions
 */
int gethostname (char *name, size_t len)
{
    if(len > sizeof("localhost") ) {
        memcpy(name, "localhost", sizeof("localhost") );
        return 0;
    }
    return -1;
}

/*
 * Stub function implementations
 */
struct stats_type *stats_type_get(const char *name)
{
    return NULL;
}
struct stats_type *stats_type_for_each(size_t *i)
{
    return NULL;
}
char *dict_for_each(struct dict *dict, size_t *i)
{
    return NULL;
}

/*
 * global variables
 */
char current_jobid[80];
double current_time;


void test_stats_file()
{
    int r;
    struct stats_file s;

    memset(&s, 0, sizeof(s));

    r = stats_file_mark(&s, "testmark1 %d %d", 1234134, 23423);

    assert(r == 0);
    assert( 0 == strcmp( s.sf_mark, "testmark1 1234134 23423" ) );

    r = stats_file_mark(&s, "testmark2 %s", "content");

    assert(r == 0);
    assert( 0 == strcmp( s.sf_mark, "testmark1 1234134 23423\ntestmark2 content" ) );

    free(s.sf_mark);
}

void test_procdump()
{
    struct stats_file s;

    memset(&s, 0, sizeof(s));

    collect_proc(&s);

    assert( s.sf_mark != NULL );
    assert( 0 == strncmp( s.sf_mark, "procdump ", strlen("procdump ") ) );

    free(s.sf_mark);
}

void test_slurm()
{
    struct stats_file s;
    memset(&s, 0, sizeof(s));

    parse_slurm_cgroups(&s);

    assert( s.sf_mark != NULL );

    assert( 0 == strcmp(s.sf_mark, "slurm 1241231 2314231 0-3") );

    free(s.sf_mark);

    get_slurm_jobids(&current_jobid[0]);

    assert( 0 == strcmp(current_jobid, "2911095,2911100"));
}

int main(int argc, char **argv)
{
    test_stats_file();
    test_procdump();
    test_slurm();

    return 0;
}
