add_executable(thread_create main.c)
# POSIX uses pthreads; Threads::Threads adds -pthread. On glibc >= 2.34 and on
# musl the pthread implementation is part of libc, so this changes compile flags
# but adds no separate NEEDED library -- the libc under measurement stays the
# discriminator. Windows uses CreateThread from kernel32 (linked by default), so
# no thread library is needed there.
if(NOT WIN32)
  find_package(Threads REQUIRED)
  target_link_libraries(thread_create PRIVATE Threads::Threads)
endif()
install(TARGETS thread_create RUNTIME DESTINATION .)
