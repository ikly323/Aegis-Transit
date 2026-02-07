curl -X POST --verbose "http://127.0.0.1:6862/transactions/signAndBroadcast" \
  -H "Content-Type: application/json" \
  -H "X-Contract-Api-Token: we" \
  -d '
{
    "sender": "3Np2P4vuMEAAC9uZpgDxiGi1nTCkyGPLxVZ",
    "password": "3aStpvcKO8AUWQnPYrtWKg",
    "contractId": "",
    "fee": 789654,
    "type": 106,
    "version": 2
}' 
