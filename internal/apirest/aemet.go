package apirest

import "github.com/macperez/meteoandalucia/internal/posg"

func GetMeasurementsAllAemet(from string, to string, insert bool) {
	stations := posg.GetStations(true)

	for _, station := range stations {
		GetMeasurements(station.ProvCode, station.StationCode, from, to, true, insert)
	}
}
