# Windows C++ primitives built with Clang against LLVM libc++, on UCRT.
#
# Same compiler as the libstdc++ config (clang++); -stdlib=libc++ selects LLVM's
# standard library. On MSYS2 ucrt64 this imports libc++.dll in place of
# libstdc++-6.dll, while both keep the UCRT C runtime -- so the only varying
# factor is the C++ standard library. Requires the ucrt64 libc++ package.
set(CMAKE_CXX_COMPILER clang++)
set(CMAKE_CXX_FLAGS_INIT "-stdlib=libc++")
set(CMAKE_EXE_LINKER_FLAGS_INIT "-stdlib=libc++")
