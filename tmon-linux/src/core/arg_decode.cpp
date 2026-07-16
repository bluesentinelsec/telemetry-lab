#include "core/arg_decode.hpp"

#include <cstdio>

namespace tmon {
namespace {

struct Flag {
  std::uint64_t bit;
  const char* name;
};

std::string Hex(std::uint64_t v) {
  char buf[20];
  std::snprintf(buf, sizeof(buf), "0x%llx", static_cast<unsigned long long>(v));
  return buf;
}

// OR-together named bits; append any leftover bits as hex. `zero_name` is used
// when no bits are set.
std::string JoinFlags(std::uint64_t v, const Flag* flags, std::size_t n,
                      const char* zero_name) {
  std::string out;
  std::uint64_t rem = v;
  for (std::size_t i = 0; i < n; i++) {
    if (rem & flags[i].bit) {
      if (!out.empty()) out += '|';
      out += flags[i].name;
      rem &= ~flags[i].bit;
    }
  }
  if (rem) {
    if (!out.empty()) out += '|';
    out += Hex(rem);
  }
  if (out.empty()) out = zero_name;
  return out;
}

std::string Octal(std::uint64_t v) {
  char buf[24];
  std::snprintf(buf, sizeof(buf), "0%llo", static_cast<unsigned long long>(v));
  return buf;
}

// open/openat flags: low two bits are the access mode, the rest are bit flags.
std::string OpenFlags(std::uint64_t v) {
  std::string out;
  switch (v & 3) {
    case 0: out = "O_RDONLY"; break;
    case 1: out = "O_WRONLY"; break;
    case 2: out = "O_RDWR"; break;
    default: out = "O_ACCMODE"; break;
  }
  static const Flag kOpen[] = {
      {0100, "O_CREAT"},      {0200, "O_EXCL"},      {0400, "O_NOCTTY"},
      {01000, "O_TRUNC"},     {02000, "O_APPEND"},   {04000, "O_NONBLOCK"},
      {040000, "O_DIRECT"},   {0100000, "O_LARGEFILE"}, {0200000, "O_DIRECTORY"},
      {0400000, "O_NOFOLLOW"},{01000000, "O_NOATIME"},  {02000000, "O_CLOEXEC"},
      {010000000, "O_PATH"},  {020200000, "O_TMPFILE"},
  };
  std::uint64_t rem = v & ~static_cast<std::uint64_t>(3);
  for (const auto& f : kOpen) {
    if ((rem & f.bit) == f.bit) {
      out += '|';
      out += f.name;
      rem &= ~f.bit;
    }
  }
  if (rem) out += '|' + Hex(rem);
  return out;
}

std::string Prot(std::uint64_t v) {
  static const Flag kProt[] = {
      {0x1, "PROT_READ"}, {0x2, "PROT_WRITE"}, {0x4, "PROT_EXEC"},
  };
  return JoinFlags(v, kProt, sizeof(kProt) / sizeof(kProt[0]), "PROT_NONE");
}

std::string MapFlags(std::uint64_t v) {
  static const Flag kMap[] = {
      {0x1, "MAP_SHARED"},     {0x2, "MAP_PRIVATE"},   {0x10, "MAP_FIXED"},
      {0x20, "MAP_ANONYMOUS"}, {0x100, "MAP_GROWSDOWN"},{0x800, "MAP_DENYWRITE"},
      {0x4000, "MAP_NORESERVE"},{0x8000, "MAP_POPULATE"},{0x20000, "MAP_STACK"},
  };
  return JoinFlags(v, kMap, sizeof(kMap) / sizeof(kMap[0]), "0");
}

std::string AccessMode(std::uint64_t v) {
  static const Flag kAcc[] = {
      {0x4, "R_OK"}, {0x2, "W_OK"}, {0x1, "X_OK"},
  };
  return JoinFlags(v, kAcc, sizeof(kAcc) / sizeof(kAcc[0]), "F_OK");
}

}  // namespace

std::string DecodeArg(std::int64_t nr, int arg_index, std::uint64_t value) {
  switch (nr) {
    case 2:  // open(path, flags, mode)
      if (arg_index == 1) return OpenFlags(value);
      if (arg_index == 2) return Octal(value);
      break;
    case 257:  // openat(dfd, path, flags, mode)
      if (arg_index == 2) return OpenFlags(value);
      if (arg_index == 3) return Octal(value);
      break;
    case 9:  // mmap(addr, len, prot, flags, fd, off)
      if (arg_index == 2) return Prot(value);
      if (arg_index == 3) return MapFlags(value);
      break;
    case 10:  // mprotect(addr, len, prot)
      if (arg_index == 2) return Prot(value);
      break;
    case 21:  // access(path, mode)
      if (arg_index == 1) return AccessMode(value);
      break;
    case 269:  // faccessat(dfd, path, mode, flags)
    case 439:  // faccessat2(dfd, path, mode, flags)
      if (arg_index == 2) return AccessMode(value);
      break;
    case 90:  // chmod(path, mode)
    case 133:  // mknod(path, mode, dev)
      if (arg_index == 1) return Octal(value);
      break;
    case 268:  // fchmodat(dfd, path, mode, flags)
      if (arg_index == 2) return Octal(value);
      break;
    default:
      break;
  }
  return "";
}

}  // namespace tmon
