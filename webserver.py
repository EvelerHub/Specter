#!/usr/bin/env python
# Specter Node
# Nick Frichette 12/9/2017

import argparse

from flask import Flask
from flask import jsonify
from flask import request
from flask import render_template

from node import *
from wallet import *

app = Flask(__name__)

# ANSI escape sequences
FAIL = '\033[91m'
END = '\033[0m'
OK = '\033[92m'


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/', methods=['POST'])
def receive_tranactions():
    transaction = request.get_json()

    # We just received data from a wallet or node. We now need to
    # package it into a block and add it to the blockchain. First
    # We must validate it.
    if authenticate_transaction(transaction):
        if validate_transaction(transaction):
            print OK + "Valid Transaction Received" + END
            blockchain.make_block(transaction)
            return "Confirmation"
        else:
            return "Invalid"
    return "Invalid"


@app.route('/getblockchain', methods=['GET'])
def getblockchain():
    return jsonify(blockchain.jsonify())


def authenticate_transaction(transaction):
    is_verified = wallet.verify_remote_transaction(transaction['from'], transaction['signature'], transaction)
    return is_verified

def validate_transaction(transaction):
    is_validated = blockchain.validate_transaction(transaction)
    return is_validated


if __name__ == '__main__':
    # Take in CLI Arguments
    parser = argparse.ArgumentParser(description="Node and Web Server for Specter")
    parser.add_argument('-p', help="Run the Web Server on a non-standard port", type=int, default=5000)
    args = parser.parse_args()

    # Spawn our own node and get blockchain
    node = Node()
    blockchain = node.blockchain
    wallet = None

    # Our node should have its own wallet.
    # The convention for node wallets is different from a
    # standard wallet. Those keys should be in a directory
    # called nodekey. This is because a node should have
    # only one address to mine from. As well as to simplify
    # the issue of having a normal wallet in the same directory.
    for item in os.listdir('.'):
        if 'nodekey' in item:
            wallet = Wallet(item)

    if wallet is None:
        print FAIL + 'No wallet detected. Let\'s generate one' + END
        print OK + "Creating nodekey" + END
        wallet = Wallet('nodekey')

    print wallet.get_address()

    app.run(host='0.0.0.0', port=args.p)

