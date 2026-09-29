#include "../common.hpp"
#include "../launch_fixture.h"

int main(int argc,char **argv) {
    if (!fixture_begin(argc,argv,"search_aws_credentials")) return 0;
    const char *args[] = {"/usr/bin/grep", "aws_access_key_id", "/tmp/lab/aws-search", NULL};
    launch_checked(args, "aws_access_key_id=telemetry-lab\n", NULL, NULL);
    std::cout << "CASE_OK search_aws_credentials\n";
    return 0;
}
