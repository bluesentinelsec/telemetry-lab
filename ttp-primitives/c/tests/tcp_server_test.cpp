#include <catch2/catch_test_macros.hpp>

#include "primitive_runner.hpp"

TEST_CASE("tcp_server exits zero", "[tcp_server]") {
    REQUIRE(telemetry_lab::run_primitive(TCP_SERVER_BIN) == 0);
}
