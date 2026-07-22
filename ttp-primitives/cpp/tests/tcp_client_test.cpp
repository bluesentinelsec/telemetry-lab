#include <catch2/catch_test_macros.hpp>

#include "primitive_runner.hpp"

TEST_CASE("tcp_client exits zero", "[tcp_client]") {
    REQUIRE(telemetry_lab::run_primitive(TCP_CLIENT_BIN) == 0);
}
