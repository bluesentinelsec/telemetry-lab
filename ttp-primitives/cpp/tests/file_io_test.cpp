#include <catch2/catch_test_macros.hpp>

#include "primitive_runner.hpp"

TEST_CASE("file_io exits zero", "[file_io]") {
    REQUIRE(telemetry_lab::run_primitive(FILE_IO_BIN) == 0);
}
