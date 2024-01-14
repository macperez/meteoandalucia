package main

import (
	"encoding/json"
	"fmt"
	"io"
	"meteo/internal/posg"
	"net/http"
)

const URL_BASE string = "https://www.juntadeandalucia.es/agriculturaypesca/ifapa/riaws"

func main() {
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
