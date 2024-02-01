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
	var rootCmd = &cobra.Command{Use: "aemet"}

	var fromDate string
	var toDate string

	var getStationsCmd = &cobra.Command{
		Use:   "get-stations",
		Short: "Get stations",
		Args:  cobra.ExactArgs(0),
		Run: func(cmd *cobra.Command, args []string) {
			fmt.Println("Getting stations from AEMET...")
			if !insert {
				stations := posg.GetAemetStations()
				for _, st := range stations {
					fmt.Printf("ProvId = %d; prov = %s; stationId = %s; station = %s\n", st.ProvCode, st.Province, st.StationCode,
						st.StationName)
				}

			}

		},
	}

	var getMeasurementsAllStationsCmd = &cobra.Command{
		Use:   "get-measurements-all",
		Short: "Get measurements of all stations",
		Run: func(cmd *cobra.Command, args []string) {
			from, _ := cmd.Flags().GetString("from")
			to, _ := cmd.Flags().GetString("to")
			to = strings.Trim(to, " ")
			from = strings.Trim(from, " ")
			apirest.GetMeasurementsAllAemet(from, to, insert)

		},
	}
	getMeasurementsAllStationsCmd.Flags().StringVarP(&fromDate, "from", "f", " ", "Date for which to get the time (format: yyyy-mm-dd)")
	getMeasurementsAllStationsCmd.Flags().StringVarP(&toDate, "to", "t", " ", "Date for which to get the time (format: yyyy-mm-dd)")
	getMeasurementsAllStationsCmd.MarkFlagRequired("from")
	getMeasurementsAllStationsCmd.MarkFlagRequired("to")

	var getMeasurementStationCmd = &cobra.Command{
		Use:   "get-measurements",
		Short: "Get measurements of given station",
		Run: func(cmd *cobra.Command, args []string) {
			from, _ := cmd.Flags().GetString("from")
			to, _ := cmd.Flags().GetString("to")
			to = strings.Trim(to, " ")
			from = strings.Trim(from, " ")
			station, _ := cmd.Flags().GetString("station")
			station = strings.Trim(station, " ")
			err := apirest.GetAemetMeasurements(station, from, to, insert)
			if err != nil {
				fmt.Println(err)
			}

		},
	}
	var station string
	getMeasurementStationCmd.Flags().StringVarP(&fromDate, "from", "f", " ", "Date for which to get the time (format: yyyy-mm-dd)")
	getMeasurementStationCmd.Flags().StringVarP(&toDate, "to", "t", " ", "Date for which to get the time (format: yyyy-mm-dd)")
	getMeasurementStationCmd.Flags().StringVarP(&station, "station", "s", " ", "Code for the station")
	getMeasurementStationCmd.MarkFlagRequired("from")
	getMeasurementStationCmd.MarkFlagRequired("to")
	getMeasurementStationCmd.MarkFlagRequired("station")

	rootCmd.PersistentFlags().BoolVar(&insert, "insert", false, "Insert into database")
	rootCmd.AddCommand(getMeasurementsAllStationsCmd, getMeasurementStationCmd, getStationsCmd)
	rootCmd.CompletionOptions.DisableDefaultCmd = true

	if err := rootCmd.Execute(); err != nil {
		fmt.Println(err)
	}

}
