cmake_minimum_required(VERSION 3.10)

project(Parallel-systems-2 LANGUAGES C)

option(USE_OPENMP "Enable OpenMP Parallelization" ON)

if(USE_OPENMP)
    find_package(OpenMP REQUIRED)
endif()

add_subdirectory(Exercise-1)
add_subdirectory(Exercise-2)


add_subdirectory(Shared)

