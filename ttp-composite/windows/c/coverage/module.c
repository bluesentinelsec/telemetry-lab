#include <windows.h>
__declspec(dllexport) int fixture_answer(void) { return 42; }
BOOL WINAPI DllMain(HINSTANCE instance,DWORD reason,LPVOID reserved) { (void)instance;(void)reason;(void)reserved;return TRUE; }
