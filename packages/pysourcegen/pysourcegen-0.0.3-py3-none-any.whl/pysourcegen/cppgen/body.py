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

from pysourcegen.cppgen.item import CppItem


class CppBody(CppItem):

    def __init__(self, body, semicolon=False):
        super().__init__(['{', '[B]', '};' if semicolon == True else '}'])
        self.__body = body

    def Add(self, item: CppItem) -> None:
        self.__body.append(item)

    def __GetBodyString(self) -> str:
        retval = []
        for item in self.__body:
            item.SetIndent(self.start_indent + 1)
            retval.append(str(item))
        return '\n'.join(retval)

    def __str__(self) -> str:
        retval = self.GetIndentedTemplate()
        retval = retval.replace('[B]', self.__GetBodyString())
        return retval
