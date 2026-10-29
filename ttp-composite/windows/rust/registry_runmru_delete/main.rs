// Target rule: RunMRU Registry Key Deletion - Registry
// Sigma rule ID: ec2a6d71-1139-d6f1-c39e-e9fc35500540
// Ruleset path: sigma/sysmon/registry/registry_delete/registry_delete_runmru.yml
use windows_detection_composites as fixture;
fn main() {
    print!("COMPOSITE_CASE registry_runmru_delete\n");
    if !fixture::begin("registry_runmru_delete") {
        return;
    }
    fixture::registry::delete_runmru();

    fixture::success("registry_runmru_delete");
}
