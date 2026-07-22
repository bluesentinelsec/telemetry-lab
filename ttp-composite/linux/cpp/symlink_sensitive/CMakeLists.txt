add_executable(symlink_sensitive main.cpp)

# Composites install into a flat detonation bundle for substrate verification.
install(TARGETS symlink_sensitive RUNTIME DESTINATION .)
