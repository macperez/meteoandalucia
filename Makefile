.DEFAULT_GOAL := build

MAIN_RIAWEB_PATH=./cmd/riaweb
MAIN_AEMET_PATH=./cmd/aemet
BINARY_PATH=bin
EXEEXT=$(shell go env GOEXE)
BINARY_RIAWEB_CLIENT_NAME=$(BINARY_PATH)/meteoandalucia$(EXEEXT)
BINARY_AEMET_CLIENT_NAME=$(BINARY_PATH)/aemet$(EXEEXT)

.PHONY: build client-run clean compile-riaweb compile-aemet

build: compile-aemet

client-run: compile-aemet
	@$(BINARY_AEMET_CLIENT_NAME) $(ARGS)

clean:
	@echo "Limpiando el proyecto..."
	@go clean ./cmd/aemet ./cmd/riaweb
	@rm -f $(BINARY_PATH)/*
	@echo "Proyecto limpio."


compile-riaweb:
	@echo "Building riaweb client..."
	@go build -o $(BINARY_RIAWEB_CLIENT_NAME) $(MAIN_RIAWEB_PATH)
	@echo "Binary: $(BINARY_RIAWEB_CLIENT_NAME)"

compile-aemet:
	@echo "Building AEMET client..."
	@go build -o $(BINARY_AEMET_CLIENT_NAME) $(MAIN_AEMET_PATH)
	@echo "Binary: $(BINARY_AEMET_CLIENT_NAME)"
