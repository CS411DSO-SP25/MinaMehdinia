from pymongo import MongoClient

client = MongoClient("mongodb://127.0.0.1:27017/")
db = client["academicworld"]

def find_faculty_by_keyword(keyword_input):
    query = {"keywords.name": {"$regex": keyword_input, "$options": "i"}}
    projection = {"name": 1, "keywords": 1, "photoUrl": 1, "_id": 0}

    results = []
    for doc in db.faculty.find(query, projection):
        matched_keywords = [k for k in doc.get("keywords", []) if keyword_input.lower() in k["name"].lower()]
        if matched_keywords:
            best_match = max(matched_keywords, key=lambda x: x["score"])
            results.append({
                "name": doc["name"],
                "photoUrl": doc.get("photoUrl", ""),
                "keyword": best_match["name"],
                "score": best_match["score"]
            })

    sorted_results = sorted(results, key=lambda x: -x["score"])
    return sorted_results[:10]


'''if __name__ == "__main__":
    keyword = input("Enter a keyword to search for faculty: ")
    results = find_faculty_by_keyword(keyword)
    
    if not results:
        print("No faculty found for this keyword.")
    else:
        print("\nTop Matching Faculty:\n")
        for r in results:
            print(f"{r['name']}\n  - Keyword: {r['keyword']}\n  - Score: {r['score']:.2f}\n")'''

def get_top_keywords_by_university(univ_name):
    pipeline = [
        {"$match": {"affiliation.name": univ_name}},
        {"$unwind": "$keywords"},
        {"$group": {
            "_id": "$keywords.name",
            "score": {"$sum": "$keywords.score"}
        }},
        {"$sort": {"score": -1}},
        {"$limit": 3}
    ]
    result = list(db.faculty.aggregate(pipeline))
    return [r["_id"] for r in result]

'''if __name__ == "__main__":
    univ_name = input("Enter university name: ")
    keywords = get_top_keywords_by_university(univ_name)
    print("\nTop Keywords:")
    for kw in keywords:
        print("-", kw)'''

#------------------------------Widget 5-------------------------------
#------Add to watchlist------
def add_to_watchlist(faculty_id, name, university, photoUrl):
    db.watchlist.update_one(
        {"id": faculty_id},
        {"$set": {"name": name, "university": university, "photoUrl": photoUrl}},
        upsert=True
    )
#------Remove from watchlist------
def remove_from_watchlist(faculty_id):
    db.watchlist.delete_one({"id": faculty_id})

#------Get watchlist------
def get_watchlist():
    return list(db.watchlist.find({}, {"_id": 0}))

#------Search faculty by name------
def search_faculty_by_name(name):
    query = {"name": {"$regex": name, "$options": "i"}}
    projection = {"id": 1, "name": 1, "photoUrl": 1, "affiliation.name": 1, "_id": 0}
    return list(db.faculty.find(query, projection).limit(10))


#------------------------------Widget 6-------------------------------
def search_papers(query):
    return list(db.publications.find(
        {"title": {"$regex": query, "$options": "i"}},
        {"_id": 0, "id": 1, "title": 1, "venue": 1, "year": 1, "numCitations": 1}
    ).limit(10))

def track_paper(paper):
    db.tracked_papers.update_one(
        {"id": paper["id"]},
        {"$set": paper},
        upsert=True
    )

def untrack_paper(paper_id):
    db.tracked_papers.delete_one({"id": paper_id})

def get_tracked_papers():
    return list(db.tracked_papers.find({}, {"_id": 0}))

#------------------------------Widget 7-------------------------------
def get_active_researchers_by_keyword(keyword):
    pipeline = [
        { "$match": {"keywords.name": {"$regex": keyword, "$options": "i"}} },
        { "$unwind": "$publications" },
        {
            "$lookup": {
                "from": "publications",
                "localField": "publications",
                "foreignField": "id",
                "as": "pubinfo"
            }
        },
        { "$unwind": "$pubinfo" },
        {
            "$group": {
                "_id": {"name": "$name", "photoUrl": "$photoUrl"},
                "recent_year": {"$max": {"$toInt": "$pubinfo.year"}},
                "count": {"$sum": 1}
            }
        },
        { "$sort": {"recent_year": -1, "count": -1} },
        { "$limit": 10 }       
    ]
    cursor = db.faculty.aggregate(pipeline)
    results = list(cursor)
    return [
        {
            "name": r["_id"]["name"],
            "photoUrl": r["_id"]["photoUrl"],
            "recent_year": r["recent_year"],
            "count": r["count"]
        }
        for r in results
    ]