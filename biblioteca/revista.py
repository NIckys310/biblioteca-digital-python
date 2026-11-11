"""Subclase Revista: hereda de Publicacion y añade ISSN, número, volumen y periodicidad."""
from __future__ import annotations

import re
from typing import Any, ClassVar

from .publicacion import Publicacion

_ISSN = re.compile(r"^\d{4}-\d{3}[\dX]$")


class Revista(Publicacion):
    DIAS_PRESTAMO: ClassVar[int] = 7          # override: las revistas se prestan menos tiempo
    PERIODICIDADES: ClassVar[frozenset[str]] = frozenset(
        {"semanal", "quincenal", "mensual", "trimestral", "anual"}
    )

    def __init__(
        self,
        titulo: str,
        anio: int,
        editorial: str,
        *,
        issn: str,
        numero: int,
        volumen: int,
        periodicidad: str = "mensual",
        **kwargs: Any,
    ) -> None:
        super().__init__(titulo, anio, editorial, **kwargs)
        issn = issn.strip().upper()
        if not _ISSN.match(issn):
            raise ValueError(f"ISSN inválido: {issn!r} (formato 1234-567X)")
        if numero <= 0 or volumen <= 0:
            raise ValueError("Número y volumen deben ser positivos.")
        if periodicidad not in self.PERIODICIDADES:
            raise ValueError(f"Periodicidad no válida: {periodicidad!r}")
        self.issn = issn
        self.numero = numero
        self.volumen = volumen
        self.periodicidad = periodicidad

    def descripcion(self) -> str:   # sobrescritura (override)
        return (f"Revista: '{self.titulo}' Vol. {self.volumen}, Nº {self.numero} "
                f"({self.periodicidad}, {self.anio}) – {self.disponibles}/{self.total} disponibles")

    def _campos_propios(self) -> dict[str, Any]:
        return {"issn": self.issn, "numero": self.numero,
                "volumen": self.volumen, "periodicidad": self.periodicidad}
