from config import parser as cfg_parser
from lib import db
from similarity import textual_similarity as ts
from similarity import visual_similarity as vs
import time

def main():

	config = cfg_parser.load_config()

	db_client = db.get_db_client(cfg_parser.get(config, 'DB', 'url'), 27017)
	db_session = db.connect_to_db(db_client, cfg_parser.get(config, 'DB', 'db'))
	
	print("welcome")
	choice = "yes"

	while choice == "yes":
		
		task = get_task()
		id = get_id(task)
		model = get_model(task)
		k = get_k()

		print_result(db_session, task, id, model, k)
	
		choice = input("\nwould you like to test for more tasks?(yes/no)\n")

	print("thank you")

def print_result(db_session, task, id, model, k):

	if task <=3:
		localtime = time.asctime( time.localtime(time.time()) )
		print("search start", localtime)
		similar_documents, similar_features = ts.main(db_session, task, id, model, k)
		print("top %d similar documents are" %k)
		for i in range(0, len(similar_documents)):
			print(i+1, " id:", similar_documents[i]["id"])
			print(i+1, " matching score:", similar_documents[i]["value"])
			print("top 3 contributing features for this document are: ", similar_features[i][0]['feature'], similar_features[i][1]['feature'], similar_features[i][2]['feature'])
		localtime = time.asctime( time.localtime(time.time()) )
		print("search end", localtime)

	elif task == 4:
		localtime = time.asctime( time.localtime(time.time()) )
		print("search start", localtime)
		similar_documents, similar_images = vs.main(db_session, task, id, model, k)
		print("top %d similar locations are" %k)
		for i in range(0, len(similar_documents)):
			print(i+1, " id:", similar_documents[i]["id"])
			print(i+1, " matching score:", similar_documents[i]["value"])
			print("top 3 contributing image pairs for this location are: \n") 
			print("		"+ similar_images[i][0]['query_image'] + ", " + similar_images[i][0]['compared_image'] + "\n")
			print("		"+ similar_images[i][1]['query_image'] + ", " + similar_images[i][1]['compared_image'] + "\n")
			print("		"+ similar_images[i][1]['query_image'] + ", " + similar_images[i][1]['compared_image'] + "\n")
		localtime = time.asctime( time.localtime(time.time()) )
		print("search end", localtime)

	elif task == 5:
		localtime = time.asctime( time.localtime(time.time()) )
		print("search start", localtime)
		similar_documents, model_contributions = vs.main(db_session, task, id, model, k)
		print("top %d similar locations are " %k)
		for i in range(0, len(similar_documents)):
			print(i+1, " id:", similar_documents[i]["id"])
			print(i+1, " matching rank:", similar_documents[i]["rank"])
			print("top 3 contributing image pairs for this location are: \n")
			for j in range(0, 10):
				print("		model:", model_contributions[i+j]["model"], "rank:", model_contributions[i+j]["rank"], "\n")
		localtime = time.asctime( time.localtime(time.time()) )
		print("search end", localtime)
		

def get_task():

	task = input("enter the task number(1-5) for which you want to run tests\n")
	task = int(task)

	if task < 1 or task > 5:
		print("oops! invalid task number")
		exit()

	return task

def get_id(task):

	id = input("enter the id for which you want to run tests\n")

	if id == "" or id == " ":
		print("oops! invalid id")
		exit()

	return id


def get_model(task):

	if task == 5:
		return ""

	model = input("enter the model for which you want to run tests\n")

	if model == "" or model == " ":
		print("oops! invalid model")
		exit()

	return model

def get_k():

	k = input("enter the num of similar document that you need for given ID\n")
	k = int(k)

	if k == 0:
		print("oops! invalid k")
		exit()

	return k

main()



