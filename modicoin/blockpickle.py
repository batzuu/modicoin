import pickle
from modicoin.blockchain import Blockchain

try:
    blockchainfile = open("blockchainPickle.obj", 'rb')
    # Main blockchain object
    blockchain = pickle.load(blockchainfile)
    print("loaded")
except FileNotFoundError:
    blockchain = Blockchain()
    print("created")