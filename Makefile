MAIN_PATH=cmd/main.go
BINARY_PATH=bin
BINARY_CLIENT_NAME=$(BINARY_PATH)/meteo

client-run:
	@echo "Compilando el programa..."
	@go build -o $(BINARY_CLIENT_NAME) $(MAIN_PATH)
	@echo "Ejecutando el programa..."
	@./$(BINARY_CLIENT_NAME)

clean:
	@echo "Limpiando el proyecto..."
	@go clean $(MAIN_PATH)
	@rm -f $(BINARY_PATH)/*
	@echo "Proyecto limpio."


