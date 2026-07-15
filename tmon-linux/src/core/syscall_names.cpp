#include "core/syscall_names.hpp"

#include <cstddef>

namespace tmon {
namespace {

// Generated at build time into the binary dir: defines
//   struct { long nr; const char* name; } kSyscallTable[];
//   const std::size_t kSyscallTableCount;
// sorted by ascending nr.
#include "syscall_table.generated.h"

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

}  // namespace tmon
