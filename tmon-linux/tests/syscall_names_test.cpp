#include <catch2/catch_test_macros.hpp>

#include <string>

#include "core/syscall_names.hpp"

using tmon::SyscallName;

// These x86-64 syscall numbers are ABI-stable, so asserting them against the
// build-generated table also proves the table was generated and sorted.
TEST_CASE("known x86-64 syscall numbers resolve to names", "[syscall_names]") {
  REQUIRE(std::string(SyscallName(0)) == "read");
  REQUIRE(std::string(SyscallName(1)) == "write");
  REQUIRE(std::string(SyscallName(59)) == "execve");
  REQUIRE(std::string(SyscallName(257)) == "openat");
}

TEST_CASE("unknown syscall numbers return nullptr", "[syscall_names]") {
  REQUIRE(SyscallName(-1) == nullptr);
  REQUIRE(SyscallName(9999999) == nullptr);
}

TEST_CASE("syscall arity reflects real argument counts", "[syscall_names]") {
  REQUIRE(tmon::SyscallArity(0) == 3);    // read
  REQUIRE(tmon::SyscallArity(3) == 1);    // close
  REQUIRE(tmon::SyscallArity(9) == 6);    // mmap
  REQUIRE(tmon::SyscallArity(257) == 4);  // openat
  REQUIRE(tmon::SyscallArity(9999999) == -1);
}

TEST_CASE("pointer-returning syscalls are flagged", "[syscall_names]") {
  REQUIRE(tmon::SyscallReturnsPointer(9));   // mmap
  REQUIRE(tmon::SyscallReturnsPointer(12));  // brk
  REQUIRE_FALSE(tmon::SyscallReturnsPointer(0));   // read
  REQUIRE_FALSE(tmon::SyscallReturnsPointer(257)); // openat
}
