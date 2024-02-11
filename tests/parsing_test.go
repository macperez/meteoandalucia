package tests

import (
	"database/sql"
	"fmt"
	"math"
	"reflect"
	"testing"
	"time"

	"github.com/macperez/meteoandalucia/internal/posg"
)

func TestParse(t *testing.T) {

	measurement := posg.MeasurementAemet{
		Fecha:       "2023-01-15",
		Id:          "ID123",
		Name:        "Estación A",
		Province:    "Provincia A",
		AltitudeStr: "123.45",

		AvgTempStr: "25.5",

		PrecStr: "10.2",

		MinTempStr: "18.7",

		TMinTime:   "08:30",
		MaxTempStr: "30.2",

		TMaxTime:     "15:45",
		DirectionStr: "180.0",

		AvgVelStr: "5.3",

		MaxVelStr: "12.8",

		MaxVelTime:     "18:20",
		MaxPressureStr: "1012.5",

		MaxPressureTime: "10:00",
		MinPressureStr:  "1008.2",

		MinPressureTime: "03:30",
	}

	err := posg.ParseAemetMeasurement(&measurement)
	if err != nil {
		fmt.Printf("error: %v\n", err)
	}
	dateNow, _ := time.Parse("2006-01-02", "2023-01-15")
	expected := posg.MeasurementAemet{
		Date:            dateNow,
		Fecha:           "2023-01-15",
		Id:              "ID123",
		Name:            "Estación A",
		Province:        "Provincia A",
		AltitudeStr:     "123.45",
		Altitude:        sql.NullFloat64{Float64: 123.45, Valid: true},
		AvgTempStr:      "25.5",
		AvgTemp:         sql.NullFloat64{Float64: 25.5, Valid: true},
		PrecStr:         "10.2",
		Prec:            sql.NullFloat64{Float64: 10.2, Valid: true},
		MinTempStr:      "18.7",
		MinTemp:         sql.NullFloat64{Float64: 18.7, Valid: true},
		TMinTime:        "08:30",
		MaxTempStr:      "30.2",
		MaxTemp:         sql.NullFloat64{Float64: 30.2, Valid: true},
		TMaxTime:        "15:45",
		DirectionStr:    "180.0",
		Direction:       sql.NullFloat64{Float64: 180.0, Valid: true},
		AvgVelStr:       "5.3",
		AvgVel:          sql.NullFloat64{Float64: 5.3, Valid: true},
		MaxVelStr:       "12.8",
		MaxVel:          sql.NullFloat64{Float64: 12.8, Valid: true},
		MaxVelTime:      "18:20",
		MaxPressureStr:  "1012.5",
		MaxPressure:     sql.NullFloat64{Float64: 1012.5, Valid: true},
		MaxPressureTime: "10:00",
		MinPressureStr:  "1008.2",
		MinPressure:     sql.NullFloat64{Float64: 1008.2, Valid: true},
		MinPressureTime: "03:30",
	}
	if !compareFloatTolerance(measurement, expected, 0.001) {
		t.Errorf(" %+v\n; se esperaba %+v\n", measurement, expected)
	}

}
func compareFloatTolerance(m1, m2 posg.MeasurementAemet, allowance float64) bool {
	measureAemetValues := reflect.ValueOf(m1)
	measureAemetExpected := reflect.ValueOf(m2)
	measureAemetType := reflect.TypeOf(m1)
	same := true
	for i := 0; i < measureAemetType.NumField(); i++ {
		fieldToTest := measureAemetType.Field(i)
		if fieldToTest.Type == reflect.TypeOf(sql.NullFloat64{}) {
			valFloat := measureAemetValues.Field(i).Interface().(sql.NullFloat64).Float64
			expFloat := measureAemetExpected.Field(i).Interface().(sql.NullFloat64).Float64
			same = same && (math.Abs(valFloat-expFloat) < allowance)

		} else {
			same = same && measureAemetValues.Field(i).Interface() == measureAemetExpected.Field(i).Interface()
		}

	}
	return same
}
