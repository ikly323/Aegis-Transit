curl -X POST --verbose "http://127.0.0.1:6862/transactions/signAndBroadcast" \
  -H "Content-Type: application/json" \
  -H "X-Contract-Api-Token: we" \
  -d '
{
	"image" : "localhost:5000/SampleContract:latest",
	"sender" : "3Np2P4vuMEAAC9uZpgDxiGi1nTCkyGPLxVZ",
	"password": "3aStpvcKO8AUWQnPYrtWKg",
	"fee" : 789654,
	"contractId" : "",
	"imageHash" : "",
	"type" : 107,
	"version" : 2
}'
