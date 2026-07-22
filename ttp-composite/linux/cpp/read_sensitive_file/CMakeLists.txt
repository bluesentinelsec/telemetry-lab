add_executable(read_sensitive_file main.cpp)

# Composites install into a flat detonation bundle for substrate verification.
install(TARGETS read_sensitive_file RUNTIME DESTINATION .)
