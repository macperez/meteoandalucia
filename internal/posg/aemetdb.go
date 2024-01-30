package posg

import (
	"fmt"
	"log"
)

type ResultAemetStation struct {
	ProvCode    int
	Province    string
	StationCode string
	StationName string
}

func GetAemetStations() []ResultAemetStation {
	conn, _ := New()

	stationsQuery := `
	select provincia_id as prov_code, provincia as province, indicativo as station_code, nombre as station_name
	from aemet.station s 
	where provincia_id in (4, 11, 14, 18, 21, 23, 29, 41)
	order by province, station_name;`

	fmt.Println(stationsQuery)
	res, err := conn.db.Query(stationsQuery)

	if err != nil {
		log.Fatal(err)
	}

	var stations []ResultAemetStation
	for res.Next() {

		var resStation ResultAemetStation
		err := res.Scan(&resStation.ProvCode, &resStation.Province,
			&resStation.StationCode, &resStation.StationName)
		if err != nil {
			log.Fatal(err)
		}
		stations = append(stations, resStation)
	}
	conn.Close()
	return stations
}
