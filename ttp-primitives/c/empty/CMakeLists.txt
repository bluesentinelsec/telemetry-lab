add_executable(empty main.c)

add_test(NAME empty_exits_zero COMMAND empty)
set_tests_properties(empty_exits_zero PROPERTIES WILL_RETURN 0)
