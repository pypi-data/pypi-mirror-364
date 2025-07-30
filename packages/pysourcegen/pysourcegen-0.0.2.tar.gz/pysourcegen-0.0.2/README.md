# pysourcegen
Python Source Code Generator

A different approach for generating repetitive C/C++ source code using Python.

## Examples

### C++ - Hello World

  run [src/hello_world_cpp_example.py](src/hello_world_cpp_example.py) to create an exectuble called `cpphello`:

    ./hello_world_cpp_example.py | g++ -x c++ -o cpphello -

### C - Hello World

  run [src/hello_world_c_example.py](src/hello_world_c_example.py) to create an exectuble called `chello`:

    ./hello_world_c_example.py | gcc -x c -o chello -
