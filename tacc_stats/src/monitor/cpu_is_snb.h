/*! \file cpu_is_snb.h

  \brief Check CPUID vendor and signature.  
 */

#include "get_cpuid.h"

//! Test if signature is Sandy Bridge
static int cpu_is_sandybridge(char *cpu)
{
  char cpuid_path[80];
  int cpuid_fd = -1;
  uint32_t buf[4];
  int rc = 0;
  char signature[5];

  /* Open /dev/cpuid/cpu/cpuid. */
  snprintf(cpuid_path, sizeof(cpuid_path), "/dev/cpu/%s/cpuid", cpu);
  cpuid_fd = open(cpuid_path, O_RDONLY);
  if (cpuid_fd < 0) {
    ERROR("cannot open `%s': %m\n", cpuid_path);
    goto out;
  }
  
  /* Get cpu vendor. */
  if (pread(cpuid_fd, buf, sizeof(buf), 0x0) < 0) {
    ERROR("cannot read cpu vendor through `%s': %m\n", cpuid_path);
    goto out;
  }

  buf[0] = buf[2], buf[2] = buf[3], buf[3] = buf[0];
  TRACE("cpu %s, vendor `%.12s'\n", cpu, (char*) buf + 4);

  if (strncmp((char*) buf + 4, "GenuineIntel", 12) != 0)
    goto out; /* CentaurHauls? */

  get_cpuid_signature(cpuid_fd,signature,sizeof(signature));
  TRACE("cpu%s, CPUID Signature %s\n", cpu, signature);
  if (strncmp(signature, "06_3e", 5) !=0 && strncmp(signature, "06_2a", 5) !=0 && strncmp(signature, "06_2d", 5) !=0)
    goto out;

  rc = 1;

 out:
  if (cpuid_fd >= 0)
    close(cpuid_fd);

  return rc;
}

