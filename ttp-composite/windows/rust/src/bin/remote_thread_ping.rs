use windows_detection_composites as fixture;
fn main(){println!("COMPOSITE_CASE remote_thread_ping");if !fixture::begin("remote_thread_ping") {return;}
fixture::process_fixture::run(true);
fixture::success("remote_thread_ping");}
