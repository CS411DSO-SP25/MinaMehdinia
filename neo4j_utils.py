from neo4j import GraphDatabase
from dotenv import load_dotenv
import os

load_dotenv()

uri = "bolt://localhost:7687"
username = "neo4j"
password = os.getenv("MYNEO4J_PWD")

driver = GraphDatabase.driver(uri, auth=(username, password))


def get_keyword_trend(keyword):
    with driver.session(database="academicworld") as session:
        result = session.run("""
            MATCH (p:PUBLICATION)-[:LABEL_BY]->(k:KEYWORD)
            WHERE toLower(k.name) CONTAINS toLower($kw)
            RETURN p.year AS year, COUNT(*) AS count
            ORDER BY year
        """, kw=keyword)
        
        return [{"year": r["year"], "count": r["count"]} for r in result]

'''        # Example usage:
if __name__ == "__main__":
    trend = get_keyword_trend("machine learning")
    for row in trend:
        print(row)'''
