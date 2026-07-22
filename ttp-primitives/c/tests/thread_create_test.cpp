#include <catch2/catch_test_macros.hpp>

#include "primitive_runner.hpp"

TEST_CASE("thread_create exits zero", "[thread_create]") {
    REQUIRE(telemetry_lab::run_primitive(THREAD_CREATE_BIN) == 0);
}
