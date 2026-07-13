add_executable(empty main.cpp)

# Primitives are installed into a flat bundle; the Catch2 test harness is not.
# The bundle is what gets substrate-verified and shipped to the lab, so it must
# contain the artifacts under measurement and nothing else.
install(TARGETS empty RUNTIME DESTINATION .)
