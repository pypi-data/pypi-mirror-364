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
from pysourcegen.cppgen.body import CppBody


class CppClassConstructor(CppItem):

    def __init__(self, name: str, body: CppBody):
        super().__init__(['NAME([P])', '[B]'])
        self.__name = name
        self.__parameters = []
        self.__initlist = []
        self.__body = body

    def AddParameter(self, typename: str, name: str) -> None:
        self.__parameters.append(f"{typename} {name}")

    def __ParseParameters(self) -> str:
        return ", ".join(self.__parameters)

    def __str__(self) -> str:
        self.__body.SetIndent(self.start_indent)
        retval = self.GetIndentedTemplate()
        retval = retval.replace('NAME', self.__name)
        retval = retval.replace('[P]', self.__ParseParameters())
        retval = retval.replace('[B]', str(self.__body))
        return retval + "\n"


class CppClass(CppItem):

    def __init__(self, name: str):
        super().__init__(['class [N][H] {', '[I]', '};'])
        self.__name = name
        self.__publicitems = []
        self.__privateitems = []
        self.__inheritance = ''

    def SetInheritance(self, inheritance_class: str, public: bool) -> None:
        self.__inheritance = ''
        if public:
            self.__inheritance = ': public '
        else:
            self.__inheritance = ': private '
        self.__inheritance += '{}'.format(inheritance_class)

    def AddPublicItem(self, item: CppItem) -> None:
        item.SetIndent(self.start_indent + 2)
        self.__publicitems.append(item)

    def AddPrivateItem(self, item: CppItem) -> None:
        item.SetIndent(self.start_indent + 2)
        self.__privateitems.append(item)

    def __ParseItems(self) -> str:
        items = []
        if len(self.__publicitems) > 0:
            items.append(self.Indent(self.start_indent + 1, "public:"))
            for item in self.__publicitems:
                items.append(str(item))

        if len(self.__privateitems) > 0:
            items.append(self.Indent(self.start_indent + 1, "private:"))
            for item in self.__privateitems:
                items.append(str(item))
        return '\n'.join(items)

    def __str__(self) -> str:
        retval = self.GetIndentedTemplate()
        retval = retval.replace('[N]', self.__name)
        retval = retval.replace('[I]', self.__ParseItems())
        retval = retval.replace('[H]', self.__inheritance)
        return retval
