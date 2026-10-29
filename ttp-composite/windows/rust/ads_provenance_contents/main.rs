// Target rule: Unusual File Download from Direct IP Address
// Sigma rule ID: ecb9ed8e-9e96-85bd-a68e-c86d68005053
// Ruleset path: sigma/sysmon/create_stream_hash/create_stream_hash_susp_ip_domains.yml
use windows_detection_composites as fixture;
fn main() {
    print!("COMPOSITE_CASE ads_provenance_contents\n");
    if !fixture::begin("ads_provenance_contents") {return;}
    let path=r"C:\lab\windows-coverage\work\provenance.exe:Zone.Identifier";
    let data=b"[ZoneTransfer]\r\nZoneId=3\r\nHostUrl=http://192.0.2.1/fixture.exe\r\n";
    std::fs::write(path,data).unwrap();assert_eq!(std::fs::read(path).unwrap(),data);
    fixture::success("ads_provenance_contents");
}
