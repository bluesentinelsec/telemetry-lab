#include "../common.hpp"

int main(int argc, char **argv) {
    if (!fixture_begin(argc,argv,"proc_environ")) return 0;
    std::ifstream in("/proc/self/environ", std::ios::binary); CHECK(in.is_open());
    std::string data((std::istreambuf_iterator<char>(in)), {});
    CHECK(!in.bad() && data.find("TELEMETRY_LAB_FIXTURE=1") != std::string::npos);
    in.close(); CHECK(!in.fail());
    std::cout << "CASE_OK proc_environ\n";
    return 0;
}
