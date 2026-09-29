#include "../common.hpp"
#include "../expansion_helpers.hpp"

int main(int argc,char **argv) {
    std::cout << "COMPOSITE_CASE registry_cor_profiler" << "\n";
    if(!fixture_begin(argc,argv,"registry_cor_profiler")) return 0;
    set_registry_verified("Environment", "COR_PROFILER", "{9B9C8026-806D-41E2-992A-909553D7A52A}");
    success("registry_cor_profiler"); return 0;
}
