package posg

import (
	"strings"
	"testing"
)

func TestReadAemetStationsCSV(t *testing.T) {
	header := "indicativo,nombre,provincia,altitud,latitud,longitud,indsinop\n"
	rows, err := readAemetStationsCSV(strings.NewReader("\ufeff" + header + "0010,\"MÁLAGA, AEROPUERTO\",MALAGA,7,364000N,042900W,08482\n0011,OTRA,MALAGA,-2,364000N,042900W,\n"))
	if err != nil {
		t.Fatal(err)
	}
	if len(rows) != 2 || rows[0].code != "0010" || rows[0].name != "MÁLAGA, AEROPUERTO" || rows[0].synoptic.String != "08482" || !rows[0].synoptic.Valid || rows[1].synoptic.Valid || rows[1].altitude != -2 {
		t.Fatalf("datos alterados: %+v", rows)
	}
	for _, body := range []string{
		"", "nombre,indicativo\n",
		header + "x,n,p,no,364000N,042900W,\n",
		header + "x,n,p,1\n",
		header + ",n,p,1,364000N,042900W,\n",
		header + "x,n,p,1,364000N,042900W,\nx,n,p,1,364000N,042900W,\n",
	} {
		if _, err := readAemetStationsCSV(strings.NewReader(body)); err == nil {
			t.Errorf("se esperaba error para %q", body)
		}
	}
}
