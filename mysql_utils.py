from dotenv import load_dotenv
import mysql.connector, os


load_dotenv()
def get_mysql_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.getenv("MYSQL_PWD"),
        database="academicworld"
    )

def get_top_authors_by_citations():
    conn = get_mysql_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT f.name, SUM(p.num_citations) AS total_citations
        FROM faculty f
        JOIN faculty_publication fp ON f.id = fp.faculty_id
        JOIN publication p ON p.id = fp.publication_id
        GROUP BY f.id
        ORDER BY total_citations DESC
        LIMIT 10;
    """
    cursor.execute(query)
    result = cursor.fetchall()
    conn.close()
    return result


def get_university_comparison(universities: list[str]):
    conn = get_mysql_connection()
    cursor = conn.cursor(dictionary=True)

    patterns = [f"%{u.lower().strip()}%" for u in universities]
    where_clauses = " OR ".join("LOWER(u.name) LIKE %s" for _ in patterns)

    query = f"""
    SELECT u.name AS university, 
           COUNT(DISTINCT f.id) AS faculty_count, 
           COALESCE(SUM(p.num_citations), 0) AS total_citations
    FROM university u
    LEFT JOIN faculty f ON u.id = f.university_id
    LEFT JOIN faculty_publication fp ON f.id = fp.faculty_id
    LEFT JOIN publication p ON p.id = fp.publication_id
    WHERE {where_clauses}
    GROUP BY u.id;
    """

    cursor.execute(query, patterns)
    raw = cursor.fetchall()
    conn.close()

    processed = []
    for r in raw:
        total = int(r["total_citations"] or 0)
        fac   = int(r["faculty_count"]  or 0)
        avg   = round(total / fac, 2) if fac else 0.0

        processed.append({
            "university":     r["university"],
            "faculty_count":  fac,
            "total_citations": total,
            "avg_citations":  avg
        })

    return processed


