add_executable(reverse_shell main.cpp)

# Composites install into a flat detonation bundle for substrate verification.
install(TARGETS reverse_shell RUNTIME DESTINATION .)
