**🎓 Academic Navigator** 

**📌Purpose:** Academic Navigator is designed for prospective graduate students and early-career researchers who want to:

* Discover top authors by citation impact
* Explore specialized research areas and trending keywords
* Compare universities on faculty size, citations, and key topics
* Build and manage a watchlist of potential advisors or collaborators
* Identify active researchers in a given domain
* Search for papers by title or keyword and mark “interesting” works for later review

**🔗 Demo:** Check out a live demo here: [Link}(https://mediaspace.illinois.edu/media/t/1_hg4x155y)

**🚀 Installation:** 

 1. Clone the repository
```python
git clone https://github.com/yourusername/academic-navigator.git
cd academic-navigator   
```
 2. Install Python dependencies
```python
pip install -r requirements.txt 
```
3. Start Databases
   
## MYSQL

```python
# on macOS with Homebrew
brew services start mysql
# or on Linux
sudo service mysql start
```
Create the academicworld schema and import the sample data:

```python
CREATE DATABASE academicworld;
USE academicworld;
SOURCE mysql_schema.sql;
SOURCE mysql_data_dump.sql;
```
## MongoDB

```python
mongosh
use academicworld #Assume you already load faculty and publications collections from JSON
show collections
```

## Neo4j

Same as Mongodb, we assume you already have your neo4j account with database added. 

4. Configure environment variables

Create a .env file in the project root:
```python
MYSQL_PWD=your_mysql_root_password
MYNEO4J_PWD=your_neo4j_password
```
5. Run the application
```python
uvicorn main:app --reload
```
#### The dashboard will be available at http://localhost:your_local_host.

**🖥️ Usage:** 

1. Top Authors by Citations:
View a bar chart of the 10 most‐cited faculty across the MySQL database.

2. University Comparison:
Enter two or more university names (e.g., “University of illinois at Urbana Champaign", "Harvard University”) and compare faculty count, total and average citations, plus top keywords.

3. Search Faculty by Keyword: Type a research keyword to find matching faculty from MongoDB, ranked by relevance score. (e.g., machine learning)

4. Keyword Trend Over Time: Enter a keyword to see how many papers per year match that term in the Neo4j graph.(e.g., transformers)

5. Faculty Watchlist: Search faculty by name, add them to your personal watchlist, view and remove entries. 

6. Paper Tracking: Search papers by title or keyword, mark interesting papers, and manage your saved list.

7. Active Researchers: Input a keyword to find top faculty who’ve published most recently on that topic.

**🎨 Design & Architecture** 


####  Frontend:

Single‐page HTML/CSS/JavaScript

Chart.js for dynamic charts

Responsive “widget” panels with unique color themes

#### Backend:

FastAPI (Python) serving JSON endpoints

Pydantic for request validation

Uvicorn ASGI server for high performance

#### Data Stores:

MySQL: relational data on faculty, publications, universities

MongoDB: document collections for faculty profiles & publications

Neo4j: graph database modeling publication‐keyword relationships

Each “widget” corresponds to one or more endpoints that query the appropriate database(s), transform results into JSON, and render them on the front end.


**🛠️ Implementation** 

* FastAPI: lightweight, async-ready, automatic docs (Swagger UI at /docs).

* Pydantic: type‐safe request parsing & response schemas.

* Chart.js: flexible bar, line and custom‐styled charts.

* MongoDB Aggregation Pipelines: $match, $unwind, $group, $sort, $limit to compute top keywords, faculty scores, and active researchers.

* MySQL Queries: JOIN across faculty, publication, faculty_publication, university for citations and comparisons; use LIKE for case‐insensitive partial matches.

* Neo4j Cypher: keyword‐year counting via MATCH (p:Publication)-[:HAS_KEYWORD]->(k:Keyword) and RETURN p.year, COUNT(*).

* Client-side Widgets: modular JavaScript functions for fetch/error handling, DOM updates, and Chart.js instantiation.

**💾 Database Techniques** 
#### 1. Indexing
Used MongoDB indexing to optimize keyword searches:
```python
db.faculty.createIndex({ "keywords.name": 1 })
```

#### 2. Prepared Statements
All MySQL queries are executed using parameterized queries (e.g., cursor.execute(query, params)) in mysql_utils.py, preventing SQL injection and improving efficiency:
```python
cursor.execute("SELECT * FROM faculty WHERE id = %s", (faculty_id,))
```
#### 3. REST API for Accessing Databases
All data access is routed through REST API endpoints built with FastAPI, allowing frontend–backend separation and clean database access for:

* Author citation data (MySQL)
* Watchlist and paper tracking (MongoDB)
* Collaborator graph and keyword trends (Neo4j)

#### 4. Atomic Upserts

MongoDB “watchlist” and “tracked papers” collections use update_one(..., upsert=True) for idempotent updates.

#### 5. Query Optimization

MongoDB: regex search with case‐insensitive indexing on frequently queried fields.
	
Neo4j: label and property indexes on KEYWORD.name for fast trend lookups.



**✨Extra-Credit Capabilities:** 

#### 1. RESTful Full-Stack Design

Converted the entire project to a modern REST API architecture using FastAPI, with all data exposed through endpoints and consumed by a clean index.html frontend. This elevates the project beyond a basic Dash app.

#### 2.	Multi-Database Integration in a Single Widget

University Comparator combines data from both:
* MySQL for faculty count and citations
* MongoDB for keyword analysis

This cross-database aggregation demonstrates advanced system design.

#### 3.	Personal Watchlists & Paper Tracking

Build and manage lists of faculty and papers for later review.


**🤝 Contributions** 

This project was developed and implemented individually by Mina Mehdinia.

* Time Spent: ~60 hours over 2 weeks

* Key Learnings: integrating multiple databases, asynchronous Python development, advanced front-end charting, and aggregation pipelines.



