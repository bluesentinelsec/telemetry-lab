add_executable(imds main.cpp)

# Composites install into a flat detonation bundle for substrate verification.
install(TARGETS imds RUNTIME DESTINATION .)
