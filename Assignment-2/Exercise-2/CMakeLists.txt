add_executable(Solution2 solution.c)

target_link_libraries(Solution2 PUBLIC RNG)

if(USE_OPENMP)
    target_link_libraries(Solution2 PRIVATE OpenMP::OpenMP_C)
endif()

target_include_directories(Solution2 PUBLIC
                          "${PROJECT_BINARY_DIR}"
                          "${PROJECT_SOURCE_DIR}/Shared"
                          )