#pragma once
#include "common.hpp"
// Exercise the selected C++ standard library, including its buffering and OS calls.
static inline void file_write(const char *path) {
    std::ofstream out(path, std::ios::binary | std::ios::trunc);
    CHECK(out.is_open());
    out.write(fixture_payload, sizeof(fixture_payload)-1);
    out.close(); CHECK(!out.fail());
    CHECK(fs::file_size(path) == sizeof(fixture_payload)-1);
}
static inline void file_read(const char *path) {
    std::ifstream in(path, std::ios::binary); CHECK(in.is_open());
    std::string data((std::istreambuf_iterator<char>(in)), {});
    CHECK(!in.bad() && data == fixture_payload);
    in.close(); CHECK(!in.fail());
}
static inline void truncate_file(const char *path) {
    CHECK(fs::exists(path));
    std::ofstream out(path, std::ios::binary | std::ios::trunc);
    CHECK(out.is_open()); out.close(); CHECK(!out.fail());
    CHECK(fs::file_size(path) == 0);
}
static inline void directory(const char *path) {
    fs::create_directory(path); CHECK(fs::is_directory(path));
}
