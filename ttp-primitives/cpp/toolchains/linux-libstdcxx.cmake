# C++ primitives built with Clang against GNU libstdc++.
#
# The compiler is held constant (clang++) across both C++ Linux configs so that
# the only varying factor is the C++ standard library, mirroring how the C
# configs hold the compiler constant and vary only the C runtime (glibc/musl).
# clang++ uses libstdc++ by default on Linux, so no stdlib flag is needed here.
set(CMAKE_CXX_COMPILER clang++)
