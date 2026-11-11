"""Subclase Libro: hereda de Publicacion y añade ISBN, autores, páginas y género."""
from __future__ import annotations

import re
from typing import Any

from .publicacion import Publicacion

_ISBN = re.compile(r"^(\d{9}[\dX]|97[89]\d{10})$")


class Libro(Publicacion):
    def __init__(
        self,
        titulo: str,
        anio: int,
        editorial: str,
        *,
        isbn: str,
        autores: list[str],
        paginas: int,
        genero: str = "General",
        **kwargs: Any,
    ) -> None:
        super().__init__(titulo, anio, editorial, **kwargs)   # reutiliza la lógica común
        if not autores:
            raise ValueError("Un libro necesita al menos un autor.")
        if paginas <= 0:
            raise ValueError("El número de páginas debe ser positivo.")
        self.isbn = self._normalizar_isbn(isbn)
        self.autores = list(autores)
        self.paginas = paginas
        self.genero = genero

    @staticmethod
    def _normalizar_isbn(isbn: str) -> str:
        limpio = re.sub(r"[-\s]", "", isbn).upper()
        if not _ISBN.match(limpio):
            raise ValueError(f"ISBN inválido: {isbn!r}")
        return limpio

    def descripcion(self) -> str:   # sobrescritura (override)
        return (f"Libro: '{self.titulo}' de {', '.join(self.autores)} "
                f"({self.anio}, {self.paginas} págs.) – {self.disponibles}/{self.total} disponibles")

    def _campos_propios(self) -> dict[str, Any]:
        return {"isbn": self.isbn, "autores": list(self.autores),
                "paginas": self.paginas, "genero": self.genero}
