#ifndef GET_CPUID_H_
#define GET_CPUID_H_

#include <cpuid.h>

static void get_cpuid_signature(int cpuid_file, char* signature, size_t sigbuflen)
{
  unsigned int ebx = 0, ecx = 0, edx = 0, eax = 1;
  __get_cpuid(1, &eax, &ebx, &ecx, &edx);

  int model = (eax & 0x0FF) >> 4;
  int extended_model = (eax & 0xF0000) >> 12;
  int family_code = (eax & 0xF00) >> 8;
  int extended_family_code = (eax & 0xFF00000) >> 16;

  snprintf(signature,sigbuflen,"%02x_%x", extended_family_code | family_code, extended_model | model);

}

#endif
