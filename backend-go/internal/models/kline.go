package models

// Kline maps to the existing SQLite "klines" table.
// Schema source: app/models/kline.py and KLINE_SERVICE.md.
type Kline struct {
	Symbol    string  `gorm:"column:symbol;type:text;primaryKey"`
	Interval  string  `gorm:"column:interval;type:text;primaryKey"`
	Timestamp int64   `gorm:"column:timestamp;type:integer;primaryKey"`
	Open      float64 `gorm:"column:open;type:real;not null"`
	High      float64 `gorm:"column:high;type:real;not null"`
	Low       float64 `gorm:"column:low;type:real;not null"`
	Close     float64 `gorm:"column:close;type:real;not null"`
	Volume    float64 `gorm:"column:volume;type:real;not null"`
}

func (Kline) TableName() string {
	return "klines"
}
