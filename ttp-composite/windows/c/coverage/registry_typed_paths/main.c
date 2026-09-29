#include "../common.h"
#include "../expansion_helpers.h"

int main(int argc,char **argv) {
    puts("COMPOSITE_CASE registry_typed_paths");
    if(!fixture_begin(argc,argv,"registry_typed_paths")) return 0;
    set_registry_verified("Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\TypedPaths", "url99", "C:\\lab\\windows-coverage\\work");
    success("registry_typed_paths"); return 0;
}
