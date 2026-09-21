#include <stdio.h>
/* One identical, static helper for both caller runtimes. */
int main(void) { return puts("HELPER_OK") < 0; }
