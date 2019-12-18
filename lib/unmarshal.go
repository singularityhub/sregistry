package main

import "C"

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
)

// BuildRequest contains the info necessary for submitting a build to build service
type BuildRequest struct {
	//	LibraryRef          string            `json:"libraryRef"`
	//	LibraryURL          string            `json:"libraryURL"`
	//	CallbackURL         string            `json:"callbackURL"`
	DefinitionRaw []byte `json:"definitionRaw"`
	//	BuilderRequirements map[string]string `json:"builderRequirements"`
}

//export Unmarshal
func Unmarshal(definitionRaw string, name string) int {

	var br BuildRequest

	buildrequest := fmt.Sprintf("{\"definitionRaw\":\"%s\"}", definitionRaw)
	//fmt.Printf("buildrequest %s\n", buildrequest)
	json.Unmarshal([]byte(buildrequest), &br)
	//	fmt.Printf("BuildRequest: %s\n", br.DefinitionRaw)
	//return string(br.DefinitionRaw)
	err := ioutil.WriteFile(name, br.DefinitionRaw, 0644)
	if err != nil {
		return 1
	}
	return 0
}

func main() {}

//func main() {
//	definitionRaw := "CkJvb3RTdHJhcDogZGVib290c3RyYXAKT1NWZXJzaW9uOiBzdHJldGNoCk1pcnJvclVSTDogaHR0cDovL2Z0cC5kZWJpYW4ub3JnL2RlYmlhbgpJbmNsdWRlOiBpbmV0dXRpbHMtcGluZyxpcHJvdXRlLGJhc2gK"
//
//	fmt.Printf("BuildRequest: %s\n", Unmarshal(definitionRaw, "/tmp/Singularity"))
//}
