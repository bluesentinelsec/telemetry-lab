#include <catch2/catch_test_macros.hpp>

#include "primitive_runner.hpp"

TEST_CASE("memory_allocate exits zero", "[memory_allocate]") {
    REQUIRE(telemetry_lab::run_primitive(MEMORY_ALLOCATE_BIN) == 0);
}
