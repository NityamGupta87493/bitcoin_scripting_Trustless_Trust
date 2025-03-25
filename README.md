# Bitcoin Legacy & SegWit Transaction Scripts

## Overview
This repository contains three Python scripts that interact with Bitcoin's RPC interface to perform transactions using Legacy and SegWit addresses. These scripts demonstrate the process of creating, signing, and broadcasting transactions on a Bitcoin test network.

## Scripts

### 1. `Legacy_1.py`
This script sets up a Bitcoin Legacy wallet (`Synergy_Legacy`), generates addresses, mines testnet blocks, and performs a transaction from a sender to a receiver using legacy addresses.
- Creates a legacy wallet and addresses.
- Mines initial blocks to fund the sender.
- Creates, signs, and broadcasts a transaction.
- Extracts and displays the `scriptPubKey`.

### 2. `Legacy_2.py`
An extended version of `Legacy_1.py`, adding:
- Wallet reloading mechanism.
- Verification of existing UTXOs before creating transactions.
- Extracting and displaying `scriptSig` from the transaction input.

### 3. `segwit.py`
This script demonstrates SegWit transactions using a `p2sh-segwit` wallet (`Synergy_SegWit`). It executes transactions between three parties:
- Generates SegWit addresses.
- Mines test blocks.
- Performs two transactions: X → Y and Y → Z.
- Extracts `scriptPubKey` and `scriptSig`.
- Computes transaction sizes to compare efficiency.

## Requirements
- Bitcoin Core with RPC enabled.
- Python 3.
- `bitcoinrpc` library (install using `pip install python-bitcoinrpc`).

## Setup & Usage
1. Ensure Bitcoin Core is running in regtest mode with RPC enabled:
   ```sh
   bitcoind -regtest -daemon -server -rpcuser=admin -rpcpassword=admin
   ```
2. Clone this repository and install dependencies:
   ```sh
   git clone <repo_url>
   cd <repo_directory>
   pip install -r requirements.txt
   ```
3. Run any script:
   ```sh
   python Legacy_1.py
   python Legacy_2.py
   python segwit.py
   ```

## Expected Output
- Bitcoin addresses, transactions, and UTXO details.
- Raw and signed transaction hex values.
- Transaction sizes and extracted scripts.

## Notes
- The scripts run on Bitcoin's `regtest` network, so they are safe for testing.
- Ensure the Bitcoin RPC server is running before executing the scripts.
- The transaction fees and mining block rewards are preset for demonstration.


