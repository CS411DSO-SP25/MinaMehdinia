from fastapi import FastAPI
from fastapi import Request

from backend.mysql_utils import (get_top_authors_by_citations, get_university_comparison)
from backend.mongodb_utils import (get_top_keywords_by_university,find_faculty_by_keyword,
                                   add_to_watchlist,remove_from_watchlist,
                                   get_watchlist,search_faculty_by_name,
                                   search_papers, track_paper, untrack_paper, 
                                   get_tracked_papers, get_active_researchers_by_keyword)
from backend.neo4j_utils import (get_keyword_trend)

from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from fastapi.responses import JSONResponse
from fastapi import Query
from pydantic import BaseModel
from fastapi import Query
import logging
logger = logging.getLogger("uvicorn.error")


app = FastAPI()
app.mount("/static", StaticFiles(), name="static")


@app.get("/", response_class=HTMLResponse)
def serve_frontend():
    with open("frontend/index.html", "r") as f:
        return f.read()

# ----------------------------------
# Widget 1:
# ---------------------------------- 
@app.get("/top-authors")
def top_authors():
    return get_top_authors_by_citations()

# ----------------------------------
# Widget 2:
# ---------------------------------- 
class UniversityRequest(BaseModel):
    universities: list[str]

@app.post("/api/university-data")
async def get_university_data(request: UniversityRequest):
    # directly fetch only the rows the user asked for
    rows = get_university_comparison(request.universities)

    # attach top_keywords to each row
    for uni in rows:
        uni["top_keywords"] = get_top_keywords_by_university(uni["university"])

    return JSONResponse(content=rows)

# ----------------------------------
# Widget 3:
# ---------------------------------- 
@app.get("/search-faculty")
def search_faculty(keyword: str = Query(...)):
    return find_faculty_by_keyword(keyword)


# ----------------------------------
# Widget 4:
# ---------------------------------- 
@app.get("/api/keyword-trend")
async def keyword_trend(keyword: str = Query(...)):
    """
    Returns a list of { year: int, count: int } for how many papers
    used `keyword` in each publication year, powered by Neo4j.
    """
    try:
        trend = get_keyword_trend(keyword)
        return JSONResponse(content=trend)
    except Exception as e:
        logger.exception("Error in /api/keyword-trend")
        return JSONResponse(status_code=500, content={"error": str(e)})

# ----------------------------------
# Widget 5
# ---------------------------------- 

@app.get("/api/faculty-search-name")
async def faculty_search_name(name: str = Query(...)):
    return search_faculty_by_name(name)


@app.get("/api/watchlist")
async def read_watchlist():
    return get_watchlist()


@app.post("/api/watchlist")
async def create_watchlist_item(item: dict):
    """
    Expects JSON { id, name, university, photoUrl }
    """
    try:
        add_to_watchlist(
            faculty_id=item["id"],
            name=item["name"],
            university=item["university"],
            photoUrl=item["photoUrl"],
        )
        return JSONResponse(status_code=201, content={"status": "added"})
    except Exception as e:
        logger.exception("Error adding to watchlist")
        return JSONResponse(status_code=500, content={"error": str(e)})


    
@app.delete("/api/watchlist/{faculty_id}")
async def delete_watchlist_item(faculty_id: int):
    try:
        remove_from_watchlist(faculty_id)
        return JSONResponse(content={"status": "removed"})
    except Exception as e:
        logger.exception("Error removing from watchlist")
        return JSONResponse(status_code=500, content={"error": str(e)})
    
# ----------------------------------
# Widget 6: Papers Tracking Endpoints
# ----------------------------------

@app.get("/api/papers-search")
async def papers_search(query: str = Query(...)):
    return search_papers(query)


@app.get("/api/tracked-papers")
async def read_tracked_papers():
    return get_tracked_papers()


@app.post("/api/tracked-papers")
async def create_tracked_paper(item: dict):
    try:
        track_paper(item)
        return JSONResponse(status_code=201, content={"status": "tracked"})
    except Exception as e:
        logger.exception("Error tracking paper")
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.delete("/api/tracked-papers/{paper_id}")
async def delete_tracked_paper(paper_id: int):
    try:
        untrack_paper(paper_id)
        return JSONResponse(content={"status": "untracked"})
    except Exception as e:
        logger.exception("Error untracking paper")
        return JSONResponse(status_code=500, content={"error": str(e)})
    
# ------------------------------
# Widget 7: Active Researchers
# ------------------------------
@app.get("/api/active-researchers")
async def active_researchers(keyword: str = Query(...)):
    """
    Returns top faculty who’ve published most recently on `keyword`.
    """
    try:
        results = get_active_researchers_by_keyword(keyword)
        return JSONResponse(content=results)
    except Exception as e:
        logger.exception("Error in /api/active-researchers")
        return JSONResponse(status_code=500, content={"error": str(e)})