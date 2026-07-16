/* file_io primitive: write a temporary file and read it back.
 *
 * Self-contained and deterministic: it creates its own temp file, so it needs
 * no arguments and no ambient state. tmpfile() is C-standard and portable across
 * Linux and Windows. The file work exercises the file-I/O telemetry family
 * (open/write/read/close) and links the C runtime naturally, so no substrate
 * anchor is required. Always exits 0 on success. */
#include <stdio.h>

int main(void) {
    FILE *f = tmpfile();
    if (!f) {
        return 1;
    }
    const char *msg = "telemetry-lab\n";
    if (fwrite(msg, 1, 14, f) != 14) {
        fclose(f);
        return 1;
    }
    rewind(f);
    char buf[32];
    fread(buf, 1, sizeof buf, f);
    fclose(f);
    return 0;
}
