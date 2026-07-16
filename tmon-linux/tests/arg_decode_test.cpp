#include <catch2/catch_test_macros.hpp>

#include <string>

#include "core/arg_decode.hpp"

using tmon::DecodeArg;

TEST_CASE("openat flags decode to symbolic O_* names", "[arg_decode]") {
  // 0x241 = O_WRONLY | O_CREAT | O_TRUNC
  REQUIRE(DecodeArg(257, 2, 0x241) == "O_WRONLY|O_CREAT|O_TRUNC");
  // 0x80000 = O_CLOEXEC (low bits 0 -> O_RDONLY)
  REQUIRE(DecodeArg(257, 2, 0x80000) == "O_RDONLY|O_CLOEXEC");
  // openat mode argument renders octal
  REQUIRE(DecodeArg(257, 3, 0644) == "0644");
}

TEST_CASE("mmap prot and flags decode", "[arg_decode]") {
  REQUIRE(DecodeArg(9, 2, 0x3) == "PROT_READ|PROT_WRITE");
  REQUIRE(DecodeArg(9, 2, 0x0) == "PROT_NONE");
  REQUIRE(DecodeArg(9, 3, 0x22) == "MAP_PRIVATE|MAP_ANONYMOUS");
  REQUIRE(DecodeArg(10, 2, 0x1) == "PROT_READ");  // mprotect
}

TEST_CASE("access mode decodes", "[arg_decode]") {
  REQUIRE(DecodeArg(21, 1, 4) == "R_OK");
  REQUIRE(DecodeArg(21, 1, 0) == "F_OK");
}

TEST_CASE("unknown (syscall, arg) pairs yield empty (caller uses hex)",
          "[arg_decode]") {
  REQUIRE(DecodeArg(0, 0, 5).empty());     // read has no decoder
  REQUIRE(DecodeArg(257, 0, 5).empty());   // openat dfd is not decoded
}

TEST_CASE("leftover unknown bits are appended as hex", "[arg_decode]") {
  // O_WRONLY plus an unknown high bit
  REQUIRE(DecodeArg(257, 2, 0x1 | 0x40000000) == "O_WRONLY|0x40000000");
}
