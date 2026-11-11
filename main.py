"""Demostración: herencia, polimorfismo y serialización a documentos MongoDB."""
import json

from biblioteca import Libro, Publicacion, Revista, SinEjemplaresError, Usuario


def crear_catalogo() -> list[Publicacion]:
    return [
        Libro("Cien años de soledad", 1967, "Sudamericana",
              isbn="978-0307474728", autores=["Gabriel García Márquez"],
              paginas=417, genero="Novela", categorias=["literatura"], ejemplares=3),
        Libro("Clean Code", 2008, "Prentice Hall",
              isbn="978-0132350884", autores=["Robert C. Martin"],
              paginas=464, genero="Tecnología", categorias=["software"], ejemplares=2),
        Revista("Investigación y Ciencia", 2024, "Prensa Científica",
                issn="0210-136X", numero=570, volumen=48, periodicidad="mensual",
                categorias=["ciencia"], ejemplares=1),
    ]


def titulo(texto: str) -> None:
    print(f"\n== {texto} ==")


def main() -> None:
    catalogo = crear_catalogo()

    titulo("Catálogo (polimorfismo: cada clase implementa su descripción)")
    for pub in catalogo:
        print(f"- {pub}")

    libro, revista = catalogo[0], catalogo[2]
    ana = Usuario("Ana Torres", "ana.torres@example.com", membresia="premium")
    luis = Usuario("Luis Gómez", "luis.gomez@example.com")

    titulo("Préstamos (plazo heredado vs. sobrescrito)")
    for pub in (libro, revista):
        p = ana.solicitar_prestamo(pub)
        print(f"Ana lleva '{p.titulo}' ({p.tipo}) hasta {p.fecha_limite}")

    try:
        luis.solicitar_prestamo(revista)
    except SinEjemplaresError as error:
        print(f"Luis no puede: {error}")

    ana.devolver(revista)
    luis.solicitar_prestamo(revista)
    print(f"Tras la devolución, Luis obtiene la revista. {revista}")

    titulo("Documento MongoDB del libro")
    doc = libro.to_dict()
    print(json.dumps(doc, ensure_ascii=False, indent=2))

    copia = Publicacion.from_dict(doc)           # la fábrica elige la subclase correcta
    assert isinstance(copia, Libro) and copia.isbn == libro.isbn
    assert copia.disponibles == libro.disponibles
    print(f"Reconstruido desde dict -> {copia!r}")

    titulo("Documento MongoDB de Ana (préstamos embebidos)")
    print(json.dumps(ana.to_dict(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
