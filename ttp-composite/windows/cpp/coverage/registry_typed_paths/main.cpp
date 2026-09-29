#include "../common.hpp"
#include "../expansion_helpers.hpp"

int main(int argc,char **argv) {
    std::cout << "COMPOSITE_CASE registry_typed_paths" << "\n";
    if(!fixture_begin(argc,argv,"registry_typed_paths")) return 0;
    set_registry_verified("Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\TypedPaths", "url99", "C:\\lab\\windows-coverage\\work");
    success("registry_typed_paths"); return 0;
}
