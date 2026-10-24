package posg

import (
	"context"
	"database/sql"
	"encoding/csv"
	"fmt"
	"io"
	"log"
	"os"
	"strconv"
	"strings"
	"time"
)

// ImportAemetStationsCSV inserta o actualiza el inventario en una transacción.
// Las provincias deben existir en aemet.provincia con los nombres del CSV.
// Devuelve el número de estaciones procesadas solo si se confirma la importación.
func ImportAemetStationsCSV(ctx context.Context, path string) (int, error) {
	file, err := os.Open(path)
	if err != nil {
		return 0, fmt.Errorf("abrir CSV: %w", err)
	}
	defer file.Close()
	stations, err := readAemetStationsCSV(file)
	if err != nil {
		return 0, err
	}
	conn, err := New()
	if err != nil {
		return 0, err
	}
	defer conn.Close()
	tx, err := conn.db.BeginTx(ctx, nil)
	if err != nil {
		return 0, fmt.Errorf("iniciar importación: %w", err)
	}
	defer tx.Rollback()
	stmt, err := tx.PrepareContext(ctx, `
		INSERT INTO aemet.station (indicativo, nombre, provincia_id, altitud, latitud, longitud, indsinop)
		SELECT $1, $2, id, $4, $5, $6, $7 FROM aemet.provincia
		WHERE upper(btrim(provincia)) = upper(btrim($3))
		ON CONFLICT (indicativo) DO UPDATE SET
		    nombre = EXCLUDED.nombre, provincia_id = EXCLUDED.provincia_id,
		    altitud = EXCLUDED.altitud, latitud = EXCLUDED.latitud,
		    longitud = EXCLUDED.longitud, indsinop = EXCLUDED.indsinop`)
	if err != nil {
		return 0, fmt.Errorf("preparar importación: %w", err)
	}
	defer stmt.Close()
	for i, station := range stations {
		result, err := stmt.ExecContext(ctx, station.code, station.name, station.province,
			station.altitude, station.latitude, station.longitude, station.synoptic)
		if err != nil {
			return 0, fmt.Errorf("registro %d, estación %s: %w", i+2, station.code, err)
		}
		count, err := result.RowsAffected()
		if err != nil {
			return 0, fmt.Errorf("comprobar estación %s: %w", station.code, err)
		}
		if count != 1 {
			return 0, fmt.Errorf("registro %d: provincia %q ausente o ambigua en aemet.provincia", i+2, station.province)
		}
	}
	if err := tx.Commit(); err != nil {
		return 0, fmt.Errorf("confirmar importación: %w", err)
	}
	return len(stations), nil
}

type aemetCSVStation struct {
	code, name, province, latitude, longitude string
	altitude                                  int32
	synoptic                                  sql.NullString
}

func readAemetStationsCSV(input io.Reader) ([]aemetCSVStation, error) {
	reader := csv.NewReader(input)
	header, err := reader.Read()
	if err != nil {
		return nil, fmt.Errorf("leer cabecera CSV: %w", err)
	}
	header[0] = strings.TrimPrefix(header[0], "\ufeff")
	expected := []string{"indicativo", "nombre", "provincia", "altitud", "latitud", "longitud", "indsinop"}
	if strings.Join(header, ",") != strings.Join(expected, ",") {
		return nil, fmt.Errorf("cabecera CSV incorrecta: se esperaba %s", strings.Join(expected, ","))
	}
	var stations []aemetCSVStation
	seen := make(map[string]bool)
	for row := 2; ; row++ {
		record, err := reader.Read()
		if err == io.EOF {
			break
		}
		if err != nil {
			return nil, fmt.Errorf("registro %d: %w", row, err)
		}
		for i := range record {
			record[i] = strings.TrimSpace(record[i])
		}
		if record[0] == "" || record[1] == "" || record[2] == "" {
			return nil, fmt.Errorf("registro %d: indicativo, nombre y provincia son obligatorios", row)
		}
		if seen[record[0]] {
			return nil, fmt.Errorf("registro %d: indicativo duplicado %q", row, record[0])
		}
		seen[record[0]] = true
		altitude, err := strconv.ParseInt(record[3], 10, 32)
		if err != nil {
			return nil, fmt.Errorf("registro %d: altitud inválida %q: %w", row, record[3], err)
		}
		stations = append(stations, aemetCSVStation{code: record[0], name: record[1], province: record[2], altitude: int32(altitude), latitude: record[4], longitude: record[5], synoptic: sql.NullString{String: record[6], Valid: record[6] != ""}})
	}
	return stations, nil
}

