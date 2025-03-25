from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from decimal import Decimal, InvalidOperation
import time

def establish_rpc_connection():
    return AuthServiceProxy("http://admin:admin@127.0.0.1:18443")

def prompt_amount(max_funds: Decimal, dest_address: str) -> Decimal:
    while True:
        try:
            funds = Decimal(input(f"\nEnter the amount to send from sender to receiver (max {max_funds} BTC): "))
            if funds <= Decimal('0'):
                print("Error: Amount must be greater than 0.")
            elif funds > max_funds:
                print(f"Error: Amount cannot exceed {max_funds} BTC.")
            else:
                return funds
        except InvalidOperation:
            print("Error: Invalid amount. Please enter a numeric value.")

def execute_transaction():
    wallet_name = "Synergy_Legacy"
    try:
        connection = establish_rpc_connection()
        try:
            connection.loadwallet(wallet_name)
            print(f"Loaded wallet: {wallet_name}")
        except JSONRPCException:
            connection.createwallet(wallet_name)
            print(f"Created wallet: {wallet_name}")

        connection = establish_rpc_connection()
        sender_address = connection.getnewaddress("Sender", "legacy")
        receiver_address = connection.getnewaddress("Receiver", "legacy")
        change_address = connection.getnewaddress("Change", "legacy")
        print(f"\nLegacy Addresses:\nSender: {sender_address}\nReceiver: {receiver_address}\nChange: {change_address}")

        print("\nMining some initial blocks to fund sender address ...\n")
        connection.generatetoaddress(101, sender_address)
        print(f"Balance of Sender: {connection.getbalance()} BTC")

        connection = establish_rpc_connection()
        sender_utxo = connection.listunspent(1, 9999999, [sender_address])[0]
        print(f"UTXO of Sender: {sender_utxo['amount']} BTC")

        transaction_fee = Decimal('0.0001')
        max_funds = sender_utxo["amount"] - transaction_fee
        funds = prompt_amount(max_funds, receiver_address)

        print("\nCreating a raw transaction from Sender to Receiver ...")
        connection = establish_rpc_connection()
        input_data = [{"txid": sender_utxo["txid"], "vout": sender_utxo["vout"]}]
        output_data = {
            receiver_address: funds,
            sender_address: sender_utxo["amount"] - funds - transaction_fee
        }
        raw_transaction = connection.createrawtransaction(input_data, output_data)
        print(f"\nUnsigned raw transaction hex: \n{raw_transaction}")

        print("\nDecoding raw transaction to extract the challenge script ... ")
        decoded_transaction = connection.decoderawtransaction(raw_transaction)
        extracted_script = decoded_transaction["vout"][0]["scriptPubKey"]["hex"]
        script_length = len(extracted_script) // 2
        print(f"\nExtracted ScriptPubKey: {extracted_script}")
        print(f"Script size: {script_length} vbytes")

        print("\nSigning the transaction Sender → Receiver ...")
        signed_transaction = connection.signrawtransactionwithwallet(raw_transaction)
        print(f"\nSigned transaction hex: \n{signed_transaction['hex']}")

        print("\nBroadcasting the transaction Sender → Receiver ...")
        transaction_id = connection.sendrawtransaction(signed_transaction["hex"])
        transaction_size = len(signed_transaction["hex"]) // 2
        print(f"\nTransaction ID (Sender → Receiver): {transaction_id}")
        print(f"Transaction size: {transaction_size} vbytes")

    except (JSONRPCException, ConnectionError) as error:
        print(f"Error: {error}. Retrying...")
        time.sleep(1)
        try:
            connection = establish_rpc_connection()
        except Exception as fatal_error:
            print(f"Fatal error: {fatal_error}")

    finally:
        try:
            connection = establish_rpc_connection()
            connection.unloadwallet(wallet_name)
            print(f"\nUnloaded wallet: {wallet_name}")
        except Exception as unload_error:
            print(f"Error unloading wallet: {unload_error}")

if __name__ == "__main__":
    execute_transaction()
    