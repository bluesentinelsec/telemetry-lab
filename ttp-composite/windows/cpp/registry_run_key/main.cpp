// registry_run_key composite (T1547.001, Boot or Logon Autostart Execution:
// Registry Run Keys / Startup Folder).
//
// Detection target: Sysmon EID 13 (registry value set); the shipped Sigma rule
// ("CurrentVersion Autorun Keys Modification") keys on a value written under a
// Run key. The behaviour is a RegSetValueEx into
// HKCU\Software\Microsoft\Windows\CurrentVersion\Run. Expected robust across
// the Windows substrate matrix: Sysmon records the registry set (the
// event-level fact), never the advapi32 call path where substrate differences
// would live.
//
// Benign: the value is written and then deleted, leaving no persistence behind;
// the referenced path is a placeholder that is never executed. The set-value
// telemetry is emitted on the write regardless of the immediate cleanup.
// Exits 0.
#include <windows.h>

int main() {
    HKEY key;
    if (RegOpenKeyExA(HKEY_CURRENT_USER,
                      "Software\\Microsoft\\Windows\\CurrentVersion\\Run",
                      0, KEY_SET_VALUE, &key) != ERROR_SUCCESS) {
        return 1;
    }

    const char name[] = "lab_test";
    const char data[] = "C:\\lab\\x.exe";
    LONG set = RegSetValueExA(key, name, 0, REG_SZ,
                              (const BYTE *)data, (DWORD)sizeof data);
    if (set == ERROR_SUCCESS) {
        RegDeleteValueA(key, name);
    }

    RegCloseKey(key);
    return set == ERROR_SUCCESS ? 0 : 1;
}
