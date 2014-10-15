#ifndef SLURM_H_
#define SLURM_H_

#include "stats_file.h"

int parse_slurm_cgroups(struct stats_file *sf);
int get_slurm_jobids(char *current_jobid);

#endif
