#include <catch2/catch_test_macros.hpp>

#include "primitive_runner.hpp"

TEST_CASE("process_enumeration exits zero", "[process_enumeration]") {
    REQUIRE(telemetry_lab::run_primitive(PROCESS_ENUMERATION_BIN) == 0);
}
