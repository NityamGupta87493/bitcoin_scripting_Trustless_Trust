from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from decimal import Decimal, InvalidOperation
import os
import shutil

def get_rpc_connection(wallet_name: str = None):
    base_url = "http://admin:admin@127.0.0.1:18443"
    if wallet_name:
        return AuthServiceProxy(f"{base_url}/wallet/{wallet_name}")
    return AuthServiceProxy(base_url)

def input_amount(max_amount: Decimal, recipient: str) -> Decimal:
    while True:
        try:
            amount = Decimal(input(f"\nEnter the amount to send from {recipient[0]} to {recipient[1]} (max {max_amount} BTC): "))
            if amount <= Decimal('0'):
                print("Error: Amount must be greater than 0.")
            elif amount > max_amount:
                print(f"Error: Amount cannot exceed {max_amount} BTC.")
            else:
                return amount
        except InvalidOperation:
            print("Error: Invalid amount. Please enter a numeric value.")

def main():
    wallet = "Synergy_SegWit"
    root_conn = get_rpc_connection()
    
    try:
        if wallet in root_conn.listwallets():
            root_conn.loadwallet(wallet)
            print(f"Loaded wallet: {wallet}")
        else:
            root_conn.createwallet(wallet)
            print(f"Created wallet: {wallet}")

        conn = get_rpc_connection(wallet)
        address_X = conn.getnewaddress("X", "p2sh-segwit")
        address_Y = conn.getnewaddress("Y", "p2sh-segwit")
        address_Z = conn.getnewaddress("Z", "p2sh-segwit")
        print(f"\nSegWit Addresses:\nX: {address_X}\nY: {address_Y}\nZ: {address_Z}")

        print("\nMining some initial blocks to fund address X ...")
        get_rpc_connection(wallet).generatetoaddress(101, address_X)
        
        conn = get_rpc_connection(wallet)
        utxo_X = conn.listunspent(1, 9999999, [address_X])[0]
        print(f"\nBalance of X: {conn.getbalance()} BTC")
        print(f"UTXO of X: {utxo_X['amount']} BTC")

        fee = Decimal('0.0001')
        max_amount = utxo_X["amount"] - fee
        amount = input_amount(max_amount, ("X", "Y"))

        print("\nCreating a raw transaction from X to Y ...")
        inputs = [{"txid": utxo_X["txid"], "vout": utxo_X["vout"]}]
        outputs = {address_Y: amount, address_X: utxo_X["amount"] - amount - fee}
        raw_tx_XY = conn.createrawtransaction(inputs, outputs)
        
        print("\nDecoding the transaction X → Y to extract challenge script ...")
        decoded_XY = conn.decoderawtransaction(raw_tx_XY)
        scriptPubKey_Y = decoded_XY["vout"][0]["scriptPubKey"]["hex"]
        script_size = len(scriptPubKey_Y) // 2
        print(f"\nExtracted ScriptPubKey: {scriptPubKey_Y}")
        print(f"Script size: {script_size} vbytes")

        print("\nSigning the transaction X → Y ...")
        signed_XY = conn.signrawtransactionwithwallet(raw_tx_XY)
        
        print("\nBroadcasting the transaction X → Y ...")
        txid_XY = conn.sendrawtransaction(signed_XY["hex"])
        decoded_signed_XY = conn.decoderawtransaction(signed_XY["hex"], True)
        tx_vsize_XY = decoded_signed_XY["vsize"]
        print(f"\nTransaction ID (X → Y): {txid_XY}")
        print(f"Transaction size: {tx_vsize_XY} vbytes")
        
        get_rpc_connection(wallet).generatetoaddress(1, address_X)

        print("\nFetching the UTXO list  ...")
        utxo_Y = conn.listunspent(1, 9999999, [address_Y])[0]
        print(f"\nUTXO of Y:\nTXID: {utxo_Y['txid']}\nVout: {utxo_Y['vout']}\nAmount: {utxo_Y['amount']} BTC")

        max_amount_YZ = utxo_Y["amount"] - fee
        amount_YZ = input_amount(max_amount_YZ, ("Y", "Z"))

        print("\nCreating a raw transaction from Y to Z ...")
        inputs = [{"txid": utxo_Y["txid"], "vout": utxo_Y["vout"]}]
        outputs = {address_Z: amount_YZ, address_Y: utxo_Y["amount"] - amount_YZ - fee}
        raw_tx_YZ = conn.createrawtransaction(inputs, outputs)
        
        print("\nSigning the transaction Y → Z ...")
        signed_YZ = conn.signrawtransactionwithwallet(raw_tx_YZ)
        
        print("\nBroadcasting the transaction Y → Z ...")
        txid_YZ = conn.sendrawtransaction(signed_YZ["hex"])
        decoded_signed_YZ = conn.decoderawtransaction(signed_YZ["hex"], True)
        tx_vsize_YZ = decoded_signed_YZ["vsize"]
        print(f"\nTransaction ID (Y → Z): {txid_YZ}")
        print(f"Transaction size: {tx_vsize_YZ} vbytes")
        
        print("\nDecoding the transaction Y → Z to extract response script ...")
        decoded_YZ_signed = conn.decoderawtransaction(signed_YZ["hex"])
        scriptSig = decoded_YZ_signed["vin"][0]["scriptSig"]["hex"]
        scriptSig_size = len(scriptSig) // 2
        print(f"\nExtracted ScriptSig: {scriptSig}")
        print(f"Script size: {scriptSig_size} vbytes")

    except JSONRPCException as e:
        print(f"Error: {e}")
    finally:
        try:
            root_conn.unloadwallet(wallet)
            print(f"\nUnloaded wallet: {wallet}")
            
            wallet_path = os.path.join(
                os.getenv('APPDATA'),
                'Bitcoin',
                'regtest',
                'wallets',
                wallet
            )
            if os.path.exists(wallet_path):
                shutil.rmtree(wallet_path)
        except:
            print()

if __name__ == "__main__":
    main()
    