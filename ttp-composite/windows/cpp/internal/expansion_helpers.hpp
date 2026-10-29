#pragma once
static inline void set_registry_dword_verified(const char *path,const char *name,DWORD value) {
 HKEY key; CHECK(RegOpenKeyExA(HKEY_CURRENT_USER,path,0,KEY_SET_VALUE|KEY_QUERY_VALUE,&key)==ERROR_SUCCESS);
 CHECK(RegSetValueExA(key,name,0,REG_DWORD,(BYTE*)&value,sizeof value)==ERROR_SUCCESS);
 DWORD actual=0,type=0,size=sizeof actual;CHECK(RegQueryValueExA(key,name,NULL,&type,(BYTE*)&actual,&size)==ERROR_SUCCESS);
 CHECK(type==REG_DWORD && size==sizeof actual && actual==value);CHECK(RegCloseKey(key)==ERROR_SUCCESS);
}
#include <filesystem>
static inline void copy_verified_w(const wchar_t *src,const wchar_t *dst) {
 std::ifstream in(std::filesystem::path(src),std::ios::binary);std::ofstream out(std::filesystem::path(dst),std::ios::binary|std::ios::trunc);CHECK(in && out);
 out<<in.rdbuf();CHECK(!in.bad() && out.good());out.close();CHECK(!out.fail());in.close();
 std::ifstream a(std::filesystem::path(src),std::ios::binary),b(std::filesystem::path(dst),std::ios::binary);CHECK(a && b);
 std::string aa((std::istreambuf_iterator<char>(a)),{}),bb((std::istreambuf_iterator<char>(b)),{});CHECK(!a.bad() && !b.bad() && aa==bb);
}
