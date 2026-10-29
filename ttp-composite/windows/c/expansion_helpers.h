#pragma once
static inline void set_registry_dword_verified(const char *path,const char *name,DWORD value) {
 HKEY key; CHECK(RegOpenKeyExA(HKEY_CURRENT_USER,path,0,KEY_SET_VALUE|KEY_QUERY_VALUE,&key)==ERROR_SUCCESS);
 CHECK(RegSetValueExA(key,name,0,REG_DWORD,(BYTE*)&value,sizeof value)==ERROR_SUCCESS);
 DWORD actual=0,type=0,size=sizeof actual;CHECK(RegQueryValueExA(key,name,NULL,&type,(BYTE*)&actual,&size)==ERROR_SUCCESS);
 CHECK(type==REG_DWORD && size==sizeof actual && actual==value);CHECK(RegCloseKey(key)==ERROR_SUCCESS);
}
static inline void copy_verified_w(const wchar_t *src,const wchar_t *dst) {
 FILE *in=_wfopen(src,L"rb"),*out=_wfopen(dst,L"wb");CHECK(in && out);char buf[4096];size_t n;
 while((n=fread(buf,1,sizeof buf,in))!=0) CHECK(fwrite(buf,1,n,out)==n);
 CHECK(!ferror(in));CHECK(fclose(in)==0 && fclose(out)==0);
 in=_wfopen(src,L"rb");out=_wfopen(dst,L"rb");CHECK(in && out);char other[4096];size_t m;
 do{n=fread(buf,1,sizeof buf,in);m=fread(other,1,sizeof other,out);CHECK(n==m && !memcmp(buf,other,n));}while(n);
 CHECK(!ferror(in) && !ferror(out));CHECK(fclose(in)==0 && fclose(out)==0);
}
