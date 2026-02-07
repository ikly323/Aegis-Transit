curl -X POST --verbose "http://127.0.0.1:6862/transactions/signAndBroadcast" \
  -H "Content-Type: application/json" \
  -H "X-Contract-Api-Token: we" \
  -d '
{
  	"contractId": "",
	"fee": 10,
	"sender": "3Np2P4vuMEAAC9uZpgDxiGi1nTCkyGPLxVZ",
	"password": "3aStpvcKO8AUWQnPYrtWKg",
	"type": 104,
	"params": [],
	"version": 2,
	"contractVersion": 1
}' 

	
