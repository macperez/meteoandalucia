package posg

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"time"

	_ "github.com/lib/pq"
)

const (
	host     = "172.17.0.2"
	port     = 5432
	user     = "postgres"
	password = "admin"
	dbname   = "postgres"
)

type Provincia struct {
	ID     int    `json:"id"`
	Nombre string `json:"nombre"`
}

type Estacion struct {
	Provincia      Provincia `json:"provincia"`
	CodigoEstacion int       `json:"codigoEstacion,string,omitempty"`
	Nombre         string    `json:"nombre"`
	BajoPlastico   bool      `json:"bajoplastico"`
	Activa         bool      `json:"activa"`
	Visible        bool      `json:"visible"`
	Longitud       string    `json:"longitud"`
	Latitud        string    `json:"latitud"`
	Altitud        int       `json:"altitud"`
	XUTM           float64   `json:"xutm"`
	YUTM           float64   `json:"yutm"`
	Huso           int       `json:"huso"`
}

type Measurement struct {
	Estacion        Estacion
	Fecha           time.Time
	FechaStr        string  `json:"fecha"`
	Dia             int     `json:"dia"`
	TempMedia       float64 `json:"tempMedia"`
	TempMax         float64 `json:"tempMax"`
	HorMinTempMax   string  `json:"horMinTempMax"`
	TempMin         float64 `json:"tempMin"`
	HorMinTempMin   string  `json:"horMinTempMin"`
	HumedadMedia    float64 `json:"humedadMedia"`
	HumedadMax      float64 `json:"humedadMax"`
	HorMinHumMax    string  `json:"horMinHumMax"`
	HumedadMin      float64 `json:"humedadMin"`
	HorMinHumMin    string  `json:"horMinHumMin"`
	VelViento       float64 `json:"velViento"`
	DirViento       float64 `json:"dirViento"`
	VelVientoMax    float64 `json:"velVientoMax"`
	HorMinVelMax    string  `json:"horMinVelMax"`
	DirVientoVelMax float64 `json:"dirVientoVelMax"`
	Radiacion       float64 `json:"radiacion"`
	Precipitacion   float64 `json:"precipitacion"`
	Bateria         float64 `json:"bateria"`
	FechaUtlMod     string  `json:"fechaUtlMod"`
	Et0             float64 `json:"et0"`
}

func (est Estacion) String() string {
	return fmt.Sprintf("prov: %d, nombre: %s", est.Provincia.ID, est.Nombre)
}

var db *sql.DB

func closeConnection() {
	db.Close()
	fmt.Println("Connection close")
}

func init() {

	connStr := fmt.Sprintf("host=%s port=%d user=%s password=%s dbname=%s sslmode=disable",
		host, port, user, password, dbname)

	fmt.Println(connStr)
	var err error
	db, err = sql.Open("postgres", connStr)
	if err != nil {
		log.Fatal(err)
	}

	err = db.Ping()
	if err != nil {
		log.Fatal(err)
	}
	if db != nil {
		fmt.Println("Succesful connection")
	}

}

func Truncate(table string) error {
	query := fmt.Sprintf("TRUNCATE TABLE %s;", table)

	_, err := db.Exec(query)
	if err != nil {
		log.Println("Error truncateing table", err)
		return err
	}

	log.Println("Truncate ok")
	return nil
}

func InsertStations(estaciones []Estacion) {

	// Iterar sobre la slice e insertar en la tabla
	for _, estacion := range estaciones {
		fmt.Printf("%s\n", estacion)
		_, err := db.Exec(`
				INSERT INTO meteo.station (
					prov, station_code, station_name, under_plastic, active, visible,
					longitude, latitude, altitude, xutm, yutm, huso
				) VALUES (
					$1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12
				);
			`, estacion.Provincia.ID, estacion.CodigoEstacion, estacion.Nombre, estacion.BajoPlastico, estacion.Activa, estacion.Visible,
			estacion.Longitud, estacion.Latitud, estacion.Altitud, estacion.XUTM, estacion.YUTM, estacion.Huso)

		if err != nil {
			fmt.Printf("Error in row %s", estacion)
			log.Fatal(err)
		}
	}
	closeConnection()
	fmt.Println("Data inserted")
}

func InsertMeasure(data []byte, provId int, stationId int) error {
	var measure Measurement
	fmt.Println("Insert Measure")

	if err := json.Unmarshal(data, &measure); err != nil {
		return err
	}

	dat, err := time.Parse("2006-01-02", measure.FechaStr)
	if err != nil {
		return err
	}
	measure.Estacion.Provincia.ID = provId
	measure.Estacion.CodigoEstacion = stationId
	measure.Fecha = dat
	insertStr := `INSERT INTO meteo.daily_measurement(
		id, prov_id, station_id, 
		measurement_date, max_temp, min_temp, 
		avg_temp, time_maxtemp, time_mintemp, 
		max_humid, min_humid, avg_humid, 
		time_maxhumid, time_minhumid, wind_speed, 
		wind_direction, max_wind_speed, direction_max_wind, 
		time_maxwind, radiation, precipitation, 
		batery, dateutlmod, et0)
			VALUES(nextval('meteo.daily_measurement_id_seq'::regclass), 
		$1, $2, 
		$3, $4, $5, 
		$6, $7, $8, 
		$9, $10, $11, 
		$12, $13, $14, 
		$15, $16, $17, 
		$18, $19, $20, 
		$21, $22, $23);`
	_, err = db.Exec(insertStr,
		measure.Estacion.Provincia.ID, measure.Estacion.CodigoEstacion,
		measure.Fecha, measure.TempMax, measure.TempMin,
		measure.TempMedia, measure.HorMinTempMax, measure.HorMinTempMin,
		measure.HumedadMax, measure.HumedadMin, measure.HumedadMedia,
		measure.HorMinHumMax, measure.HorMinHumMin, measure.VelViento,
		measure.DirViento, measure.VelVientoMax, measure.DirVientoVelMax,
		measure.HorMinVelMax, measure.Radiacion, measure.Precipitacion,
		measure.Bateria, measure.FechaUtlMod, measure.Et0)

	if err != nil {
		fmt.Printf("Error in row %d %d %s", measure.Estacion.Provincia.ID, measure.Estacion.CodigoEstacion, measure.Fecha)
		log.Fatal(err)
	}
	return nil
}
