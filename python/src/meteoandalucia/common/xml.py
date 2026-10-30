"""Lectura incremental de registros XML planos bajo un elemento raíz."""

from collections.abc import Iterator
from pathlib import Path
from xml.etree import ElementTree


class XMLRecords:
    """Iterador reutilizable que libera cada registro tras consumirlo.

    Respeta la codificación declarada por el XML. Conserva textos y distingue
    campos ausentes de elementos vacíos. Las etiquetas incluyen su namespace.
    """

    def __init__(self, path: str | Path, record_tags: set[str]):
        self.path = Path(path)
        self.record_tags = record_tags

    def __iter__(self) -> Iterator[dict[str, str]]:
        with self.path.open("rb") as source:
            context = ElementTree.iterparse(source, events=("start", "end"))
            _, root = next(context)
            depth = 0
            for event, element in context:
                if event == "start":
                    depth += 1
                    continue
                if depth == 1:
                    if element.tag not in self.record_tags:
                        raise ValueError(f"{self.path}: registro XML desconocido: {element.tag}")
                    row = {}
                    for child in element:
                        if len(child) or child.attrib or child.tag in row:
                            raise ValueError(
                                f"{self.path}: campo anidado, con atributos o duplicado: "
                                f"{child.tag}"
                            )
                        row[child.tag] = child.text if child.text is not None else ""
                    yield row
                    root.remove(element)
                    element.clear()
                depth -= 1
