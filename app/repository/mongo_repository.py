from datetime import datetime, timedelta

from pymongo import MongoClient
from bson import ObjectId


class AttackRepository:
    def __init__(self, db_url: str, db_name: str, collection_name: str):
        self.client = MongoClient(db_url)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def get_attack_by_id(self, attack_id: str):
        return self.collection.find_one({"_id": ObjectId(attack_id)})

    def get_all_attacks(self):
        return list(self.collection.find())

    def get_all_fatal_attacks_by_group(self, top_num: int = None):
        pipeline = [
            {"$unwind": "$attack_types"},
            {
                "$project": {
                    "attack_type": "$attack_types",
                    "points": {"$add": [{"$multiply": ["$fatalities", 2]}, "$injuries"]}
                }
            },
            {
                "$group": {
                    "_id": "$attack_type",
                    "total_points": {"$sum": "$points"}
                }
            },
            {"$sort": {"total_points": -1}},
        ]

        if top_num is not None:
            pipeline.append({"$limit": top_num})
        return list(self.collection.aggregate(pipeline))

    def percentage_of_casualties_by_region(self, location_type, top_num):
        pipeline = [
            {
                '$addFields': {
                    'casualties': {
                        '$add': [
                            {'$multiply': ["$fatalities", 2]},
                            "$injuries"
                        ]
                    }
                }
            },
            {
                '$group': {
                    '_id': f"$location.{location_type}",
                    'totalCasualties': {'$sum': "$casualties"},
                    'eventCount': {'$sum': 1},
                    'lat': {'$first': "$location.lat"},
                    'lon': {'$first': "$location.lon"}

                }
            },
            {
                '$project': {
                    '_id': 1,
                    'avgCasualties': {'$divide': ["$totalCasualties", "$eventCount"]},
                    'lat': 1,
                    'lon': 1
                }
            },
        ]
        if top_num is not None:
            pipeline.append({"$limit": top_num})
        return list(self.collection.aggregate(pipeline))

    def top_five_attackers(self):
        pipeline = [
            {
                "$unwind": "$group_names"},
            {
                "$match": {
                    "group_names": {"$ne": "Unknown"},
                }
            },
            {
                "$group": {
                    "_id": "$group_names",
                    "sum": {"$sum": 1}
                }
            },
            {
                "$sort": {"sum": -1}
            },
            {"$limit": 5}
        ]
        return list(self.collection.aggregate(pipeline))

    def get_all_attacks_by_years(self, years_ago=None):
        query = {}
        if years_ago is not None:
            cutoff_date = datetime.now() - timedelta(days=years_ago * 365)
            query["date"] = {"$gte": cutoff_date}
        return list(self.collection.find(query))

    def get_most_active_groups_per_country(self, country_name):
        pipeline = [
            {
                "$unwind": "$group_names"
            },
            {
                "$match": {
                    "group_names": {"$ne": "Unknown"}
                }
            },
            {
                "$group": {
                    "_id": {
                        "country": "$location.country",
                        "group": "$group_names"
                    },
                    "sum": {"$sum": 1},
                    "lat": {"$first": "$location.lat"},
                    "lon": {"$first": "$location.lon"}
                }
            },
            {
                "$sort": {
                    "_id.country": 1,
                    "sum": -1
                }
            },
            {
                "$group": {
                    "_id": "$_id.country",
                    "top_groups": {
                        "$push": {
                            "group": "$_id.group",
                            "sum": "$sum",
                            "lat": "$lat",
                            "lon": "$lon"
                        }
                    }
                }
            },
            {
                "$project": {
                    "top_groups": {"$slice": ["$top_groups", 5]}
                }
            }
        ]
        if country_name is not None:
            pipeline.insert(1, {"$match": {"location.country": country_name}})
        return list(self.collection.aggregate(pipeline))

    def delete_attack_by_id(self, attack_id: str):
        return self.collection.delete_one({"_id": ObjectId(attack_id)}).deleted_count

    def delete_all_attacks(self):
        return self.collection.delete_many({}).deleted_count