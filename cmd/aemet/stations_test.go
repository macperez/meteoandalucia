package main

import (
	"context"
	"fmt"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
)

func TestStations(t *testing.T) {
	var server *httptest.Server
	server = httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		switch r.URL.Path {
		case "/inventory":
			if r.Header.Get("api_key") != "test-token" {
				t.Error("falta cabecera api_key")
			}
			fmt.Fprintf(w, `{"estado":200,"datos":%q}`, server.URL+"/data")
		case "/data":
			if r.Header.Get("api_key") != "" {
				t.Error("el token no debe enviarse al enlace de descarga")
			}
			fmt.Fprint(w, `[{"indicativo":"5783","nombre":"CÓRDOBA","provincia":"CORDOBA","altitud":"90","latitud":"375056N","longitud":"045050W","indsinop":"08410"}]`)
		default:
			http.NotFound(w, r)
		}
	}))
	defer server.Close()
	client := newAemetClient("test-token")
	client.http = server.Client()
	client.inventoryURL = server.URL + "/inventory"
	stations, err := client.stations(context.Background())
	if err != nil {
		t.Fatal(err)
	}
	if len(stations) != 1 || stations[0].Code != "5783" || stations[0].Name != "CÓRDOBA" {
		t.Fatalf("inventario inesperado: %+v", stations)
	}
}

func TestJSONEncoding(t *testing.T) {
	for _, tc := range []struct{ name, body string }{
		{"UTF-8", `{"nombre":"C\u00d3RDOBA, MÁLAGA, PEÑA"}`},
		{"ISO-8859-1", "{\"nombre\":\"C\xd3RDOBA, M\xc1LAGA, PE\xd1A\"}"},
	} {
		t.Run(tc.name, func(t *testing.T) {
			server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				w.Header().Set("Content-Type", "application/json")
				fmt.Fprint(w, tc.body)
			}))
			defer server.Close()
			client := newAemetClient("")
			client.http = server.Client()
			var result station
			if err := client.getJSON(context.Background(), server.URL, false, &result); err != nil {
				t.Fatal(err)
			}
			if result.Name != "CÓRDOBA, MÁLAGA, PEÑA" {
				t.Fatalf("texto alterado: %q", result.Name)
			}
		})
	}
}

func TestStationsErrors(t *testing.T) {
	for _, tc := range []struct {
		name       string
		status     int
		body, want string
	}{
		{"HTTP", 401, "", "HTTP 401"},
		{"estado AEMET", 200, `{"estado":429,"descripcion":"Límite de peticiones"}`, "estado 429"},
		{"JSON", 200, `no es JSON`, "JSON inválida"},
		{"enlace ausente", 200, `{"estado":200}`, "enlace de datos válido"},
	} {
		t.Run(tc.name, func(t *testing.T) {
			server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				w.WriteHeader(tc.status)
				fmt.Fprint(w, tc.body)
			}))
			defer server.Close()
			client := newAemetClient("test-token")
			client.http = server.Client()
			client.inventoryURL = server.URL
			_, err := client.stations(context.Background())
			if err == nil || !strings.Contains(err.Error(), tc.want) {
				t.Fatalf("error esperado %q; recibido %v", tc.want, err)
			}
		})
	}
}
