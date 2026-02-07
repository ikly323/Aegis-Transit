import grpc
import os
import sys
import traceback

from protobuf import contract_contract_service_pb2 as contract_pb2
from protobuf import contract_contract_service_pb2_grpc as contract_pb2_grpc
from protobuf import data_entry_pb2 as common_pb2


CreateContractTransactionType = 103
CallContractTransactionType = 104
AUTH_METADATA_KEY = "authorization"

print("=== SCRIPT STARTED ===", file=sys.stderr)
print("Python version:", sys.version, file=sys.stderr)
print("Current working dir:", os.getcwd(), file=sys.stderr)
print("os.environ keys:", list(os.environ.keys()), file=sys.stderr)

class ContractHandler:
    def __init__(self, stub, connection_id):
        print(f"ContractHandler.__init__ called with connection_id={connection_id}", file=sys.stderr)
        self.client = stub
        self.connection_id = connection_id

    def start(self, connection_token):
        print(f"start() called with token length={len(connection_token)}", file=sys.stderr)
        try:
            self.__connect(connection_token)
        except Exception as e:
            print(f"start() EXCEPTION: {type(e).__name__}: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)

    def __connect(self, connection_token):
        print("__connect() started", file=sys.stderr)
        try:
            request = contract_pb2.ConnectionRequest(
                connection_id=self.connection_id
            )
            print("ConnectionRequest created", file=sys.stderr)

            metadata = [(AUTH_METADATA_KEY, connection_token)]
            print("Metadata prepared", file=sys.stderr)

            print("Calling client.Connect() ...", file=sys.stderr)
            stream = self.client.Connect(request=request, metadata=metadata)

            for i, contract_transaction_response in enumerate(stream):
                print(f"Received message #{i+1} from stream", file=sys.stderr)
                self.__process_connect_response(contract_transaction_response)
        except Exception as e:
            print(f"__connect() EXCEPTION: {type(e).__name__}: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)

    def __process_connect_response(self, contract_transaction_response):
        print("=== __process_connect_response START ===", file=sys.stderr)
        try:
            print("Full response:", contract_transaction_response, file=sys.stderr)
            contract_transaction = contract_transaction_response.transaction
            print(f"Transaction type: {contract_transaction.type}", file=sys.stderr)

            if contract_transaction.type == CreateContractTransactionType:
                print("Branch: CreateContractTransaction", file=sys.stderr)
                self.__handle_create_transaction(contract_transaction_response)
            elif contract_transaction.type == CallContractTransactionType:
                print("Branch: CallContractTransaction", file=sys.stderr)
                self.__handle_call_transaction(contract_transaction_response)
            else:
                print(f"UNKNOWN transaction type: {contract_transaction.type}", file=sys.stderr)
        except Exception as e:
            print(f"__process_connect_response EXCEPTION: {type(e).__name__}: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
        print("=== __process_connect_response END ===", file=sys.stderr)

    def __handle_create_transaction(self, contract_transaction_response):
        print("=== __handle_create_transaction START ===", file=sys.stderr)
        try:
            create_transaction = contract_transaction_response.transaction
            print(f"Create tx id: {create_transaction.id}", file=sys.stderr)

            results_list = [
                common_pb2.DataEntry(key="Sender", string_value="OOO sender"),
		common_pb2.DataEntry(key="INN_sender", string_value="88005553535"),
                common_pb2.DataEntry(key="Recipient", string_value="OOO recipient"),
		common_pb2.DataEntry(key="INN_recipient", string_value="8541268"),
                common_pb2.DataEntry(key="Carrier", string_value="OOO carrier"),
		common_pb2.DataEntry(key="INN_carrier", string_value="542281448"),
                common_pb2.DataEntry(key="temperature", string_value="+20/+35"),
		common_pb2.DataEntry(key="light", string_value="700/1100"),
		common_pb2.DataEntry(key="press", string_value="900/1100"),
		common_pb2.DataEntry(key="integrity", string_value="None")
            ]

            request = contract_pb2.ExecutionSuccessRequest(
                tx_id=create_transaction.id,
                results=results_list
            )
            print("ExecutionSuccessRequest prepared", file=sys.stderr)

            metadata = [(AUTH_METADATA_KEY, contract_transaction_response.auth_token)]
            print("Metadata for CommitExecutionSuccess prepared", file=sys.stderr)

            print("Calling CommitExecutionSuccess...", file=sys.stderr)
            response = self.client.CommitExecutionSuccess(request=request, metadata=metadata)
            print(f"CommitExecutionSuccess response: {response}", file=sys.stderr)
        except Exception as e:
            print(f"__handle_create_transaction EXCEPTION: {type(e).__name__}: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
        print("=== __handle_create_transaction END ===", file=sys.stderr)

    def __handle_call_transaction(self, contract_transaction_response):
        print("=== __handle_call_transaction START ===", file=sys.stderr)
        try:
            call_transaction = contract_transaction_response.transaction
            print(f"Call tx id: {call_transaction.id}", file=sys.stderr)

            metadata = [(AUTH_METADATA_KEY, contract_transaction_response.auth_token)]
            print("Metadata prepared", file=sys.stderr)

            contract_key_request = contract_pb2.ContractKeyRequest(
                contract_id=call_transaction.contract_id,
                key="sum"
            )
            print("ContractKeyRequest prepared", file=sys.stderr)

            print("Calling GetContractKey...", file=sys.stderr)
            contract_key = self.client.GetContractKey(request=contract_key_request, metadata=metadata)
            old_value = contract_key.entry.int_value
            print(f"Old value from key 'sum': {old_value}", file=sys.stderr)

            request = contract_pb2.ExecutionSuccessRequest(
                tx_id=call_transaction.id,
                results=[common_pb2.DataEntry(key="integrity", string_value='crash!!!')]
            )
            print("ExecutionSuccessRequest prepared", file=sys.stderr)

            print("Calling CommitExecutionSuccess...", file=sys.stderr)
            response = self.client.CommitExecutionSuccess(request=request, metadata=metadata)
            print(f"CommitExecutionSuccess response: {response}", file=sys.stderr)
        except Exception as e:
            print(f"__handle_call_transaction EXCEPTION: {type(e).__name__}: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
        print("=== __handle_call_transaction END ===", file=sys.stderr)

def run(connection_id, node_host, node_port, connection_token):
    print(f"run() called with node={node_host}:{node_port}, conn_id={connection_id}", file=sys.stderr)
    try:
        channel_address = f"{node_host}:{node_port}"
        print(f"Creating insecure channel to {channel_address}", file=sys.stderr)
        with grpc.insecure_channel(channel_address) as channel:
            print("Channel created", file=sys.stderr)
            stub = contract_pb2_grpc.ContractServiceStub(channel)
            print("Stub created", file=sys.stderr)
            handler = ContractHandler(stub, connection_id)
            print("Handler created", file=sys.stderr)
            handler.start(connection_token)
            print("handler.start() finished", file=sys.stderr)
    except Exception as e:
        print(f"run() EXCEPTION: {type(e).__name__}: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)

CONNECTION_ID_KEY = 'CONNECTION_ID'
CONNECTION_TOKEN_KEY = 'CONNECTION_TOKEN'
NODE_KEY = 'NODE'
NODE_PORT_KEY = 'NODE_PORT'

if __name__ == '__main__':
    print("=== MAIN BLOCK START ===", file=sys.stderr)
    print("os.environ keys:", list(os.environ.keys()), file=sys.stderr)

    if CONNECTION_ID_KEY not in os.environ:
        print("Connection id is not set", file=sys.stderr)
        sys.exit("Connection id is not set")
    print("CONNECTION_ID found", file=sys.stderr)

    if CONNECTION_TOKEN_KEY not in os.environ:
        print("Connection token is not set", file=sys.stderr)
        sys.exit("Connection token is not set")
    print("CONNECTION_TOKEN found", file=sys.stderr)

    if NODE_KEY not in os.environ:
        print("Node host is not set", file=sys.stderr)
        sys.exit("Node host is not set")
    print("NODE found", file=sys.stderr)

    if NODE_PORT_KEY not in os.environ:
        print("Node port is not set", file=sys.stderr)
        sys.exit("Node port is not set")
    print("NODE_PORT found", file=sys.stderr)

    connection_id = os.environ['CONNECTION_ID']
    connection_token = os.environ['CONNECTION_TOKEN']
    node_host = os.environ['NODE']
    node_port = os.environ['NODE_PORT']

    print(f"Calling run() with: conn_id={connection_id}, node={node_host}:{node_port}", file=sys.stderr)
    run(connection_id, node_host, node_port, connection_token)
    print("=== MAIN BLOCK END ===", file=sys.stderr)
