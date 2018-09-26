from config import parser as cfg_parser
from lib import db
from similarity import load
import time

localtime = time.asctime( time.localtime(time.time()) )
print(localtime)

print("initialising project")

config = cfg_parser.load_config()
print("app config loaded")

db_client = db.get_db_client(cfg_parser.get(config, 'DB', 'url'), 27017)
db_session = db.connect_to_db(db_client, cfg_parser.get(config, 'DB', 'db'))
print("database connection established")

file_paths = {}
file_paths['user'] = cfg_parser.get(config, 'Data', 'user')
file_paths['image'] = cfg_parser.get(config, 'Data', 'image')
file_paths['location'] = cfg_parser.get(config, 'Data', 'location')
file_paths['location_keys'] = cfg_parser.get(config, 'Data', 'location_keys')
file_paths['visual_descriptors'] = cfg_parser.get(config, 'Data', 'visual_descriptors')

textual_collections, visual_collections = load.form_collections(file_paths)
print("documents created")

# print("inserting textual collections to database")
# load.insert_textual_collections(db_session, textual_collections)
print("inserting visual collections to database")
load.insert_visual_collections(db_session, visual_collections)

print("inserted documents to database")

print("initialization successful")

print("closing connection to database")
db.close(db_client)

localtime = time.asctime( time.localtime(time.time()) )
print(localtime)
