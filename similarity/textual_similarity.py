import lib.db as db
import lib.math as math
from similarity.helper import *
import time

# retrieve particular as well as all required documents from database
def retrieve_documents(db_session, table_name, doc_id):

	# connect to desired table
	table = db.table(db_session, table_name)
	
	# query database for particular id and all other ids to be compared with

	localtime = time.asctime( time.localtime(time.time()) )
	print("query doc retrieval start", localtime)
	query_doc = db.get(table, {"id": doc_id})
	localtime = time.asctime( time.localtime(time.time()) )
	print("query doc retrieval end", localtime)

	localtime = time.asctime( time.localtime(time.time()) )
	print("all doc retrieval start", localtime)
	all_docs = db.get(table, {})
	localtime = time.asctime( time.localtime(time.time()) )
	print("all doc retrieval end", localtime)

	return query_doc, all_docs


# query_doc is the document whose similarity will be compared with all_docs(all other docs in db)
# model describes which model to use to weigh features - tf/df/idf
# k specifies how many most similar documents to return
def calculate_similarity(query_doc, all_docs, model, k):

	# keys of vectors in database are stored as td/df/tf-idf
	vector_key = "vector_"+model.lower()
	all_similarities = []

 	# looping over all documets in database
	for doc in all_docs:

 		# do not calculate similarity of query doc with itself
		if doc["id"] == query_doc["id"]:
			continue
 		
 		# calculate similarity using cosine similarity measure
		similarity = {}
		similarity['id'] = doc['id']
		similarity['features'] = doc['features']
		similarity[vector_key] = doc[vector_key]
		error, similarity['value'] = math.cosine_similarity(doc[vector_key], query_doc[vector_key])
		if error:
			raise RuntimeError(error)

 		# sort similarities before adding them to return list 
		all_similarities = sort(all_similarities, similarity, k, 'value', 0)

	return all_similarities


# for most similar documents, calculates the 'k' most contributing features
# paramater similar_docs is a list of most similar documents already found
def calculate_most_contributing_features(query_doc, similar_docs, model, k):

	features = []
	vector_key = vector_key = "vector_"+model.lower()

	for similar_doc in similar_docs:
		
		feature_scores = []

		for similar_doc_feature in similar_doc["features"]:
				
			index = similar_doc_feature["index"]
			score = similar_doc[vector_key][index] * query_doc[vector_key][index]
				
			feature_score = {}
			feature_score["feature"] = similar_doc_feature["feature"]
			feature_score["value"] = score

			feature_scores = sort(feature_scores, feature_score, 3, "value", 0)
			
		features.append(feature_scores)

	return features
	


 # function that will be called from outside
def main(db_session, task, id, model, k):

 	# assuming default task is task 1
	table = "user" 

 	# check task number to assign table name
	if task == 2:
		table = "image"
	elif task == 3:
		table = "location"

 	# query document is the document corresponding to given id
 	# all_docs refers to all the documents for that entity(user/image/location)
	query_doc, all_docs = retrieve_documents(db_session, table, id)

 	# calculate similarities
	similarities = calculate_similarity(query_doc, all_docs, model, k)

 	# calculate the most important 3 features
	features = calculate_most_contributing_features(query_doc, similarities, model, 3)

	return similarities, features


def runner():

	db_client = db.get_db_client('localhost', 27017)
	db_session = db.connect_to_db(db_client, 'mwdb')
	print("database connection established")

	task = 3
	id = "10"
	model = "TF"
	k = 10

	similarities, features = main(db_session, task, id, model, k)

#runner()

	 

