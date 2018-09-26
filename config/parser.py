import configparser as cp

# create config object and load config file in it
def load_config():
	config = cp.ConfigParser()
	config.read('/Users/manthan/Code/Python/mwdb/project/config/config.ini')
	return config

# return the value of given key from given section
def get(config, section, key):
	return config[section][key]
