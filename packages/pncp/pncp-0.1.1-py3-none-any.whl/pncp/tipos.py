from typing import Any, Callable, Self

from pydantic import BaseModel


class Lista[X](list[X]):
    def filtrar(self, funcao: Callable[[X], bool]) -> "Lista[X]":
        return Lista(filter(funcao, self))

    def transformar[Y](self, funcao: Callable[[X], Y]) -> "Lista[Y]":
        return Lista(map(funcao, self))


def para_camel_case(string_em_snake_case: str) -> str:
    parts = string_em_snake_case.split("_")
    if not parts:
        return ""
    return parts[0] + "".join(word[0].upper() + word[1:] for word in parts[1:])


class ModeloBasico(BaseModel):
    class Config:
        arbitrary_types_allowed = True
        populate_by_name = True
        alias_generator = para_camel_case

    def como_dicionario(self) -> dict[str, Any]:
        return self.model_dump()

    @classmethod
    def de_dicionario(cls, dicionario: dict[str, Any]) -> Self:
        return cls.model_validate(dicionario)
