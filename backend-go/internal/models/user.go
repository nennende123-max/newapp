package models

// User maps to the "users" table referenced by the API auth flow.
// Fields mirror the Python user shape: id, address, role.
type User struct {
	ID      int64  `gorm:"column:id;primaryKey;autoIncrement"`
	Address string `gorm:"column:address;type:text"`
	Role    string `gorm:"column:role;type:text"`
}

func (User) TableName() string {
	return "users"
}
