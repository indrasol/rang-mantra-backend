from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.db.supabase_db import get_supabase_client, safe_supabase_operation
from datetime import datetime

router = APIRouter()

class StatsResponse(BaseModel):
    total_users: int
    total_memories: int
    last_updated: str

@router.get("/", response_model=StatsResponse)
async def get_stats():
    """
    Get the latest statistics from colorize_events_totals table.
    Returns total users and total memories processed.
    """
    try:
        supabase = get_supabase_client()
        
        # Fetch totals from the new table
        def fetch_stats():
            response = supabase.table("colorize_events_totals")\
                .select("total_unique_users, total_memories")\
                .limit(1)\
                .execute()
            return response
        
        result = await safe_supabase_operation(
            fetch_stats,
            "Failed to fetch stats from database"
        )
        
        if not result.data:
            # Return default values if no data exists
            return StatsResponse(
                total_users=0,
                total_memories=0,
                last_updated=datetime.now().isoformat()
            )
        
        record = result.data[0]
        
        return StatsResponse(
            total_users=record.get("total_unique_users", 0),
            total_memories=record.get("total_memories", 0),
            last_updated=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve stats: {str(e)}"
        )
