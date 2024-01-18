package main

import (
	"fmt"
	"strings"

	"github.com/macperez/meteoandalucia/internal/apirest"
	"github.com/macperez/meteoandalucia/internal/posg"
	"github.com/spf13/cobra"
)

func main() {
	var insert bool
	var rootCmd = &cobra.Command{Use: "meteo"}

	var getMeasurementsCmd = &cobra.Command{
		Use:   "get-measurements",
		Short: "Get measurements",
		Run: func(cmd *cobra.Command, args []string) {
			from, _ := cmd.Flags().GetString("from")
			to, _ := cmd.Flags().GetString("to")
			to = strings.Trim(to, " ")
			from = strings.Trim(from, " ")
			province, _ := cmd.Flags().GetInt("province")
			station, _ := cmd.Flags().GetInt("station")
			fmt.Printf("Province = %d, station = %d, %s, %s\n", province, station, from, to)

			if to == "" {
				apirest.GetMeasurement(province, station, from, true, insert)
			} else {
				apirest.GetMeasurements(province, station, from, to, true, insert)
			}
			//apirest.GetMeasurement(4, 1, "2023-01-16", true, false)
			//apirest.GetMeasurements()
		},
	}

	var fromDate string
	var toDate string
	var provincia int
	var station int

	getMeasurementsCmd.Flags().StringVarP(&fromDate, "from", "f", " ", "Date for which to get the time (format: yyyy-mm-dd)")
	getMeasurementsCmd.Flags().StringVarP(&toDate, "to", "t", " ", "Date for which to get the time (format: yyyy-mm-dd)")
	getMeasurementsCmd.Flags().IntVarP(&provincia, "province", "p", 4, "Province code")
	getMeasurementsCmd.Flags().IntVarP(&station, "station", "s", 41, "Station code")
	getMeasurementsCmd.MarkFlagRequired("from")
	getMeasurementsCmd.MarkFlagRequired("province")
	getMeasurementsCmd.MarkFlagRequired("station")

	var getStationsCmd = &cobra.Command{
		Use:   "get-stations",
		Short: "Get stations",
		Args:  cobra.ExactArgs(0),
		Run: func(cmd *cobra.Command, args []string) {
			fmt.Println("Getting stations...")
			if !insert {
				posg.GetStations()
			} else {
				apirest.GetStations(insert)
			}

		},
	}
	rootCmd.PersistentFlags().BoolVar(&insert, "insert", false, "Insert into database")
	rootCmd.AddCommand(getMeasurementsCmd, getStationsCmd)
	if err := rootCmd.Execute(); err != nil {
		fmt.Println(err)
	}
}
