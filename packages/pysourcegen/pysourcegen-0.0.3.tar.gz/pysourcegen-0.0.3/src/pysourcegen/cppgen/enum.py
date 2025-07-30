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


class CppEnum(CppItem):

    class CppEnumItem(CppItem):

        def __init__(self, name: str, value: int):
            super().__init__([f"{name} = {value},"])
            self.__name = name

        def __str__(self) -> str:
            retval = self.GetIndentedTemplate().replace('\n', '')
            return retval

    def __init__(self, name: str):
        super().__init__(['enum class [N] {', '[I]', '};'])
        self.__name = name
        self.__items = []

    def AddEnum(self, name: str, value: int) -> None:
        self.__items.append(self.CppEnumItem(name, value))

    def Add(self, item: CppItem) -> None:
        self.__items.append(item)

    def __GetItemsString(self) -> str:
        retval = []
        for item in self.__items:
            retval.append(self.Indent(self.start_indent + 1, f"{item}"))
        return '\n'.join(retval)

    def __str__(self) -> str:
        retval = self.GetIndentedTemplate()
        retval = retval.replace('[N]', self.__name)
        retval = retval.replace('[I]', self.__GetItemsString())
        return retval + '\n'
