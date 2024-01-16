package main

import "github.com/macperez/meteoandalucia/internal/apirest"

func main() {
	apirest.GetMeasurement(4, 1, "2023-01-16", true, false)
}
