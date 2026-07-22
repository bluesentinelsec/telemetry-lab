add_executable(ptrace_antidebug main.cpp)

# Composites install into a flat detonation bundle for substrate verification.
install(TARGETS ptrace_antidebug RUNTIME DESTINATION .)
