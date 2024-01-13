package main

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
)

type Provincia struct {
	ID     int    `json:"id"`
	Nombre string `json:"nombre"`
}

type Estacion struct {
	Provincia      Provincia `json:"provincia"`
	CodigoEstacion string    `json:"codigoEstacion"`
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

func main() {
	apiURL := "https://www.juntadeandalucia.es/agriculturaypesca/ifapa/riaws/estaciones"

	resp, err := http.Get(apiURL)
	if err != nil {
		fmt.Println("Request Error :", err)
		return
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		fmt.Println("HTTP ERROR. Código de estado:", resp.StatusCode)
		return
	}

	var estaciones []Estacion
	body, _ := io.ReadAll(resp.Body)

	err = json.Unmarshal([]byte(body), &estaciones)
	if err != nil {
		fmt.Println("Error al decodificar la respuesta JSON:", err)
		return
	}

	// Imprime la información parseada
	fmt.Println("Estaciones:")
	for _, estacion := range estaciones {
		fmt.Printf("Nombre: %s, Provincia: %s, Activa: %t\n", estacion.Nombre, estacion.Provincia.Nombre, estacion.Activa)
	}

}
