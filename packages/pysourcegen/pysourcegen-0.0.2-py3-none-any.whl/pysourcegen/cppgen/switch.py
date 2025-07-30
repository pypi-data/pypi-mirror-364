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


class CppSwitchCase(CppItem):

    def __init__(self, case: str, body: CppBody):
        super().__init__(["case [CASE]:", "[B]", "break;"])
        self.__case = case
        self.__body = body

    def __str__(self) -> str:
        self.__body.SetIndent(self.start_indent)
        retval = self.GetIndentedTemplate()
        retval = retval.replace('[CASE]', self.__case)
        retval = retval.replace('[B]', str(self.__body))
        return retval


class CppSwitchDefault(CppItem):

    def __init__(self, body: CppBody):
        super().__init__(["default:", "[B]", "break;"])
        self.__body = body

    def __str__(self) -> str:
        self.__body.SetIndent(self.start_indent)
        retval = self.GetIndentedTemplate()
        retval = retval.replace('[B]', str(self.__body))
        return retval


class CppSwitch(CppItem):

    def __init__(self, variable: str, body: CppBody):
        super().__init__(["switch ([VAR])", "[B]"])
        self.__variable = variable
        self.__body = body

    def __str__(self) -> str:
        self.__body.SetIndent(self.start_indent)
        retval = self.GetIndentedTemplate()
        retval = retval.replace('[VAR]', self.__variable)
        retval = retval.replace('[B]', str(self.__body))
        return retval
