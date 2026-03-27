from fastapi import APIRouter, Query, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime

router = APIRouter(prefix="/db", tags=["db"])

from fastapi import Request, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from database.session import get_db

@router.post("/query")
async def exec_query(req: Request, db: Session = Depends(get_db)):
    body = await req.json()
    query = body.get("query")

    if not query:
        raise HTTPException(status_code=400, detail="Missing SQL query")

    try:
        result = db.execute(text(query))
        
        if result.returns_rows:
            rows = [dict(row._mapping) for row in result.fetchall()]
            return rows
        
        db.commit()
        return {"status": "ok"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))