package posg

import (
	"database/sql"
	"fmt"
	"log"
	"time"
)

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
	select provincia_id as prov_code, provincia as province, indicativo as station_code, nombre as station_name
	from aemet.station s 
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
