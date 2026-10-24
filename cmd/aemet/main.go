package main

import (
	"context"
	"fmt"
	"os"
	"path/filepath"
	"sort"
	"strings"
	"text/tabwriter"
	"time"

	"github.com/joho/godotenv"
	"github.com/spf13/cobra"
)

func main() {
	if err := newRootCommand().Execute(); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}

func newRootCommand() *cobra.Command {
	var list, exportCSV bool
	cmd := &cobra.Command{
		Use:           "aemet [--list] [--csv]",
		Short:         "Consulta el inventario de estaciones de AEMET",
		SilenceUsage:  true,
		SilenceErrors: true,
		Args:          cobra.NoArgs,
		RunE: func(cmd *cobra.Command, args []string) error {
			if !list && !exportCSV {
				return cmd.Help()
			}
			if err := godotenv.Load(); err != nil && !os.IsNotExist(err) {
				return fmt.Errorf("leer .env: %w", err)
			}
			key := strings.TrimSpace(os.Getenv("API_KEY"))
			if key == "" {
				return fmt.Errorf("falta API_KEY: añade tu token de AEMET al archivo .env (API_KEY=tu_token)")
			}
			ctx, cancel := context.WithTimeout(cmd.Context(), 60*time.Second)
			defer cancel()
			stations, err := newAemetClient(key).stations(ctx)
			if err != nil {
				return err
			}
			sort.Slice(stations, func(i, j int) bool {
				if stations[i].Province != stations[j].Province {
					return stations[i].Province < stations[j].Province
				}
				return stations[i].Code < stations[j].Code
			})
			if exportCSV {
				executable, err := os.Executable()
				if err != nil {
					return fmt.Errorf("localizar ejecutable: %w", err)
				}
				path := filepath.Join(filepath.Dir(executable), "estaciones.csv")
				if err := exportStationsCSV(path, stations); err != nil {
					return err
				}
				if _, err := fmt.Fprintf(cmd.OutOrStdout(), "CSV exportado correctamente (%d estaciones): %s\n", len(stations), path); err != nil {
					return err
				}
			}
			if !list {
				return nil
			}
			out := tabwriter.NewWriter(cmd.OutOrStdout(), 0, 4, 2, ' ', 0)
			if _, err := fmt.Fprintln(out, "CÓDIGO\tPROVINCIA\tESTACIÓN\tALTITUD (m)\tLATITUD\tLONGITUD\tIND. SINÓPTICO"); err != nil {
				return err
			}
			for _, station := range stations {
				if _, err := fmt.Fprintf(out, "%s\t%s\t%s\t%s\t%s\t%s\t%s\n", station.Code, station.Province, station.Name, station.Altitude, station.Latitude, station.Longitude, station.SynopticCode); err != nil {
					return err
				}
			}
			return out.Flush()
		},
	}
	cmd.CompletionOptions.DisableDefaultCmd = true
	cmd.Flags().BoolVar(&list, "list", false, "Lista todas las estaciones del inventario de AEMET")
	cmd.Flags().BoolVar(&exportCSV, "csv", false, "Exporta estaciones.csv en la carpeta del ejecutable")
	return cmd
}
