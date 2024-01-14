package posg

import (
	"database/sql"
	"fmt"
	"log"

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
					prov, id_station, station_name, under_plastic, active, visible,
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
