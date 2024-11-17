import pymongo



client = pymongo.MongoClient("mongodb://localhost:27017/")

db = client["YatrueMaps"]


user_collection = db["users"]

all_users = user_collection.find()

for user in all_users:
    print(user)
    print("\n")

client.close()
