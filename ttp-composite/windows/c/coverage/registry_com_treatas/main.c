#include "../common.h"
#include "../expansion_helpers.h"

int main(int argc,char **argv) {
    puts("COMPOSITE_CASE registry_com_treatas");
    if(!fixture_begin(argc,argv,"registry_com_treatas")) return 0;
    set_registry_verified("Software\\Classes\\CLSID\\{9B9C8026-806D-41E2-992A-909553D7A52A}\\TreatAs", "", "{9B9C8026-806D-41E2-992A-909553D7A52A}");
    success("registry_com_treatas"); return 0;
}
