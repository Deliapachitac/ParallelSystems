
add_executable(solution1 solution1.c)

target_link_libraries(solution1 PUBLIC RNG)

target_link_libraries(solution1 PRIVATE OpenMP::OpenMP_C)
target_include_directories(solution1 PUBLIC
                          "${PROJECT_BINARY_DIR}"
                          )