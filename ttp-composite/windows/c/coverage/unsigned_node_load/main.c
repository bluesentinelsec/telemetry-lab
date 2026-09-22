#include "../common.h"

int main(int argc, char **argv) {
    if (!fixture_begin(argc,argv,"unsigned_node_load")) return 0;
    HMODULE module=LoadLibraryA(ROOT "\\fixtures\\fixture.node"); CHECK(module!=NULL);
    typedef int (*answer_fn)(void);
    /* Copy the function pointer representation without incompatible-function casts. */
    FARPROC proc=GetProcAddress(module,"fixture_answer"); CHECK(proc!=NULL);
    answer_fn answer; CHECK(sizeof answer==sizeof proc); memcpy(&answer,&proc,sizeof answer);
    CHECK(answer()==42); CHECK(FreeLibrary(module));
    success("unsigned_node_load");
    return 0;
}
