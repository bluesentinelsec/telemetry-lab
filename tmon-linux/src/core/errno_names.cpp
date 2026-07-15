#include "core/errno_names.hpp"

#include <cstddef>

namespace tmon {
namespace {

// Generated into the binary dir: kErrnoTable[] sorted by ascending num, and
// kErrnoTableCount.
#include "errno_table.generated.h"

}  // namespace

const char* ErrnoName(int num) {
  std::size_t lo = 0, hi = kErrnoTableCount;
  while (lo < hi) {
    std::size_t mid = lo + (hi - lo) / 2;
    int m = kErrnoTable[mid].num;
    if (m == num) return kErrnoTable[mid].name;
    if (m < num)
      lo = mid + 1;
    else
      hi = mid;
  }
  return nullptr;
}

}  // namespace tmon
