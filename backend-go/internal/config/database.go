package config

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"

	"gorm.io/driver/mysql"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
)

// ConnectDatabase opens a GORM connection using existing project config.
func ConnectDatabase() (*gorm.DB, error) {
	dialect := strings.ToLower(strings.TrimSpace(os.Getenv("DB_DIALECT")))
	if dialect == "" {
		dialect = "sqlite"
	}

	switch dialect {
	case "mysql":
		return connectMySQL()
	default:
		return connectSQLite()
	}
}

func connectSQLite() (*gorm.DB, error) {
	path := strings.TrimSpace(os.Getenv("DB_SQLITE_PATH"))
	if path == "" {
		path = filepath.Join(projectRoot(), "data", "kline.db")
	}
	return gorm.Open(sqlite.Open(path), &gorm.Config{})
}

func connectMySQL() (*gorm.DB, error) {
	host := getEnv("DB_HOST", "localhost")
	port := getEnv("DB_PORT", "3306")
	user := getEnv("DB_USER", "root")
	password := os.Getenv("DB_PASSWORD")
	name := getEnv("DB_NAME", "")
	params := getEnv("DB_PARAMS", "charset=utf8mb4&parseTime=True&loc=Local")

	dsn := fmt.Sprintf("%s:%s@tcp(%s:%s)/%s?%s", user, password, host, port, name, params)
	return gorm.Open(mysql.Open(dsn), &gorm.Config{})
}

func getEnv(key, fallback string) string {
	value := strings.TrimSpace(os.Getenv(key))
	if value == "" {
		return fallback
	}
	return value
}

func projectRoot() string {
	workingDir, err := os.Getwd()
	if err != nil {
		return "."
	}
	if filepath.Base(workingDir) == "backend-go" {
		return filepath.Dir(workingDir)
	}
	return workingDir
}
