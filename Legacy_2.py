from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from decimal import Decimal, InvalidOperation
import time

def establish_rpc_connection():
    return AuthServiceProxy("http://admin:admin@127.0.0.1:18443")

def prompt_transfer_amount(max_funds: Decimal, destination_address: str) -> Decimal:
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

def execute_transfer():
    wallet_name = "Synergy_Legacy"
    try:
        connection = establish_rpc_connection()
        loaded_wallets = connection.listwallets()
        if wallet_name not in loaded_wallets:
            connection.loadwallet(wallet_name)
            print(f"Loaded wallet: {wallet_name}")
        else:
            print(f"Wallet '{wallet_name}' is already loaded.")

        connection = establish_rpc_connection()  
        sender_address = connection.getaddressesbylabel("Sender")
        receiver_address = connection.getaddressesbylabel("Receiver")

        if sender_address:
            sender_address = list(sender_address.keys())[0]
        else:
            sender_address = connection.getnewaddress("Sender", "legacy")

        if receiver_address:
            receiver_address = list(receiver_address.keys())[0]
        else:
            receiver_address = connection.getnewaddress("Receiver", "legacy")

        print(f"\nSender Address: {sender_address}\nReceiver Address: {receiver_address}")

        connection = establish_rpc_connection() 
        print("\nFetching the UTXO list ...")
        sender_utxo = connection.listunspent(0, 9999999, [sender_address])
        if not sender_utxo:
            print(f"No UTXO found for sender address: {sender_address}")
            return

        sender_utxo = sender_utxo[0]
        print(f"\nUTXO of Sender:\nTXID: {sender_utxo['txid']}\nVout: {sender_utxo['vout']}\nAmount: {sender_utxo['amount']} BTC")

        transaction_fee = Decimal('0.0001')
        max_funds = sender_utxo["amount"] - transaction_fee
        funds = prompt_transfer_amount(max_funds, receiver_address)

        connection = establish_rpc_connection() 
        print("\nCreating the transaction from Sender to Receiver ...")
        input_data = [{"txid": sender_utxo["txid"], "vout": sender_utxo["vout"]}]
        output_data = {
            receiver_address: funds,
            sender_address: sender_utxo["amount"] - funds - transaction_fee
        }
        raw_transaction = connection.createrawtransaction(input_data, output_data)
        print(f"\nUnsigned raw transaction hex: \n{raw_transaction}")

        print("\nSigning the transaction Sender → Receiver ...")
        signed_transaction = connection.signrawtransactionwithwallet(raw_transaction)
        print(f"\nSigned transaction hex: \n{signed_transaction['hex']}")

        print("\nBroadcasting the transaction Sender → Receiver ...")
        transaction_id = connection.sendrawtransaction(signed_transaction["hex"])
        transaction_size = len(signed_transaction["hex"]) // 2
        print(f"\nTransaction ID (Sender → Receiver): {transaction_id}")
        print(f"Transaction size: {transaction_size} vbytes")

        connection = establish_rpc_connection()  
        print("\nDecoding raw transaction to extract the response script ...")
        decoded_transfer = connection.decoderawtransaction(signed_transaction["hex"])
        extracted_scriptSig = decoded_transfer["vin"][0]["scriptSig"]["hex"]
        scriptSig_length = len(extracted_scriptSig) // 2
        print(f"\nExtracted ScriptSig:\n{extracted_scriptSig}")
        print(f"Script size: {scriptSig_length} vbytes")

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
    execute_transfer()