#include <catch2/catch_test_macros.hpp>

#include "primitive_runner.hpp"

TEST_CASE("pipe_ipc exits zero", "[pipe_ipc]") {
    REQUIRE(telemetry_lab::run_primitive(PIPE_IPC_BIN) == 0);
}
