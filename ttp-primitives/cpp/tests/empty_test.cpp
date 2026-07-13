#include <catch2/catch_test_macros.hpp>

#include "primitive_runner.hpp"

TEST_CASE("empty exits zero", "[empty]") {
    REQUIRE(telemetry_lab::run_primitive(EMPTY_BIN) == 0);
}
