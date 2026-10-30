"""Casos de uso que coordinan clientes API y repositorios."""

from dataclasses import dataclass, field


@dataclass
class BatchResult:
    measurements: list[dict] = field(default_factory=list)
    inserted: int = 0
    errors: dict[str, str] = field(default_factory=dict)


def aemet_measurements(client, repository, station: str, start: str, end: str, persist=False):
    rows = client.measurements(station, start, end)
    if persist:
        repository.insert_measurements(rows)
    return rows


def riaweb_measurements(
    client,
    repository,
    province: int,
    station: int,
    start: str,
    end: str | None = None,
    et0: bool = True,
    persist: bool = False,
):
    rows = (
        client.measurements(province, station, start, end, et0)
        if end
        else [client.measurement(province, station, start, et0)]
    )
    if persist:
        repository.insert_measurements(rows, province, station)
    return rows


def measurements_all(client, repository, start: str, end: str, *, provider: str, persist=False):
    """Continúa tras un fallo por estación y devuelve los errores al llamador."""
    from meteoandalucia.common.parsing import validate_date_range

    validate_date_range(start, end)
    if provider not in {"aemet", "riaweb"}:
        raise ValueError("Proveedor desconocido")
    stations = (
        repository.stations() if provider == "aemet" else repository.stations(active_only=True)
    )
    result = BatchResult()
    for station in stations:
        code = station["station_code"]
        key = str(code) if provider == "aemet" else f"{station['prov_code']}/{code}"
        try:
            if provider == "aemet":
                rows = client.measurements(code, start, end)
                if persist:
                    result.inserted += repository.insert_measurements(rows)
            else:
                rows = client.measurements(station["prov_code"], code, start, end, True)
                if persist:
                    result.inserted += repository.insert_measurements(
                        rows, station["prov_code"], code
                    )
            result.measurements.extend(rows)
        except Exception as exc:
            result.errors[key] = str(exc)
    return result
