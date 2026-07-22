#include <catch2/catch_test_macros.hpp>

#include "primitive_runner.hpp"

TEST_CASE("http_client exits zero", "[http_client]") {
    REQUIRE(telemetry_lab::run_primitive(HTTP_CLIENT_BIN) == 0);
}
