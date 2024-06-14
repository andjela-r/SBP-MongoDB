from pymongo import MongoClient
import pandas as pd
import json

def mongoimport(csv_path, db_name, coll_name, db_url='localhost', db_port=27017):
    """ Imports a csv file at path csv_name to a mongo colection
    returns: count of the documants in the new collection
    """
    client = MongoClient(db_url, db_port)
    db = client[db_name]
    coll = db[coll_name]
    data = pd.read_csv(csv_path)
    payload = json.loads(data.to_json(orient='records'))
    if coll_name in db.list_collection_names():
        coll.drop()

    coll.insert_many(payload)
    count = coll.count_documents({})
    
    client.close()
    return count


mongoimport('C:/Users/Kiki/Documents/python files/mongodb_skripta/champs.csv', 'league_of_legends', 'champs')
mongoimport('C:/Users/Kiki/Documents/python files/mongodb_skripta/clean_matches.csv', 'league_of_legends', 'matches')
mongoimport('C:/Users/Kiki/Documents/python files/mongodb_skripta/clean_participants.csv', 'league_of_legends', 'participants')
mongoimport('C:/Users/Kiki/Documents/python files/mongodb_skripta/clean_player_stats.csv', 'league_of_legends', 'playerstats')
mongoimport('C:/Users/Kiki/Documents/python files/mongodb_skripta/clean_teambans.csv', 'league_of_legends', 'teambans')
mongoimport('C:/Users/Kiki/Documents/python files/mongodb_skripta/clean_teamstats.csv', 'league_of_legends', 'teamstats')
