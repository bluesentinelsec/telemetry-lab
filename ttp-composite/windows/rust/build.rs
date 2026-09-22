fn main() {
    let target = std::env::var("TARGET").unwrap();
    assert_eq!(
        target, "x86_64-pc-windows-msvc",
        "This suite requires the declared Windows target"
    );
    let features = std::env::var("CARGO_CFG_TARGET_FEATURE").unwrap();
    let crt = if features.split(',').any(|f| f == "crt-static") {
        "static"
    } else {
        "dynamic"
    };
    println!("cargo:rustc-env=COMPOSITE_BUILD_TARGET={target}");
    println!("cargo:rustc-env=COMPOSITE_BUILD_CRT={crt}");
}
