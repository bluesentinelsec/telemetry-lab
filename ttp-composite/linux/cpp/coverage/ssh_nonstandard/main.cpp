#include "../common.hpp"
#include "../utility.h"
int main(int argc, char **argv) {
 if (!fixture_begin(argc,argv,"ssh_nonstandard")) return 0;
const char *args[] = {"/usr/bin/ssh", "-F", "/dev/null", "-i", "/tmp/lab/sshkey", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=yes", "-o", "UserKnownHostsFile=/tmp/lab/known_hosts", "-p", "4444", "labfixture@198.18.0.1", "/usr/bin/printf SSH_OK", NULL};
launch_verified(args, "SSH_OK", 0, NULL, NULL);
std::cout << "CASE_OK ssh_nonstandard\n";
return 0;
}
