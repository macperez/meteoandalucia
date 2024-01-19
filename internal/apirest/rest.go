package apirest

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"

	"github.com/macperez/meteoandalucia/internal/posg"
)

const URL_BASE string = "https://www.juntadeandalucia.es/agriculturaypesca/ifapa/riaws"

func GetStations(insert bool) {
	apiURL := "/estaciones"

	resp, err := http.Get(URL_BASE + apiURL)
	if err != nil {
		fmt.Println("Request Error :", err)
		return
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		fmt.Println("HTTP ERROR::", resp.StatusCode)
		return
	}

	var estaciones []posg.Estacion
	body, _ := io.ReadAll(resp.Body)

	err = json.Unmarshal([]byte(body), &estaciones)
	if err != nil {
		fmt.Println("Error trying to decode JSON:", err)
		return
	}
	if insert {
		fmt.Printf("Trying to insert %d stations", len(estaciones))
		posg.InsertStations(estaciones)
	} else {
		for _, est := range estaciones {
			fmt.Printf("provincia: %d | codigo_estacion = %d | nombre_estacion = %s\n", est.Provincia.ID, est.CodigoEstacion, est.Nombre)
		}
	}

}

func GetMeasurement(provId int, stationId int, dateStr string, ethoAlg bool, persist bool) {
	apiURL := URL_BASE + fmt.Sprintf("/datosdiarios/%d/%d/%s/%t", provId, stationId, dateStr, ethoAlg)
	resp, err := http.Get(apiURL)
	if err != nil {
		fmt.Println("Request Error :", err)
		return
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		fmt.Println("HTTP ERROR::", resp.StatusCode)
		return
	}

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		fmt.Println("Error:", err)
		return
	}

	fmt.Println("JSON:")
	fmt.Println(string(body))
	if persist {
		posg.InsertOneMeasure(body, provId, stationId)
	}
}

func GetMeasurements(provId int, stationId int, fromDateStr string, toDateStr string, ethoAlg bool, persist bool) {

	apiURL := URL_BASE + fmt.Sprintf("/datosdiarios/%d/%d/%s/%s/%t", provId, stationId, fromDateStr, toDateStr, false)
	resp, err := http.Get(apiURL)
	if err != nil {
		fmt.Println("Request Error :", err)
		return
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		fmt.Printf("HTTP ERROR for province %d and station %d :: %d\n", provId, stationId, resp.StatusCode)
		return
	}

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		fmt.Println("Error:", err)
		return
	}

	if persist {

		fmt.Printf("Inserting prov %d, station %d ...(%s / %s)\n", provId, stationId, fromDateStr, toDateStr)
		posg.InsertMeasures(body, provId, stationId)
	} else {
		fmt.Println("JSON:")
		fmt.Println(string(body))

	}

}

func GetMeasurementsAll(from string, to string, insert bool) {
	stations := posg.GetStations()
	for _, station := range stations {
		GetMeasurements(station.ProvCode, station.StationCode, from, to, true, insert)
	}
}
