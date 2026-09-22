use windows_detection_composites as fixture;
fn main() {
    print!("COMPOSITE_CASE registry_runmru_delete\n");
    if !fixture::begin("registry_runmru_delete") {
        return;
    }
    fixture::registry::delete_runmru();

    fixture::success("registry_runmru_delete");
}
