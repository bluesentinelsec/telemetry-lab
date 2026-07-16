#include "core/syscall_names.hpp"

#include <cstddef>

namespace tmon {
namespace {

// Generated at build time into the binary dir: defines
//   struct { long nr; const char* name; } kSyscallTable[];
//   const std::size_t kSyscallTableCount;
// sorted by ascending nr.
#include "syscall_table.generated.h"

// Committed table of per-syscall argument counts (arity), from tracefs metadata:
//   struct SyscallMeta { long nr; int arity; } kSyscallMeta[]; sorted by nr.
#include "core/syscall_meta.h"

}  // namespace

const char* SyscallName(std::int64_t nr) {
  // Binary search over the generated, nr-sorted table.
  std::size_t lo = 0, hi = kSyscallTableCount;
  while (lo < hi) {
    std::size_t mid = lo + (hi - lo) / 2;
    long midnr = kSyscallTable[mid].nr;
    if (midnr == nr) return kSyscallTable[mid].name;
    if (midnr < nr)
      lo = mid + 1;
    else
      hi = mid;
  }
  return nullptr;
}

int SyscallArity(std::int64_t nr) {
  std::size_t lo = 0, hi = kSyscallMetaCount;
  while (lo < hi) {
    std::size_t mid = lo + (hi - lo) / 2;
    long midnr = kSyscallMeta[mid].nr;
    if (midnr == nr) return kSyscallMeta[mid].arity;
    if (midnr < nr)
      lo = mid + 1;
    else
      hi = mid;
  }
  return -1;  // unknown -> caller shows all captured args
}

bool SyscallReturnsPointer(std::int64_t nr) {
  switch (nr) {
    case 9:   // mmap
    case 12:  // brk
    case 25:  // mremap
    case 30:  // shmat
      return true;
    default:
      return false;
  }
}

}  // namespace tmon
