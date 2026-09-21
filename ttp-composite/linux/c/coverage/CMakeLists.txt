add_executable(falco_cases cases.c)
target_compile_definitions(falco_cases PRIVATE _GNU_SOURCE)
target_compile_options(falco_cases PRIVATE -Wall -Wextra -Werror)
install(TARGETS falco_cases RUNTIME DESTINATION .)
