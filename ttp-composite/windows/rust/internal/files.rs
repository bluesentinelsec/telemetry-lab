use std::{
    fs::{self, File},
    io::{Read, Write},
    path::Path,
};
pub fn copy_verified(src: impl AsRef<Path>, dst: impl AsRef<Path>) {
    let mut input = File::open(&src).unwrap();
    let mut output = File::create(&dst).unwrap();
    let mut buffer = [0u8; 4096];
    loop {
        let n = input.read(&mut buffer).unwrap();
        if n == 0 {
            break;
        }
        output.write_all(&buffer[..n]).unwrap();
    }
    output.flush().unwrap();
    drop(output);
    drop(input);
    assert_eq!(
        fs::read(src).unwrap(),
        fs::read(dst).unwrap(),
        "file readback differs"
    );
}
