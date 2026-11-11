"""Clase base abstracta de la jerarquía de publicaciones."""
from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from datetime import date
from typing import Any, ClassVar


class SinEjemplaresError(Exception):
    """No quedan ejemplares disponibles para prestar."""


class Publicacion(ABC):
    """Superclase: define lo que TODA publicación tiene y sabe hacer."""

    ANIO_MINIMO: ClassVar[int] = 1450
    DIAS_PRESTAMO: ClassVar[int] = 14          # las subclases pueden sobrescribirlo
    _registro: ClassVar[dict[str, type[Publicacion]]] = {}

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """Registra cada subclase para poder reconstruirla desde un documento."""
        super().__init_subclass__(**kwargs)
        Publicacion._registro[cls.__name__] = cls

    def __init__(
        self,
        titulo: str,
        anio: int,
        editorial: str,
        *,
        categorias: list[str] | None = None,
        ejemplares: int = 1,
        id: str | None = None,
    ) -> None:
        if not titulo or not titulo.strip():
            raise ValueError("El título no puede estar vacío.")
        if not self.ANIO_MINIMO <= anio <= date.today().year:
            raise ValueError(f"Año fuera de rango: {anio}")
        if ejemplares < 0:
            raise ValueError("El número de ejemplares no puede ser negativo.")

        self.id = id or uuid.uuid4().hex
        self.titulo = titulo.strip()
        self.anio = anio
        self.editorial = editorial.strip()
        self.categorias = list(categorias or [])
        self._total = ejemplares
        self._disponibles = ejemplares

    # ---------- Comportamiento heredado por todas las subclases ----------
    @property
    def tipo(self) -> str:
        """Discriminador: coincide con el campo `tipo` del documento MongoDB."""
        return type(self).__name__

    @property
    def total(self) -> int:
        return self._total

    @property
    def disponibles(self) -> int:
        return self._disponibles

    def prestar(self) -> None:
        if self._disponibles == 0:
            raise SinEjemplaresError(f"'{self.titulo}' no tiene ejemplares disponibles.")
        self._disponibles -= 1

    def devolver(self) -> None:
        if self._disponibles >= self._total:
            raise ValueError(f"Todos los ejemplares de '{self.titulo}' ya están en la biblioteca.")
        self._disponibles += 1

    # ---------- Contrato que cada subclase DEBE implementar ----------
    @abstractmethod
    def descripcion(self) -> str:
        """Texto legible propio de cada tipo de publicación."""

    @abstractmethod
    def _campos_propios(self) -> dict[str, Any]:
        """Atributos exclusivos de la subclase, para serializar."""

    # ---------- Serialización compatible con MongoDB ----------
    def to_dict(self) -> dict[str, Any]:
        return {
            "_id": self.id,
            "tipo": self.tipo,
            "titulo": self.titulo,
            "anio": self.anio,
            "editorial": self.editorial,
            "categorias": list(self.categorias),
            "inventario": {"total": self._total, "disponibles": self._disponibles},
            **self._campos_propios(),
        }

    @classmethod
    def from_dict(cls, doc: dict[str, Any]) -> Publicacion:
        """Fábrica polimórfica: devuelve un Libro o una Revista según `tipo`."""
        datos = dict(doc)
        tipo = datos.pop("tipo", None)
        subclase = cls._registro.get(tipo)
        if subclase is None:
            raise ValueError(f"Tipo de publicación desconocido: {tipo!r}")

        inventario = datos.pop("inventario", {})
        for meta in ("createdAt", "updatedAt", "__v"):      # metadatos de Mongoose
            datos.pop(meta, None)
        id_doc = datos.pop("_id", None)

        obj = subclase(
            id=str(id_doc) if id_doc is not None else None,
            ejemplares=inventario.get("total", 1),
            **datos,
        )
        obj._disponibles = inventario.get("disponibles", obj.total)
        return obj

    def __str__(self) -> str:
        return self.descripcion()

    def __repr__(self) -> str:
        return f"{self.tipo}(id={self.id!r}, titulo={self.titulo!r})"
