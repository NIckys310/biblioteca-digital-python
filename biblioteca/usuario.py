"""Usuario de la biblioteca. Sus préstamos van EMBEBIDOS, igual que en MongoDB."""
from __future__ import annotations

import re
import uuid
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any, ClassVar

from .publicacion import Publicacion

_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class LimitePrestamosError(Exception):
    """El usuario alcanzó el máximo de préstamos activos de su membresía."""


@dataclass
class Prestamo:
    publicacion_id: str
    titulo: str          # copia desnormalizada: evita una "consulta extra" para mostrar el título
    tipo: str
    fecha_prestamo: date
    fecha_limite: date
    devuelto: bool = False

    @property
    def vencido(self) -> bool:
        return not self.devuelto and date.today() > self.fecha_limite

    def to_dict(self) -> dict[str, Any]:
        return {
            "publicacionId": self.publicacion_id,
            "titulo": self.titulo,
            "tipo": self.tipo,
            "fechaPrestamo": self.fecha_prestamo.isoformat(),
            "fechaLimite": self.fecha_limite.isoformat(),
            "devuelto": self.devuelto,
        }


class Usuario:
    LIMITES: ClassVar[dict[str, int]] = {"basica": 3, "premium": 10}

    def __init__(self, nombre: str, email: str, membresia: str = "basica",
                 id: str | None = None) -> None:
        if not nombre.strip():
            raise ValueError("El nombre no puede estar vacío.")
        if not _EMAIL.match(email):
            raise ValueError(f"Email inválido: {email!r}")
        if membresia not in self.LIMITES:
            raise ValueError(f"Membresía no válida: {membresia!r}")
        self.id = id or uuid.uuid4().hex
        self.nombre = nombre.strip()
        self.email = email.lower()
        self.membresia = membresia
        self.prestamos: list[Prestamo] = []

    @property
    def prestamos_activos(self) -> list[Prestamo]:
        return [p for p in self.prestamos if not p.devuelto]

    def solicitar_prestamo(self, publicacion: Publicacion, hoy: date | None = None) -> Prestamo:
        """Acepta CUALQUIER Publicacion (Libro, Revista...) gracias al polimorfismo."""
        if len(self.prestamos_activos) >= self.LIMITES[self.membresia]:
            raise LimitePrestamosError(f"{self.nombre} alcanzó su límite de préstamos.")
        hoy = hoy or date.today()
        publicacion.prestar()                    # lanza SinEjemplaresError si no hay stock
        prestamo = Prestamo(
            publicacion_id=publicacion.id,
            titulo=publicacion.titulo,
            tipo=publicacion.tipo,
            fecha_prestamo=hoy,
            fecha_limite=hoy + timedelta(days=publicacion.DIAS_PRESTAMO),
        )
        self.prestamos.append(prestamo)
        return prestamo

    def devolver(self, publicacion: Publicacion) -> Prestamo:
        for prestamo in self.prestamos_activos:
            if prestamo.publicacion_id == publicacion.id:
                publicacion.devolver()
                prestamo.devuelto = True
                return prestamo
        raise LookupError(f"{self.nombre} no tiene un préstamo activo de '{publicacion.titulo}'.")

    def to_dict(self) -> dict[str, Any]:
        return {
            "_id": self.id,
            "nombre": self.nombre,
            "email": self.email,
            "membresia": self.membresia,
            "prestamos": [p.to_dict() for p in self.prestamos],
        }

    def __repr__(self) -> str:
        return f"Usuario(email={self.email!r}, prestamos_activos={len(self.prestamos_activos)})"
