package main

import (
	"fmt"
	"io"
	"net/http"
	"strings"

	"github.com/macperez/meteoandalucia/internal/apirest"
	"github.com/macperez/meteoandalucia/internal/posg"
	"github.com/spf13/cobra"
)

func Main1() {

	apikey := "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJtYW51ZWwuYW50LmNhc3Ryb0BnbWFpbC5jb20iLCJqdGkiOiIyYzkwMzMyMi1hZmJiLTRmZDAtYjRhMS1mZDRiY2M3Yjk0ZmQiLCJpc3MiOiJBRU1FVCIsImlhdCI6MTcwNjQ1NzQ4NCwidXNlcklkIjoiMmM5MDMzMjItYWZiYi00ZmQwLWI0YTEtZmQ0YmNjN2I5NGZkIiwicm9sZSI6IiJ9.BWMQJc9_ZpJ9OeBRO29UhL95Wp8zPLQ2PN6r3uuYa4E"
	url := "https://opendata.aemet.es/opendata/api/valores/climatologicos/inventarioestaciones/todasestaciones/?api_key=" + apikey

	req, _ := http.NewRequest("GET", url, nil)

	req.Header.Add("cache-control", "no-cache")
	res, _ := http.DefaultClient.Do(req)

	defer res.Body.Close()
	body, _ := io.ReadAll(res.Body)

	fmt.Println(res)
	fmt.Println(string(body))

}

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
			apirest.GetMeasurementsAll(from, to, insert)

		},
	}
	getMeasurementsAllStationsCmd.Flags().StringVarP(&fromDate, "from", "f", " ", "Date for which to get the time (format: yyyy-mm-dd)")
	getMeasurementsAllStationsCmd.Flags().StringVarP(&toDate, "to", "t", " ", "Date for which to get the time (format: yyyy-mm-dd)")
	getMeasurementsAllStationsCmd.MarkFlagRequired("from")
	getMeasurementsAllStationsCmd.MarkFlagRequired("to")
	rootCmd.PersistentFlags().BoolVar(&insert, "insert", false, "Insert into database")
	rootCmd.AddCommand(getMeasurementsAllStationsCmd, getStationsCmd)
	if err := rootCmd.Execute(); err != nil {
		fmt.Println(err)
	}

}
