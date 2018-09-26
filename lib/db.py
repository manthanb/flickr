from pymongo import MongoClient 

# create a client(channel) to given host and port
def get_db_client(host, port):
	return MongoClient(host, port)

# create session for given client and database
def connect_to_db(client, dbname):
	return client[dbname]

# close connection
def close(client):
	client.close()

# create connection to given collection inside given db
def table(db, collection):
	return db[collection]

# retrieve documents from given collection w.r.t. given query
# implements both findAll and findOne
# output will be array in case of multiple docs are object in case of single doc
def get(collection, query):
	cursor = collection.find(query)
	res = []
	for doc in cursor:
		res.append(doc)
	if len(res) == 1:
		res = res[0]
	return res

# insert given list of documents into given collection
def put(collection, docs):
	if isinstance(docs, list):
		return collection.insert_many(docs)
	doc_list = []
	doc_list.append(docs)
	return collection.insert_many(doc_list)
