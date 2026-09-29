#include "../file_io.hpp"

int main(int argc,char **argv) {
    if (!fixture_begin(argc,argv,"release_agent_write")) return 0;
    file_write("/tmp/lab/release_agent");
    std::cout << "CASE_OK release_agent_write\n";
    return 0;
}
