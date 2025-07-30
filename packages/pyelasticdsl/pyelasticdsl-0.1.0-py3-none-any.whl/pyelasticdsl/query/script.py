from typing import Any

from pyelasticdsl.dsl import Query

class Script(Query):

    def __init__(self, script: str):
        self.__script: str = script
        self.__typ: str = "inline"
        self.__lang: str = ""
        self.__params: dict[str, Any] = {}

    @classmethod
    def new_inline(cls, script: str) -> "Script":
        return cls(script).type("inline")

    @classmethod
    def new_stored(cls, script: str) -> "Script":
        return cls(script).type("id")

    def script(self, script: str) -> "Script":
        self.__script = script
        return self

    def type(self, typ: str) -> "Script":
        self.__typ = typ
        return self

    def lang(self, lang: str) -> "Script":
        self.__lang = lang
        return self

    def param(self, name: str, value: Any) -> "Script":
        self.__params[name] = value
        return self

    def params(self, params: dict[str, Any]) -> "Script":
        self.__params = params
        return self

    def to_dict(self) -> dict[str, Any] | str:
        # 简化处理，不做错误抛出，调用者负责传入有效参数
        if not self.__typ and not self.__lang and not self.__params:
            return self.__script

        source = {}

        # 6.x后，typ只能是 "source" 或 "id"，这里inline对应source
        if not self.__typ or self.__typ == "inline":
            src = self.__raw_script_source(self.__script)
            source["source"] = src
        else:
            source["id"] = self.__script

        if self.__lang:
            source["lang"] = self.__lang
        if self.__params:
            source["params"] = self.__params

        return source

    def __raw_script_source(self, script: str) -> str:
        v = script.strip()
        # 如果脚本不是以 { 开头且不是以 " 开头，进行引号包裹
        if not (v.startswith("{") or v.startswith('"')):
            v = f'"{v}"'
        return v
