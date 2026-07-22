add_executable(clear_log main.cpp)

# Composites install into a flat detonation bundle for substrate verification.
install(TARGETS clear_log RUNTIME DESTINATION .)
