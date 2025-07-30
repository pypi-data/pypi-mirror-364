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


class CppItem():

    def __init__(self, template):
        self.template = template
        self.start_indent = 0

    def Indent(self, level: int, string: str) -> str:
        indent_str = ' ' * level * 4
        indent_str += string
        return indent_str

    def SetIndent(self, level: int) -> None:
        self.start_indent = level

    def GetIndentedTemplate(self) -> str:
        retval = []
        for item in self.template:
            if item[0] == '[':
                retval.append(item)
            else:
                retval.append(self.Indent(self.start_indent, item))
        return '\n'.join(retval)
