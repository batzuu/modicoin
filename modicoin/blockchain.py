from Crypto.PublicKey import RSA
import datetime
import time
from datetime import datetime
import json
from hashlib import sha256

class Blockchain:
	def __init__(self):
		self.unconfirmed_trainsactions = []
		self.chain = []
		self.generate_genesis_block()
		self.miner_reward = 50

	def generate_genesis_block(self):
		genesis_block = Block(0, [], "0", datetime.now().strftime("%m/%d/%Y, %H:%M:%S")) 
		genesis_block_hash = genesis_block.compute_hash()
		self.chain.append(genesis_block)
	
	# property decorator to get the last block
	@property
	def last_block(self):
		return self.chain[-1]

	difficulty = 2
	def proof_of_work(self, block):
		block.nonce = 0
		block_hash = block.compute_hash()
		while not block_hash.startswith("0" * Blockchain.difficulty):
			block.nonce += 1
			block_hash = block.compute_hash()
		print("Found the hash - ")
		print(block_hash)
		return block_hash
	
	def add_block(self, block, proof):
		prev_hash = self.last_block.hash
		if prev_hash != block.prev_hash:
			return False
		if not self.is_valid_proof(block, proof):
			return False
		block.hash = proof
		self.chain.append(block)
		return True
	
	def is_valid_proof(self, block, proof):
		if (proof.startswith("0" * Blockchain.difficulty) and proof == block.compute_hash()):
			return True
		else:
			return False
	
	def add_new_transaction(self, transaction, sender, receiver, amt):
			
		self.unconfirmed_trainsactions.append(transaction)
	
	def generate_keys(self):
		key = RSA.generate(2048)
		priv_key = key.export_key()
		f = open("private.pem", "wb")
		f.write(priv_key)
		f.close()

		public_key = key.publickey().export_key()
		private_key = key.export_key()
		f = open("public.pem", "wb")
		f.write(public_key)
		f.close()
		key = {}
		key = {'public':public_key.decode("ASCII"),
			'private':private_key.decode("ASCII")
			}
		print(key)
		return key
	
	def mine(self):
		if not self.unconfirmed_trainsactions:
			return False
		
		last_block = self.last_block
		new_block = Block(last_block.index + 1, self.unconfirmed_trainsactions, last_block.hash, datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))

		proof = self.proof_of_work(new_block)
		self.add_block(new_block, proof)
		self.unconfirmed_trainsactions = []
		return new_block.index

class Block:
	def __init__(self, index, transactions, prev_hash, timestamp, nonce=0):
		self.index = index
		self.transactions = transactions
		self.prev_hash = prev_hash
		self.timestamp = timestamp
		self.hash = self.compute_hash()
		self.nonce = nonce
		self.miner = ""

	def compute_hash(self):
		block_str = json.dumps(self.__dict__, sort_keys=True)
		return sha256(block_str.encode()).hexdigest()

class Transaction:
	def __init__(self, sender, receiver, amt):
		self.sender = sender
		self.receiver = receiver
		self.amt = amt
		self.time = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
		self.hash = self.calculate_hash()

	def calculate_hash(self):
		hash_str = self.sender + self.receiver + str(self.amt) + str(self.time)
		hash_str_encode = json.dumps(hash_str, sort_keys=True).encode()
		return sha256(hash_str_encode).hexdigest()

