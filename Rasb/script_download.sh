#!/bin/bash
CONTRACT_ID=$(curl -X GET "http://localhost:6872/contracts" -H  "accept: application/json" -H  "X-API-Key: we" | grep -m 1 "contractId" | cut -d ':' -f 2 | cut -d '"' -f 2)


curl -X POST "http://localhost:6872/contracts" -H  "accept: application/json" -H  "Content-Type: application/json" -H  "X-API-Key: we" -d "{  \"contracts\": [    \"$CONTRACT_ID\"  ]}" | python3 Rasb_serv.py


echo "The server has stopped working, the cargo integrity has been changed in the contract " # in case of an error, contract change 104 is sent (this is stub)

rm FLAG_FILE.txt

#curl -X POST --verbose "http://127.0.0.1:6872/transactions/signAndBroadcast" \
#  -H "Content-Type: application/json" \
#  -H "X-Contract-Api-Token: we" \
#  -d '
#{
#  	"contractId": "$CONTRACT_ID",
#	"fee": 10,
#	"sender": "3NxjAYw9iAPqkLDHW3riveDRXwgk9zZGQ2w",
#	"password": "ZMI6WLqiCexFneMbcCdKoA",
#	"type": 104,
#	"params": [],
#	"version": 1,
#	"contractVersion": 2
#}'
