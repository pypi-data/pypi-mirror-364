cmake_minimum_required(VERSION 3.12)
project(MIPSolver_Examples)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Include directories
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/..)

# Create a library from the MIPSolver core
add_library(mipsolver_core STATIC
    ../src/core.cpp
)

# Example 1: Direct C++ API usage
add_executable(test_cpp_direct test_cpp_direct.cpp)
target_link_libraries(test_cpp_direct mipsolver_core)

# Example 2: Convenience C++ API usage  
add_executable(test_convenience_api test_convenience_api.cpp)
target_link_libraries(test_convenience_api mipsolver_core)

# Example 3: C API usage (if we compile the C API)
if(EXISTS ${CMAKE_CURRENT_SOURCE_DIR}/../api/mipsolver_c_api.cpp)
    add_library(mipsolver_c_api STATIC
        ../api/mipsolver_c_api.cpp
        ../src/core.cpp
    )
    
    add_executable(test_cpp_api test_cpp_api.cpp)
    target_link_libraries(test_cpp_api mipsolver_c_api)
endif()

# Compiler-specific options
if(MSVC)
    target_compile_options(mipsolver_core PRIVATE /W4)
else()
    target_compile_options(mipsolver_core PRIVATE -Wall -Wextra -Wpedantic)
endif()
