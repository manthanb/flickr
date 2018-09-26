from similarity.helper import *
from lib import db
import xml.etree.ElementTree as ET
import glob
from lib import math


def form_collections(file_paths):

	textual_descriptors = {}
	textual_descriptors['user'] = load_text_file(file_paths['user'])
	textual_descriptors['image'] = load_text_file(file_paths['image'])
	textual_descriptors['location'] = load_text_file(file_paths['location'])

	visual_descriptors = {}
	visual_descriptors_directory = load_directory(file_paths['visual_descriptors'])
	for file in visual_descriptors_directory:
		visual_descriptors[get_file_name(file)] = load_text_file(file)

	location_keys_file = load_xml_file(file_paths['location_keys'])
	location_keys_map = create_location_keys_map(location_keys_file)

	textual_collections = {}
	# for key, file in textual_descriptors.items():
	# 	textual_collections[key] = generate_textual_descriptors(key, file, location_keys_map)

	visual_collections = {}
	for key, file in visual_descriptors.items():
		tokenized_key = tokenize(key, " ")
		location_name = tokenized_key[0]
		model = tokenized_key[1]
		visual_collections[location_keys_map[location_name]+"_"+model] = generate_visual_descriptors(key, file, location_keys_map)

	return textual_collections, visual_collections


def generate_textual_descriptors(key, input_file, location_keys_map):

	print("inserting documents for", key)

	data_object = []
	feature_object = []
	feature_cache = {}
	feature_index = -1

	for line in input_file:
		tokens = tokenize(line, " ")
		new_object, new_features, feature_index, feature_cache = create_new_td_object(key, location_keys_map, tokens, feature_index, feature_cache)
		data_object.append(new_object)
		append(feature_object, new_features)

	object_index = 0
	while object_index < len(data_object):
		data_object[object_index] = load_vectors(data_object[object_index], feature_object)
		object_index = object_index + 1

	return data_object, feature_object


def create_new_td_object(key, location_keys_map, tokens, feature_index, feature_cache):
	
	data_object = {}
	data_object["id"] = tokens[0]
	data_object["features"] = []
	data_object["vector_tf"] = []
	data_object["vector_df"] = []
	data_object["vector_tf-idf"] = []

	new_features = []

	token_counter = 1

	if key == "location":
		data_object["id"] = location_keys_map[tokens[0]]
		location_name = tokens[0]
		location_name_length = len(tokenize(location_name, "_"))
		if location_name == 'doge_s_palace':
			location_name_length = 2
		token_counter = token_counter + location_name_length

	
	while token_counter < len(tokens)-1:
		
		if tokens[token_counter] not in feature_cache:
			
			if tokens[token_counter] == '' or tokens[token_counter] == '\n':
				token_counter = token_counter + 4
				continue

			feature_index = feature_index + 1
			
			new_feature = {}
			new_feature["term"] = tokens[token_counter]
			new_feature["index"] = feature_index
			new_feature["df"] = int(tokens[token_counter+2])
			new_features.append(new_feature)

			feature_cache[tokens[token_counter]] = feature_index

		data_object_term = {}

		data_object_term["feature"] = tokens[token_counter]
		data_object_term["index"] = feature_cache[tokens[token_counter]]
		data_object_term["tf"] = int(tokens[token_counter+1])
		data_object_term["df"] = int(tokens[token_counter+2])
		data_object_term["idf"] = float(tokens[token_counter+3])
		data_object["features"].append(data_object_term)

		token_counter = token_counter + 4

	return data_object, new_features, feature_index, feature_cache


def create_location_keys_map(location_keys_file):

	location_keys_map = {}
	topics = location_keys_file.getroot()

	for topic in topics:
		location_keys_map[topic[1].text] = topic[0].text

	return location_keys_map


def load_vectors(data_object, feature_object):

	for feature in feature_object:
		tf, df, idf = get_scores(data_object, feature)
		data_object["vector_tf"].append(tf)
		data_object["vector_df"].append(df)
		data_object["vector_tf-idf"].append(idf)


	return data_object


def get_scores(data_object, feature):

	tf = df = idf = 0

	for object_feature in data_object["features"]:
		if feature["index"] == object_feature["index"]:
			tf = object_feature["tf"]
			df = object_feature["df"]
			idf = object_feature["idf"]
			continue

	return tf, df, idf


def generate_visual_descriptors(input_file_name, input_file, location_keys_map):

	visual_descriptor_objects = []
	vectors = []

	for line in input_file:
		
		visual_descriptor_object = {}
		tokenized_line = tokenize(line, ",")
		
		visual_descriptor_object["id"] = tokenized_line[0]
		visual_descriptor_object["vector"] = to_float(tokenized_line[1:len(tokenized_line)])
		#visual_descriptor_object["cluster_center"] = []

		visual_descriptor_objects.append(visual_descriptor_object)
		vectors.append(visual_descriptor_object["vector"])

	error, cluster_centers = math.kmeans(vectors)
	if error:
		raise RuntimeError(error)

	print("clustering", input_file_name)

	#visual_descriptor_objects = assign_cluster_centers(visual_descriptor_objects, cluster_centers)

	cluster_center_object = {}
	cluster_center_object["id"] = location_keys_map[tokenize(input_file_name, " ")[0]]
	cluster_center_object["centers"] = to_list(cluster_centers)

	return visual_descriptor_objects, cluster_center_object


def assign_cluster_centers(visual_descriptor_objects, cluster_centers):

	for i in range(0, len(visual_descriptor_objects)):

		min_distance = 65536
		cluster_index = 0

		while cluster_index < len(cluster_centers):

			error, distance = math.euclidean_distance(visual_descriptor_objects[i]['vector'], cluster_centers[cluster_index])
			
			if error:
				raise RuntimeError(error)

			if distance < min_distance:
				min_distance = distance
				visual_descriptor_objects[i]['cluster_center'] = list(cluster_centers[cluster_index])
 			
			cluster_index = cluster_index + 1
	
	return visual_descriptor_objects


def insert_textual_collections(dbname, collections):

	for key, collection in collections.items():

		db_object_table = db.table(dbname, key)
		db.put(db_object_table, collection[0])

		db_features_table = db.table(dbname, key+"_features")
		db.put(db_features_table, collection[1])

	return

def insert_visual_collections(dbname, collections):

	for key, collection in collections.items():
		db_object_table = db.table(dbname, key)
		db.put(db_object_table, collection[0])

		db_cluster_table = db.table(dbname, "cluster_centers_"+tokenize(key, "_")[1])
		db.put(db_cluster_table, collection[1])

	return







