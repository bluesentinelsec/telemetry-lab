# Windows C++ primitives built with Clang against GNU libstdc++, on UCRT.
#
# Mirrors the Linux libstdc++ config: clang++ is held constant across both
# Windows C++ configs so only the C++ standard library varies. On MSYS2 ucrt64,
# clang++ defaults to libstdc++ and links the UCRT, so no stdlib flag is needed.
set(CMAKE_CXX_COMPILER clang++)
