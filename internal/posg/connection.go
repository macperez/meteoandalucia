package posg

import (
	"database/sql"
	"fmt"
	"log"
	"os"

	_ "github.com/joho/godotenv/autoload"
)

var (
	host     = os.Getenv("DATABASE_HOST")
	port     = os.Getenv("DATABASE_PORT")
	user     = os.Getenv("DATABASE_USER")
	password = os.Getenv("DATABASE_PASSWORD")
	dbname   = os.Getenv("DATABASE_NAME")
)

type DBConnection struct {
	db     *sql.DB
	isOpen bool
}

func New() (*DBConnection, error) {
	connStr := fmt.Sprintf("host=%s port=%s user=%s password=%s dbname=%s sslmode=disable",
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
}
