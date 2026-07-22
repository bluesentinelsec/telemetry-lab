/* startup_folder composite (T1547.001, Boot or Logon Autostart Execution:
 * Registry Run Keys / Startup Folder).
 *
 * Detection target: Sysmon EID 11 (file create); the shipped Sigma rule
 * ("Startup Folder File Write", generic on `TargetFilename contains
 * \...\StartUp`) keys on a file created under a user's Startup directory. The
 * behaviour is a CreateFile/WriteFile to
 * %APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\lab_test.lnk.
 * Expected robust across the Windows substrate matrix: Sysmon records the file
 * create (the event-level fact), never the file-API call path where substrate
 * differences would live.
 *
 * Benign: a few placeholder bytes are written and the file is deleted
 * immediately, leaving no persistence behind. The file-create telemetry is
 * emitted on creation regardless of the cleanup. Exits 0. */
#include <windows.h>
#include <shlobj.h>
#include <stdio.h>

int main(void) {
    char appdata[MAX_PATH];
    if (SHGetFolderPathA(NULL, CSIDL_APPDATA, NULL, SHGFP_TYPE_CURRENT,
                         appdata) != S_OK) {
        return 1;
    }

    char path[MAX_PATH];
    if (snprintf(path, sizeof path,
                 "%s\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\lab_test.lnk",
                 appdata) < 0) {
        return 1;
    }

    HANDLE h = CreateFileA(path, GENERIC_WRITE, 0, NULL, CREATE_ALWAYS,
                           FILE_ATTRIBUTE_NORMAL, NULL);
    if (h == INVALID_HANDLE_VALUE) {
        return 1;
    }

    const char bytes[] = "lab_test\r\n";
    DWORD written = 0;
    WriteFile(h, bytes, (DWORD)(sizeof bytes - 1), &written, NULL);
    CloseHandle(h);

    DeleteFileA(path);
    return 0;
}