type ResultAemetStation struct {
	ProvCode    int
	Province    string
	StationCode string
	StationName string
}

type MeasurementAemet struct {
	Date            time.Time
	Fecha           string `json:"fecha"`
	Id              string `json:"indicativo"`
	Name            string `json:"nombre"`
	Province        string `json:"provincia"`
	AltitudeStr     string `json:"altitud"`
	Altitude        sql.NullFloat64
	AvgTempStr      string `json:"tmed"`
	AvgTemp         sql.NullFloat64
	PrecStr         string `json:"prec"`
	Prec            sql.NullFloat64
	MinTempStr      string `json:"tmin"`
	MinTemp         sql.NullFloat64
	TMinTime        string `json:"horatmin"`
	MaxTempStr      string `json:"tmax"`
	MaxTemp         sql.NullFloat64
	TMaxTime        string `json:"horatmax"`
	DirectionStr    string `json:"dir"`
	Direction       sql.NullFloat64
	AvgVelStr       string `json:"velmedia"`
	AvgVel          sql.NullFloat64
	MaxVelStr       string `json:"racha"`
	MaxVel          sql.NullFloat64
	MaxVelTime      string `json:"horaracha"`
	MaxPressureStr  string `json:"presMax"`
	MaxPressure     sql.NullFloat64
	MaxPressureTime string `json:"horaPresMax"`
	MinPressureStr  string `json:"presMin"`
	MinPressure     sql.NullFloat64
	MinPressureTime string `json:"horaPresMin"`
}

func GetAemetStations() []ResultAemetStation {
	conn, _ := New()

	stationsQuery := `
	select provincia_id as prov_code, p.provincia as province, indicativo as station_code, nombre as station_name
	from aemet.station s
	join aemet.provincia p on p.id = s.provincia_id
	where provincia_id in (4, 11, 14, 18, 21, 23, 29, 41)
	order by province, station_name;`

	fmt.Println(stationsQuery)
	res, err := conn.db.Query(stationsQuery)

	if err != nil {
		log.Fatal(err)
	}

	var stations []ResultAemetStation
	for res.Next() {

		var resStation ResultAemetStation
		err := res.Scan(&resStation.ProvCode, &resStation.Province,
			&resStation.StationCode, &resStation.StationName)
		if err != nil {
			log.Fatal(err)
		}
		stations = append(stations, resStation)
	}
	conn.Close()
	return stations
}

func insertAemetMeasure(conn *DBConnection, measure MeasurementAemet) error {
	var err error
	err = ParseAemetMeasurement(&measure)
	if err != nil {
		fmt.Println("Parsing Error")
		return err
	}

	insertStr := `INSERT INTO aemet.daily_measurement(
			id, station_id, measurement_date, 
			avg_temp, precipitation, min_temp, 
			time_mintemp, max_temp, time_maxtemp, 
			wind_direction, avg_wind, max_wind_speed, 
			time_maxwind, max_press, time_maxpress, 
			min_press, time_minpress)
			VALUES(
				nextval('aemet.daily_measurement_id_seq'::regclass), 
				$1, $2, 
			$3, $4, $5,
			$6, $7, $8,
			$9, $10, $11,
			$12, $13, $14,
			$15, $16);`
	_, err = conn.db.Exec(insertStr,
		measure.Id, measure.Date,
		measure.AvgTemp, measure.Prec, measure.MinTemp,
		measure.TMinTime, measure.MaxTemp, measure.TMaxTime,
		measure.Direction, measure.AvgVel, measure.MaxVel,
		measure.MaxVelTime, measure.MaxPressure, measure.MaxPressureTime,
		measure.MinPressure, measure.MinPressureTime)

	if err != nil {
		fmt.Printf("Error in row %s %s %s\n", measure.Name, measure.Id, measure.Fecha)
		log.Fatal(err)
		return err
	}

	return nil

}

func InsertAemetMeasures(measures []MeasurementAemet) error {

	conn, _ := New()
	fmt.Println("Inserting in database .... ")
	count := 1
	for _, measure := range measures {

		err := insertAemetMeasure(conn, measure)
		if err != nil {
			fmt.Printf("Error in row %s %s %s\n", measure.Name, measure.Id, measure.Fecha)
			fmt.Printf("%+v\n", measure)

			log.Fatal(err)
			break
		}
		count++

	}
	fmt.Printf("%d measurements inserted\n", count)
	conn.Close()
	return nil

}
