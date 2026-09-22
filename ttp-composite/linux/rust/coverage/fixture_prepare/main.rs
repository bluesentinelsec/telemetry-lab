fn main() {
    if !coverage_suite::begin("fixture_prepare") {
        return;
    }
    coverage_suite::prepare();
}
