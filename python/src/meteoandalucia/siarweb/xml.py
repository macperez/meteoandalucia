"""Inventario y medidas XML; conserva las variantes de campos entre años."""

from decimal import Decimal
from pathlib import Path

from meteoandalucia.common.xml import XMLRecords

STATION_FIELDS = ("ID_EST", "NOMBRE", "PROVINCIA", "MUNICIPIO", "LATITUD", "LONGITUD", "ALTITUD")
MEASUREMENT_TAGS = {"Diario", "Diario_OpenData", "Cns_OpenData", "Cns_OpenData_ActualizarFcha"}
# Unión de las etiquetas originales encontradas en los XML de 2002–2026.
MEASUREMENT_FIELDS = (
    "COD_EST",
    "cod_est",
    "FECHA",
    "T_MAX",
    "T_MED",
    "T_MIN",
    "T_Max",
    "T_Med",
    "T_Min",
    "H_R_MAX",
    "H_R_MED",
    "H_R_MIN",
    "H_R_Max",
    "H_R_Med",
    "H_R_Min",
    "RADIACION",
    "Radiacion",
    "PromedioDeRadiacion",
    "Radicion_Med",
    "LLUVIA",
    "Lluvia",
    "SumaDeLluvia",
    "Lluvia_acum",
    "LLUVIA_MIN",
    "T_S_MAX",
    "T_S_MED",
    "T_S_MIN",
    "V_MAX",
    "V_MED",
    "V_MIN",
    "V_Max",
    "V_Med",
    "V_Min",
    "CV1",
    "CV2",
    "CV3",
    "CV4",
    "SumaDeCV1",
    "SumaDeCV2",
    "SumaDeCV3",
    "SumaDeCV4",
    "DIRECCION",
    "Direccion",
    "PromedioDeDireccion",
    "HORAS",
    "H_T",
    "H_HR",
    "H_R",
    "H_LL",
    "H_TS",
    "H_V",
    "H_D",
    "CALCULOS",
    "MTMEN0",
    "MTMEN7",
    "MTMA30",
    "MVMA50",
)


class StationsXML(XMLRecords):
    def __init__(self, path: str | Path):
        super().__init__(path, {"Identificacion_Estaciones_OpenDATA"})

    def read(self) -> list[dict]:
        rows, seen = [], set()
        for raw in self:
            if set(raw) - set(STATION_FIELDS) or not {"ID_EST", "NOMBRE", "PROVINCIA"} <= set(raw):
                raise ValueError(f"{self.path}: campos de estación incorrectos")
            row = {key.lower(): raw.get(key, "").strip() for key in STATION_FIELDS}
            if not row["id_est"] or not row["nombre"]:
                raise ValueError(f"{self.path}: código y nombre obligatorios")
            if row["id_est"] in seen:
                raise ValueError(f"{self.path}: estación duplicada: {row['id_est']}")
            seen.add(row["id_est"])
            for key in ("provincia", "municipio", "altitud"):
                row[key] = int(row[key]) if row[key] else None
            row["provincia_id"] = row.pop("provincia")
            if row["provincia_id"] is None:
                raise ValueError(f"{self.path}: provincia obligatoria")
            for key in ("latitud", "longitud"):
                value = Decimal(row[key]) if row[key] else None
                if value is not None and not value.is_finite():
                    raise ValueError(f"{self.path}: coordenada no finita: {key}")
                row[key] = value
            rows.append(row)
        if not rows:
            raise ValueError(f"{self.path}: inventario vacío")
        return rows


class MeasurementsXML(XMLRecords):
    def __init__(self, path: str | Path):
        super().__init__(path, MEASUREMENT_TAGS)

    def __iter__(self):
        for row in super().__iter__():
            unknown = set(row) - set(MEASUREMENT_FIELDS)
            if unknown:
                raise ValueError(f"{self.path}: campos desconocidos: {', '.join(sorted(unknown))}")
            if "FECHA" not in row or not {"COD_EST", "cod_est"}.intersection(row):
                raise ValueError(f"{self.path}: faltan los campos de estación o fecha")
            yield row
