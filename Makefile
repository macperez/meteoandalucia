MAIN_RIAWEB_PATH=cmd/riaweb/main.go
MAIN_AEMET_PATH=cmd/aemet/main.go
BINARY_PATH=bin
BINARY_RIAWEB_CLIENT_NAME=$(BINARY_PATH)/meteoandalucia
BINARY_AEMET_CLIENT_NAME=$(BINARY_PATH)/aemet

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


compile-riaweb:
	@echo "Building riaweb client..."
	@go build -o $(BINARY_RIAWEB_CLIENT_NAME) $(MAIN_RIAWEB_PATH)
	@echo "Compilation done! . See bin folder "

compile-aemet:
	@echo "Building AEMET client..."
	@go build -o $(BINARY_AEMET_CLIENT_NAME) $(MAIN_AEMET_PATH)
	@echo "Compilation done! . See bin folder "