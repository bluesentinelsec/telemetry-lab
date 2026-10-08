# std::thread is implemented over the platform thread library (pthreads on POSIX,
# winpthread on Windows via the MSYS2 toolchain). Threads::Threads lets CMake
# select the correct one per platform. On glibc >= 2.34 and on musl the pthread
# implementation is part of libc, so on Linux this adds no separate NEEDED
# library and the libc under measurement stays the discriminator.
find_package(Threads REQUIRED)
add_executable(thread_create main.cpp)
target_link_libraries(thread_create PRIVATE Threads::Threads)
install(TARGETS thread_create RUNTIME DESTINATION .)
