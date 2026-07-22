add_executable(mkdir_bin main.cpp)

# Composites install into a flat detonation bundle for substrate verification.
install(TARGETS mkdir_bin RUNTIME DESTINATION .)
