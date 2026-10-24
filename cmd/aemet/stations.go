package main

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"time"
	"unicode/utf8"
)

const stationsURL = "https://opendata.aemet.es/opendata/api/valores/climatologicos/inventarioestaciones/todasestaciones"

type station struct {
	Code         string `json:"indicativo"`
	Name         string `json:"nombre"`
	Province     string `json:"provincia"`
	Altitude     string `json:"altitud"`
	Latitude     string `json:"latitud"`
	Longitude    string `json:"longitud"`
	SynopticCode string `json:"indsinop"`
}

type aemetClient struct {
	http         *http.Client
	key          string
	inventoryURL string
}

func newAemetClient(key string) *aemetClient {
	return &aemetClient{http: &http.Client{Timeout: 30 * time.Second}, key: key, inventoryURL: stationsURL}
}

func (c *aemetClient) stations(ctx context.Context) ([]station, error) {
	var envelope struct {
		Status      int    `json:"estado"`
		Description string `json:"descripcion"`
		Data        string `json:"datos"`
	}
	if err := c.getJSON(ctx, c.inventoryURL, true, &envelope); err != nil {
		return nil, fmt.Errorf("consultar inventario de AEMET: %w", err)
	}
	if envelope.Status != http.StatusOK {
		return nil, fmt.Errorf("AEMET devolvió estado %d: %s", envelope.Status, envelope.Description)
	}
	dataURL, err := url.Parse(envelope.Data)
	if err != nil || dataURL.Host == "" || (dataURL.Scheme != "https" && dataURL.Scheme != "http") {
		return nil, fmt.Errorf("AEMET no devolvió un enlace de datos válido")
	}
	var stations []station
	if err := c.getJSON(ctx, dataURL.String(), false, &stations); err != nil {
		return nil, fmt.Errorf("descargar estaciones de AEMET: %w", err)
	}
	return stations, nil
}

func (c *aemetClient) getJSON(ctx context.Context, endpoint string, authenticated bool, target interface{}) error {
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, endpoint, nil)
	if err != nil {
		return fmt.Errorf("crear petición: %w", err)
	}
	if authenticated {
		req.Header.Set("api_key", c.key)
	}
	resp, err := c.http.Do(req)
	if err != nil {
		return fmt.Errorf("no se pudo completar la petición HTTP")
	}
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("HTTP %d (%s)", resp.StatusCode, http.StatusText(resp.StatusCode))
	}
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return fmt.Errorf("leer respuesta HTTP: %w", err)
	}
	// El inventario de AEMET puede contener texto ISO-8859-1. El decoder
	// JSON espera UTF-8 y sustituye los bytes inválidos por U+FFFD.
	if !utf8.Valid(body) {
		characters := make([]rune, len(body))
		for i, b := range body {
			characters[i] = rune(b)
		}
		body = []byte(string(characters))
	}
	if err := json.NewDecoder(bytes.NewReader(body)).Decode(target); err != nil {
		return fmt.Errorf("respuesta JSON inválida: %w", err)
	}
	return nil
}
