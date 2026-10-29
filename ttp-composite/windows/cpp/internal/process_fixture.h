#pragma once
#include <tlhelp32.h>
/* A real, disposable ping process. No renamed helper or injected payload. */
static inline void process_fixture(int remote_thread) {
 STARTUPINFOA si;PROCESS_INFORMATION pi;memset(&si,0,sizeof si);memset(&pi,0,sizeof pi);si.cb=sizeof si;
 char cmd[]="C:\\Windows\\System32\\ping.exe -n 10 -w 1000 127.0.0.1";
 CHECK(CreateProcessA("C:\\Windows\\System32\\ping.exe",cmd,NULL,NULL,FALSE,CREATE_NO_WINDOW,NULL,NULL,&si,&pi));
 CHECK(CloseHandle(pi.hThread));Sleep(200);
 HANDLE target=OpenProcess(PROCESS_ALL_ACCESS,FALSE,pi.dwProcessId);CHECK(target!=NULL);
 CHECK(GetProcessId(target)==pi.dwProcessId);
 if(remote_thread) {
  FARPROC local=GetProcAddress(GetModuleHandleA("kernel32.dll"),"GetCurrentProcessId");CHECK(local!=NULL);
  HMODULE owner=NULL;CHECK(GetModuleHandleExA(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS|GET_MODULE_HANDLE_EX_FLAG_UNCHANGED_REFCOUNT,(LPCSTR)(uintptr_t)local,&owner));
  char filename[MAX_PATH];CHECK(GetModuleFileNameA(owner,filename,MAX_PATH)>0);const char *name=strrchr(filename,'\\');CHECK(name!=NULL);++name;
  HANDLE snap=CreateToolhelp32Snapshot(TH32CS_SNAPMODULE,pi.dwProcessId);CHECK(snap!=INVALID_HANDLE_VALUE);
  MODULEENTRY32 me;memset(&me,0,sizeof me);me.dwSize=sizeof me;uintptr_t base=0;
  if(Module32First(snap,&me)){do{if(!_stricmp(me.szModule,name)){base=(uintptr_t)me.modBaseAddr;break;}}while(Module32Next(snap,&me));}
  CHECK(CloseHandle(snap));CHECK(base!=0);
  uintptr_t address=base+((uintptr_t)local-(uintptr_t)owner);
  HANDLE thread=CreateRemoteThread(target,NULL,0,(LPTHREAD_START_ROUTINE)address,NULL,0,NULL);CHECK(thread!=NULL);
  CHECK(WaitForSingleObject(thread,5000)==WAIT_OBJECT_0);DWORD code=0;CHECK(GetExitCodeThread(thread,&code) && code==pi.dwProcessId);CHECK(CloseHandle(thread));
 }
 CHECK(TerminateProcess(pi.hProcess,0));CHECK(WaitForSingleObject(pi.hProcess,5000)==WAIT_OBJECT_0);
 CHECK(CloseHandle(target));CHECK(CloseHandle(pi.hProcess));
}
