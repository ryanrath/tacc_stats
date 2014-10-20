#ifndef GET_CPUID_H_
#define GET_CPUID_H_

static void get_cpuid_signature(int cpuid_file, char* signature, size_t sigbuflen)
{
  uint32_t buf[4];

  pread(cpuid_file, buf, sizeof(buf), 1);

  int model = (buf[0] & 0x0FF) >> 4;
  int extended_model = (buf[0] & 0xF0000) >> 12;
  int family_code = (buf[0] & 0xF00) >> 8;
  int extended_family_code = (buf[0] & 0xFF00000) >> 16;

  snprintf(signature,sigbuflen,"%02x_%x", extended_family_code | family_code, extended_model | model);

}

#endif
