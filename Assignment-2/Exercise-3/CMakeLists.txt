
add_executable(solution3 solution3.c)

target_link_libraries(solution3 PUBLIC RNG)

target_link_libraries(solution3 PRIVATE OpenMP::OpenMP_C)
target_include_directories(solution3 PUBLIC
                          "${PROJECT_BINARY_DIR}"
                          "${PROJECT_SOURCE_DIR}/Shared"
                          )