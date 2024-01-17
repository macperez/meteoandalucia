package posg

import (
	"database/sql"
	"fmt"
	"log"
)

const (
	host     = "172.17.0.2"
	port     = 5432
	user     = "postgres"
	password = "admin"
	dbname   = "postgres"
)

type DBConnection struct {
	db     *sql.DB
	isOpen bool
}

func New() (*DBConnection, error) {
	connStr := fmt.Sprintf("host=%s port=%d user=%s password=%s dbname=%s sslmode=disable",
		host, port, user, password, dbname)

	var err error
	db, err := sql.Open("postgres", connStr)
	if err != nil {
		log.Fatal(err)
	}

	return &DBConnection{
		db:     db,
		isOpen: true,
	}, nil
}

func (conn *DBConnection) Ping() bool {
	err := conn.db.Ping()
	if err != nil {
		log.Fatal(err)
		return false
	}
	return true
}

func (conn *DBConnection) Close() {
	if conn.isOpen {
		conn.db.Close()
		conn.isOpen = false
	}
	fmt.Println("Connection close")
}
