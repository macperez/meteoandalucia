package posg

import (
	"database/sql"
	"fmt"
	"strconv"
	"strings"
	"time"
)

func ParseAemetMeasurement(measurement *MeasurementAemet) error {

	date, err := time.Parse("2006-01-02", measurement.Fecha)
	if err != nil {
		return err
	}
	measurement.Date = date

	if err := str2NullFloat64(&measurement.AltitudeStr, &measurement.Altitude); err != nil {
		fmt.Println(err)
		return err
	}

	if err := str2NullFloat64(&measurement.AvgTempStr, &measurement.AvgTemp); err != nil {
		fmt.Println(err)
		return err
	}

	if err := str2NullFloat64(&measurement.PrecStr, &measurement.Prec); err != nil {
		fmt.Println(err)
		return err
	}

	if err := str2NullFloat64(&measurement.MinTempStr, &measurement.MinTemp); err != nil {
		fmt.Println(err)
		return err
	}

	if err := str2NullFloat64(&measurement.MaxTempStr, &measurement.MaxTemp); err != nil {
		fmt.Println(err)
		return err
	}

	if err := str2NullFloat64(&measurement.AvgVelStr, &measurement.AvgVel); err != nil {
		fmt.Println(err)
		return err
	}

	if err := str2NullFloat64(&measurement.MaxVelStr, &measurement.MaxVel); err != nil {
		fmt.Println(err)
		return err
	}

	if err := str2NullFloat64(&measurement.MaxPressureStr, &measurement.MaxPressure); err != nil {
		fmt.Println(err)
		return err
	}

	if err := str2NullFloat64(&measurement.MinPressureStr, &measurement.MinPressure); err != nil {
		fmt.Println(err)
		return err
	}

	if err := str2NullFloat64(&measurement.DirectionStr, &measurement.Direction); err != nil {
		fmt.Println(err)
		return err
	}
	return nil
}

func str2NullFloat64(str *string, result *sql.NullFloat64) error {

	if *str != "" {
		*str = strings.Replace(*str, ",", ".", -1)
		value, err := strconv.ParseFloat(*str, 32)
		if err != nil {

			*result = sql.NullFloat64{Float64: value, Valid: false}
		}
		*result = sql.NullFloat64{Float64: value, Valid: true}

	}
	return nil
}
