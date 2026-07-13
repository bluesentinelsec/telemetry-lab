add_executable(empty main.cpp)

# A primitive passes when the built binary runs to completion and exits 0.
# CTest treats a nonzero exit code as failure by default, so no extra property
# is needed here.
add_test(NAME empty_exits_zero COMMAND empty)
