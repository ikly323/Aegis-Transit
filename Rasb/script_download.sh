#!/bin/bash

DATA_FILE="$HOME/Desktop/DockerRun/credentials.txt"


BLOCKCHAIN_ADDRESS=$(grep -A5 "node-1" "$DATA_FILE" | grep "blockchain address:" | cut -d ':' -f 2 | xargs)


KEYPAIR_PASSWORD=$(grep -A5 "node-1" "$DATA_FILE" | grep "keypair password:" | cut -d ':' -f 2 | xargs)




CONTRACT_ID=$(curl -X GET "http://localhost:6872/contracts" -H  "accept: application/json" -H  "X-API-Key: we" | grep -m 1 "contractId" | cut -d ':' -f 2 | cut -d '"' -f 2)


curl -X POST "http://localhost:6872/contracts" -H  "accept: application/json" -H  "Content-Type: application/json" -H  "X-API-Key: we" -d "{  \"contracts\": [    \"$CONTRACT_ID\"  ]}" | python3 Rasb_serv.py | tee test.txt

if tail -40 test.txt | grep -q "FAIL"; then
curl -X POST --verbose "http://127.0.0.1:6872/transactions/signAndBroadcast" \
  -H "Content-Type: application/json" \
  -H "X-Contract-Api-Token: we" \
  -d '
{
  	"contractId": "'"$CONTRACT_ID"'",
	"fee": 10,
	"sender": "'"$BLOCKCHAIN_ADDRESS"'",
	"password":"'"$KEYPAIR_PASSWORD"'",
	"type": 104,
	"params": [],
	"version": 1,
	"contractVersion": 2
}'
echo "Error trans."
fi
#It is necessary to change the confidant settings so that it can be executed either on node 1, or download the transport on the side of node 0
#curl -X POST --verbose "http://127.0.0.1:6872/transactions/signAndBroadcast" \
#  -H "Content-Type: application/json" \
#  -H "X-Contract-Api-Token: we" \
#  -d '
#{
#    "sender":"'"$BLOCKCHAIN_ADDRESS"'",
#    "password": "'"$KEYPAIR_PASSWORD"'",
#    "contractId":"'"$CONTRACT_ID"'",
#    "fee": 789654,
#    "type": 106,
#    "version": 2
#}' 


echo "The server has stopped working, the cargo integrity has been changed in the contract " # in case of an error, contract change 104 is sent (this is stub)

rm FLAG_FILE.txt

rm test.txt
