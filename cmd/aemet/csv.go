package main

import (
	"encoding/csv"
	"fmt"
	"os"
)

func exportStationsCSV(path string, stations []station) error {
	file, err := os.Create(path)
	if err != nil {
		return fmt.Errorf("crear CSV %s: %w", path, err)
	}
	writer := csv.NewWriter(file)
	records := [][]string{{"indicativo", "nombre", "provincia", "altitud", "latitud", "longitud", "indsinop"}}
	for _, station := range stations {
		records = append(records, []string{station.Code, station.Name, station.Province, station.Altitude, station.Latitude, station.Longitude, station.SynopticCode})
	}
	writeErr := writer.WriteAll(records)
	closeErr := file.Close()
	if writeErr != nil {
		return fmt.Errorf("escribir CSV %s: %w", path, writeErr)
	}
	if closeErr != nil {
		return fmt.Errorf("cerrar CSV %s: %w", path, closeErr)
	}
	return nil
}
