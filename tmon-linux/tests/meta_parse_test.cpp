#include <catch2/catch_test_macros.hpp>

#include "core/meta_parse.hpp"

using tmon::ParseMetaArg;

TEST_CASE("a valid KEY=VALUE token parses", "[meta]") {
  auto r = ParseMetaArg("lang=c");
  REQUIRE(r.has_value());
  REQUIRE(r->first == "lang");
  REQUIRE(r->second == "c");
}

TEST_CASE("value may be empty or itself contain '='", "[meta]") {
  REQUIRE(ParseMetaArg("k=")->second == "");
  REQUIRE(ParseMetaArg("k=a=b")->first == "k");
  REQUIRE(ParseMetaArg("k=a=b")->second == "a=b");
}

TEST_CASE("a token with no '=' or an empty key is rejected", "[meta]") {
  REQUIRE_FALSE(ParseMetaArg("novalue").has_value());
  REQUIRE_FALSE(ParseMetaArg("=orphan").has_value());
  REQUIRE_FALSE(ParseMetaArg("").has_value());
}
