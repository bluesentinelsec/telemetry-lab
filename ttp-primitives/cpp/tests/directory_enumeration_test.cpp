#include <catch2/catch_test_macros.hpp>

#include "primitive_runner.hpp"

TEST_CASE("directory_enumeration exits zero", "[directory_enumeration]") {
    REQUIRE(telemetry_lab::run_primitive(DIRECTORY_ENUMERATION_BIN) == 0);
}
