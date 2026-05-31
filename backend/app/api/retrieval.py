from fastapi import APIRouter, Query
from backend.retrieval import search

router = APIRouter()


@router.get("/retrieve")
async def retrieve(query: str = Query(..., min_length=3), collection: str = Query("medical_reports"), n_results: int = Query(5, ge=1, le=20)):
    return search(query=query, collection_name=collection, n_results=n_results)
