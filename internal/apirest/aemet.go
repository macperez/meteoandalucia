package apirest

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"

	_ "github.com/joho/godotenv/autoload"
	"github.com/macperez/meteoandalucia/internal/posg"
)

const URL_BASE_AEMET = "https://opendata.aemet.es/opendata/api/"

var api_key = os.Getenv("API_KEY")

type responseAemet struct {
	Descripcion string `json:"descripcion"`
	Estado      int    `json:"estado"`
	Datos       string `json:"datos"`
	Metadatos   string `json:"metadatos"`
}

func GetMeasurementsAllAemet(from string, to string, insert bool) {
	stations := posg.GetAemetStations()

	for _, station := range stations {
		err := GetAemetMeasurements(station.StationCode, from, to, insert)
		if err != nil {
			fmt.Println(err)
			fmt.Printf("Skipping station %s: %s\n Due to problems with petition\n", station.StationCode, station.StationName)
		}
	}

}

func GetAemetMeasurements(stationId string, fromDateStr string, toDateStr string, persist bool) error {
	var response responseAemet
	apiURL := fmt.Sprintf("valores/climatologicos/diarios/datos/fechaini/%sT00%%3A00%%3A00UTC/fechafin/%sT00%%3A00%%3A00UTC/estacion/%s",
		fromDateStr, toDateStr, stationId)
	apiURL = URL_BASE_AEMET + apiURL
	req, _ := http.NewRequest("GET", apiURL, nil)
	req.Header.Add("cache-control", "no-cache")
	req.Header.Add("api_key", api_key)

	resp, err := http.DefaultClient.Do(req)

	if err != nil {
		fmt.Println("Request Error :", err)
		return err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		fmt.Printf("HTTP ERROR for province station %s :: %d\n", stationId, resp.StatusCode)
		return fmt.Errorf("does not exist data for %s in the period [%s, %s]", stationId, fromDateStr, toDateStr)
	}

	body, _ := io.ReadAll(resp.Body)

	if err = json.Unmarshal(body, &response); err != nil {
		fmt.Println("Request Error :", err)
		return err
	}

	if response.Estado != http.StatusOK {
		return fmt.Errorf("error %d: does not exist data for %s in the period [%s, %s]", response.Estado, stationId, fromDateStr, toDateStr)
	}
	resp, _ = http.Get(response.Datos)

	if err != nil {
		fmt.Println("Request Error :", err)
		return err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		fmt.Println("HTTP ERROR::", resp.StatusCode)
		return fmt.Errorf("does not exist data for %s", stationId)
	}

	body, err = io.ReadAll(resp.Body)
	if err != nil {
		fmt.Println("Error:", err)
		return err
	}

	if persist {
		var measures []posg.MeasurementAemet
		if err := json.Unmarshal(body, &measures); err != nil {
			fmt.Println("Parsing error: ", err)
			return err
		}
		err := posg.InsertAemetMeasures(measures)
		if err != nil {
			fmt.Println("Error:", err)
			return err
		}

	} else {
		fmt.Println(string(body))
	}

	return nil
}
