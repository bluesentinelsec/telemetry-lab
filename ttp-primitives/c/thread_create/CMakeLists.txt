# Threads::Threads adds -pthread. On glibc >= 2.34 and on musl the pthread
# implementation is part of libc, so this changes compile flags but adds no
# separate NEEDED library -- the libc under measurement stays the discriminator.
find_package(Threads REQUIRED)
add_executable(thread_create main.c)
target_link_libraries(thread_create PRIVATE Threads::Threads)
install(TARGETS thread_create RUNTIME DESTINATION .)
