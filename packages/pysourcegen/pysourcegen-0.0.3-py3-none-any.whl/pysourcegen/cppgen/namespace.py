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


class CppNamespace(CppItem):

    def __init__(self, name: str):
        super().__init__(['namespace [N] {', '[I]', '}  // namespace [N]'])
        self.__name = name
        self.__items = []

    def Add(self, item: CppItem) -> None:
        if item.__class__.__name__ != self.__class__.__name__:
            item.SetIndent(self.start_indent + 1)
        self.__items.append(item)

    def __ParseItems(self) -> str:
        items = []
        for item in self.__items:
            items.append(str(item))
        return '\n'.join(items)

    def __str__(self) -> str:
        retval = self.GetIndentedTemplate()
        retval = retval.replace('[N]', self.__name)
        retval = retval.replace('[I]', self.__ParseItems())
        return retval
