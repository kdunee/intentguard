package domain

import "encoding/json"

type CodeObject struct {
	Name string
	Code string
}

func (p CodeObject) MarshalJSON() ([]byte, error) {
	return json.Marshal(map[string]interface{}{
		"name": p.Name,
		"code": p.Code,
	})
}
