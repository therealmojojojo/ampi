from json import load
import pathlib
import csv

database = {
    "53  b1  1d  1b  00  05  80":"https://open.spotify.com/album/1sKj6LEXiEfCmsiKwPy5uG", 
    "f0  a5  e5  a5":"",
    "53  b9  0d  3b  00  ea  80":"",
    "53  a9  08  1b  00  8a  80":""
}
initialized = False

def load_database(config_path=None):
    global database
    if config_path is None or config_path == '':
        path = str(pathlib.Path(__file__).parent.resolve())
    else: 
        path = config_path
    print("Getting card database from ", path)
    with open(path + '/database.csv', mode='r') as infile:
        reader = csv.reader(infile)
        database = {rows[0]:rows[1] for rows in reader}
    return database

def get_playlist(cardUID):
    global initialized
    if not initialized: 
        load_database()
        initialized = True
	
    print("Searching for ", cardUID)
    try:
        return database[cardUID].strip()
    except:
        print ('Card %s is not card list', cardUID)
        return None

if __name__ == '__main__':
    path = pathlib.Path(__file__).parent.resolve()
    load_database("")
    print(get_playlist("gibberish"))
    print(get_playlist("53  b1  1d  1b  00  05  80"))
    
