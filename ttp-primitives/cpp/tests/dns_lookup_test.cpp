#include <catch2/catch_test_macros.hpp>

#include "primitive_runner.hpp"

TEST_CASE("dns_lookup exits zero", "[dns_lookup]") {
    REQUIRE(telemetry_lab::run_primitive(DNS_LOOKUP_BIN) == 0);
}
