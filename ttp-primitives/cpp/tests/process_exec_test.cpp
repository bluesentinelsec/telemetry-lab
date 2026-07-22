#include <catch2/catch_test_macros.hpp>

#include "primitive_runner.hpp"

TEST_CASE("process_exec exits zero", "[process_exec]") {
    REQUIRE(telemetry_lab::run_primitive(PROCESS_EXEC_BIN) == 0);
}
