#! /bin/python3

# Copyright 2024 Compen Embedded B.V.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from pysourcegen import *

# CPPfile
cppFile = CppFile()

# Head
cppFile.AddHead(CppComment('Hello World Demo'))
cppFile.AddHead(CppComment(''))
cppFile.AddHead(CppComment('This is a generated CPP file'))

# Include iostream
cppFile.AddInclude("iostream")

main_body = CppBody([])
# Create 1000 hello worlds
for i in range(1000):
    main_body.Add(CppComment(f'This is hello world number {i}'))
    main_body.Add(CppText(f'std::cout << "Hello World " << {i} << std::endl;'))

# Return 0
main_body.Add(CppText('return 0;'))

# Main function
main = CppFunction(
    "main",  # Function Name
    "int",  # Return Value
    # Body of main function
    main_body)

# Main function parameters
main.AddParameter("int", "argv")
main.AddParameter("char**", "argc")

# Add main function to cppFile
cppFile.Add(main)

# Show output on terminal
print(cppFile)
