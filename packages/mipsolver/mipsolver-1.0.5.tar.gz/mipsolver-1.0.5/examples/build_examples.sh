#!/bin/bash

# MIPSolver C++ Examples Build Script

echo "=== Building MIPSolver C++ Examples ==="

# Create build directory
mkdir -p build
cd build

# Configure with CMake
echo "Configuring with CMake..."
cmake ..

# Build the examples
echo "Building examples..."
make -j$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 4)

echo "Build complete!"
echo ""
echo "To run the examples:"
echo "  ./build/test_cpp_direct      # Direct C++ API example"
echo "  ./build/test_convenience_api # Convenience C++ API example"
echo "  ./build/test_cpp_api         # C API example"
