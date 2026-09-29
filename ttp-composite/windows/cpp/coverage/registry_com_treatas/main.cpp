#include "../common.hpp"
#include "../expansion_helpers.hpp"

int main(int argc,char **argv) {
    std::cout << "COMPOSITE_CASE registry_com_treatas\n";
    if(!fixture_begin(argc,argv,"registry_com_treatas")) return 0;
    set_registry_verified("Software\\Classes\\CLSID\\{9B9C8026-806D-41E2-992A-909553D7A52A}\\TreatAs", "", "{9B9C8026-806D-41E2-992A-909553D7A52A}");
    success("registry_com_treatas"); return 0;
}
