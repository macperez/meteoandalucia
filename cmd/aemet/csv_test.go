package main

import (
	"encoding/csv"
	"os"
	"path/filepath"
	"reflect"
	"testing"
)

func TestExportStationsCSV(t *testing.T) {
	path := filepath.Join(t.TempDir(), "estaciones.csv")
	stations := []station{{Code: "0010", Name: "MÁLAGA, \"AEROPUERTO\"", Province: "MÁLAGA", Altitude: "7", Latitude: "364000N", Longitude: "042900W", SynopticCode: "08482"}}
	if err := exportStationsCSV(path, stations); err != nil {
		t.Fatal(err)
	}
	file, err := os.Open(path)
	if err != nil {
		t.Fatal(err)
	}
	defer file.Close()
	got, err := csv.NewReader(file).ReadAll()
	if err != nil {
		t.Fatal(err)
	}
	want := [][]string{
		{"indicativo", "nombre", "provincia", "altitud", "latitud", "longitud", "indsinop"},
		{"0010", "MÁLAGA, \"AEROPUERTO\"", "MÁLAGA", "7", "364000N", "042900W", "08482"},
	}
	if !reflect.DeepEqual(got, want) {
		t.Fatalf("CSV inesperado: %#v", got)
	}
	if err := exportStationsCSV(filepath.Dir(path), stations); err == nil {
		t.Fatal("se esperaba error al escribir sobre un directorio")
	}
}
