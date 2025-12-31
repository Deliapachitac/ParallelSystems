## Build Instructions

To compile the project, run the following commands in your terminal:

```bash
# 1. Create and enter the build directory
mkdir build && cd build

# 2. Configure the project
# Add -DUSE_OPENMP=ON/OFF to toggle parallelization
cmake ..

# 3. Build all binaries
cmake --build .