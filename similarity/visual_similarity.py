import lib.db as db
import lib.math as math
from similarity.helper import *
import time


def retrieve_documents_for_task4(db_session, table_name, doc_id):

	table = db.table(db_session, table_name)

	query_doc = db.get(table, {"id": doc_id})
	all_docs = db.get(table, {})

	return query_doc, all_docs

def get_location_images(db_session, id, model):

	table = db.table(db_session, id+"_"+model)
	return db.get(table, {})

def task4(db_session, id, model, k):

	query_doc, all_docs = retrieve_documents_for_task4(db_session, "cluster_centers_"+model, id)
	cluster_similarities = []

	for doc in all_docs:

		if doc["id"] == id:
			continue

		similarity = {}
		similarity["id"] = doc["id"]
		similarity["value"] = 0

		for query_doc_center in query_doc["centers"]:
			for other_doc_center in doc["centers"]:
				error, score = math.euclidean_distance(query_doc_center, other_doc_center)
				if error:
					raise RuntimeError(error)
				similarity["value"] = similarity["value"] + score

		similarity["value"] = similarity["value"] / ( len(query_doc["centers"]) * len(doc["centers"]) )
		cluster_similarities = sort(cluster_similarities, similarity, k, "value", 1)

	query_location_images = get_location_images(db_session, id, model)
	images = []

	for item in cluster_similarities:

		other_location_images = get_location_images(db_session, item["id"], model)
		image_scores = []

		for query_image in query_location_images:

			for other_image in other_location_images:

				error, score = math.euclidean_distance(query_image["vector"], other_image["vector"])
				if error:
					raise RuntimeError(error)
 				
				image_score_object = {}
				image_score_object["query_image"] = query_image["id"]
				image_score_object["compared_image"] = other_image["id"]
				image_score_object["value"] = score 

				image_scores = sort(image_scores, image_score_object, 3, "value", 1)

		images.append(image_scores)

	return cluster_similarities, images


def get_clusters(db_session):

	models = ["CM", "CM3x3", "CN", "CN3x3", "CSD", "GLRLM", "GLRLM3x3", "HOG", "LBP", "LBP3x3"]
	cluster_models = {}

	for model in models:
		table = db.table(db_session, "cluster_centers_"+model)
		cluster_model = db.get(table, {})
		cluster_models[model] = cluster_model

	return cluster_models


def distance(query_doc_centers, compare_doc_centers):

	distance = 0

	for query_doc_center in query_doc_centers:
			for other_doc_center in compare_doc_centers:
				error, score = math.euclidean_distance(query_doc_center, other_doc_center)
				if error:
					raise RuntimeError(error)
				distance = distance + score

	distance = distance / ( len(query_doc_centers) * len(compare_doc_centers) )

	return distance


def get_similarity_task5(distance_matrix, id, k):

	model_rank_matrix = {}

	for model in distance_matrix:
		documents_sorted_by_distance = sort_documents(distance_matrix[model])
		model_rank_matrix[model] = documents_sorted_by_distance

	documents_ranks = []

	for i in range(1, 31):
		
		if i == int(id):
			continue

		document_rank = {}
		document_rank["id"] = str(i)
		document_rank["rank"] = get_rank(model_rank_matrix, str(i))
		documents_ranks = sort(documents_ranks, document_rank, k, "rank", 1)

	model_contributions = []

	for doc in documents_ranks:
		for model, model_docs in model_rank_matrix.items():
			doc_index = 1
			for model_doc in model_docs:
				if doc["id"] == model_doc["id"]:
					model_contribution = {}
					model_contribution["model"] = model
					model_contribution["rank"] = doc_index
					model_contributions.append(model_contribution)
					break
				doc_index = doc_index + 1

	return  documents_ranks, model_contributions


def get_rank(model_rank_matrix, id):

	rank = 0

	for name, model in model_rank_matrix.items():

		for i in range(0, len(model)):
			if model[i]['id'] != id:
				continue
			elif model[i]['id'] == id:
				rank = rank + (i+1)
				break

	return rank

	

def sort_documents(model):

	docs = []

	for doc_id, distance in model.items():
		doc = {}
		doc["id"] = doc_id
		doc["distance"] = distance

		docs = sort(docs, doc, 29, "distance", 1)

	return docs



def task5(db_session, id, k):

	cluster_models = get_clusters(db_session)
	distance_matrix = {}

	for model, docs in cluster_models.items():
	
		distance_matrix[model] = {}

		query_doc_centers = []
		for doc in docs:
			if doc["id"] == id:
				query_doc_centers = doc["centers"]
				break

		for doc in docs:
			if doc["id"] == id:
				continue
			distance_matrix[model][doc["id"]] = distance(query_doc_centers, doc["centers"])

	documents_ranks, model_contributions = get_similarity_task5(distance_matrix, id, k)

	return documents_ranks, model_contributions 


def main(db_session, task, id, model, k):

	if task ==  4:
		similar_locations = task4(db_session, id, model, k)
		return similar_locations

	elif task == 5:
		return task5(db_session, id, k)

def runner():

	db_client = db.get_db_client('localhost', 27017)
	db_session = db.connect_to_db(db_client, 'mwdb')
	print("database connection established")

	task = 4
	id = "22"
	model = "CM"
	k = 5

	if task ==  4:
		similar_locations = task4(db_session, id, model, k)
		return similar_locations


	return

#print(runner())