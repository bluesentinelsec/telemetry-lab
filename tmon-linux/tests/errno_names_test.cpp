#include <catch2/catch_test_macros.hpp>

#include <string>

#include "core/errno_names.hpp"

using tmon::ErrnoName;

// Low errno numbers are ABI-stable, so asserting them also proves the table was
// generated and sorted.
TEST_CASE("known errno numbers resolve to symbols", "[errno_names]") {
  REQUIRE(std::string(ErrnoName(1)) == "EPERM");
  REQUIRE(std::string(ErrnoName(2)) == "ENOENT");
  REQUIRE(std::string(ErrnoName(13)) == "EACCES");
}

TEST_CASE("unknown errno numbers return nullptr", "[errno_names]") {
  REQUIRE(ErrnoName(0) == nullptr);
  REQUIRE(ErrnoName(100000) == nullptr);
}
