add_executable(empty main.c)

# Primitives are installed into a flat bundle; the Catch2 test harness is not.
# The bundle is what gets substrate-verified and shipped to the lab, so it must
# contain the artifacts under measurement and nothing else -- notably not the
# harness, which links the default glibc toolchain even in the musl config.
install(TARGETS empty RUNTIME DESTINATION .)
