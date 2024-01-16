package apirest

import (
	"encoding/json"
	"fmt"
	"github.com/macperez/meteoandalucia/internal/posg"
	"io"
	"net/http"
)

const URL_BASE string = "https://www.juntadeandalucia.es/agriculturaypesca/ifapa/riaws"

func GetStations() {
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
	fmt.Printf("Trying to insert %d stations", len(estaciones))
	posg.InsertStations(estaciones)
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
		posg.InsertMeasure(body, provId, stationId)
	}
}
