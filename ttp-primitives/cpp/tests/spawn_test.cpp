#include <catch2/catch_test_macros.hpp>

#include "primitive_runner.hpp"

TEST_CASE("spawn exits zero", "[spawn]") {
    REQUIRE(telemetry_lab::run_primitive(SPAWN_BIN) == 0);
}
