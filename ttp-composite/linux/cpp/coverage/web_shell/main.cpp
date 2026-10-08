#include "../common.hpp"
#include "../utility.h"
int main(int argc, char **argv) {
 if (!fixture_begin(argc,argv,"web_shell")) return 0;
const char *args[] = {"/bin/sh", "-c", "printf 'SHELL_OK\\n'", NULL};
launch_verified(args, "SHELL_OK\n", 0, NULL, NULL);
std::cout << "CASE_OK web_shell\n";
return 0;
}
