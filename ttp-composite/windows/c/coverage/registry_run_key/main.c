#include "../common.h"

int main(int argc, char **argv) {
    if (!fixture_begin(argc,argv,"registry_run_key")) return 0;
    set_registry_verified("Software\\Microsoft\\Windows\\CurrentVersion\\Run","TelemetryLabCoverage","C:\\lab\\windows-coverage\\fixtures\\helper.exe");
    success("registry_run_key");
    return 0;
}
