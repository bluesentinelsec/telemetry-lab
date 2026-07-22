# C++ primitives built with Clang against LLVM libc++.
#
# Same compiler as the libstdc++ config (clang++); the -stdlib=libc++ driver
# flag selects LLVM's standard library instead of GNU's, at both compile and
# link time. libc++ pulls libc++.so.1 and libc++abi.so.1 in place of
# libstdc++.so.6. Requires libc++-dev / libc++abi-dev on the build host.
set(CMAKE_CXX_COMPILER clang++)
set(CMAKE_CXX_FLAGS_INIT "-stdlib=libc++")
set(CMAKE_EXE_LINKER_FLAGS_INIT "-stdlib=libc++")
