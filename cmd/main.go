package main

import (
	"fmt"

	"github.com/macperez/meteoandalucia/internal/apirest"
	"github.com/spf13/cobra"
)

//apirest.GetMeasurement(4, 1, "2023-01-16", true, false)

func main() {
	var insert bool
	var rootCmd = &cobra.Command{Use: "meteo"}

	var getMeasurementsCmd = &cobra.Command{
		Use:   "get-measurements",
		Short: "Get measurements",
		Run: func(cmd *cobra.Command, args []string) {
			from, _ := cmd.Flags().GetString("from")
			to, _ := cmd.Flags().GetString("to")
			fmt.Printf("Args: %v\n", args)

			fmt.Println("Getting measurements...")
			fmt.Println("From:", from)
			fmt.Println("To:", to)
			fmt.Println("Insert:", insert)
			// Puedes agregar la lógica para insertar en la base de datos aquí si es necesario.
			apirest.GetMeasurement(4, 1, "2023-01-16", true, false)
		},
	}

	var fromDate string
	var toDate string

	getMeasurementsCmd.Flags().StringVarP(&fromDate, "from", "f", " ", "Date for which to get the time (format: yyyy-mm-dd)")
	getMeasurementsCmd.Flags().StringVarP(&toDate, "to", "t", " ", "Date for which to get the time (format: yyyy-mm-dd)")

	//getMeasurementsCmd.Flags().VarP(&fromDate, "from", "", "Specify the start date (format: yyyy-mm-dd)")
	//g //etMeasurementsCmd.Flags().VarP(&toDate, "to", "", "Specify the end date (format: yyyy-mm-dd)")
	getMeasurementsCmd.MarkFlagRequired("from")
	getMeasurementsCmd.MarkFlagRequired("to")

	var getStationsCmd = &cobra.Command{
		Use:   "get-stations",
		Short: "Get stations",
		Args:  cobra.ExactArgs(0),
		Run: func(cmd *cobra.Command, args []string) {
			fmt.Println("Getting stations...")
			fmt.Println("Insert:", insert)
			// Puedes agregar la lógica para insertar en la base de datos aquí si es necesario.
		},
	}

	/*
		var rootInsertCmd = &cobra.Command{
			Use:   "--insert",
			Short: "Insert into database",
			Args:  cobra.ExactArgs(0),
			Run: func(cmd *cobra.Command, args []string) {
				fmt.Println("Inserting into database...")
			},
		}

		rootCmd.PersistentFlags().BoolVar(&insert, "insert", false, "Insert into database")
	*/
	//rootCmd.AddCommand(getMeasurementsCmd, getStationsCmd, rootInse)
	rootCmd.AddCommand(getMeasurementsCmd, getStationsCmd)
	if err := rootCmd.Execute(); err != nil {
		fmt.Println(err)
	}
}
