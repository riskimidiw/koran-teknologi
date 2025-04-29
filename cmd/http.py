"""HTTP server handler for Koran Teknologi."""

from datetime import datetime, timedelta
from typing import List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from services.koran_service import KoranService
from utils.logger import setup_logger

logger = setup_logger(__name__)
app = FastAPI(
    title="Koran Teknologi API",
    description="API for fetching and sending tech blog posts to Telegram",
    version="1.0.0",
)
service = KoranService()


class SendPostsRequest(BaseModel):
    days: Optional[int] = Field(
        default=1, description="Number of days to look back for posts"
    )
    dry_run: Optional[bool] = Field(
        default=False, description="If true, returns posts without sending to Telegram"
    )


class BlogPostResponse(BaseModel):
    title: str
    source: str
    url: str
    date: datetime


class SendPostsResponse(BaseModel):
    status: str
    message: str
    posts: Optional[List[BlogPostResponse]] = None


class HealthResponse(BaseModel):
    status: str = "healthy"
    version: str = "1.0.0"


@app.post("/send-posts", response_model=SendPostsResponse, tags=["posts"])
async def send_posts(request: SendPostsRequest) -> SendPostsResponse:
    """Send new tech blog posts to Telegram.

    Args:
        request: SendPostsRequest containing days to look back and dry run flag

    Returns:
        JSON response with status and either sent posts confirmation or list of posts for dry run

    Raises:
        HTTPException: If there's an error processing the request
    """
    try:
        since = datetime.now() - timedelta(days=request.days)
        posts = await service.fetch_new_posts(since=since)

        if not posts:
            return SendPostsResponse(
                status="success", message="No new posts found", posts=[]
            )

        if request.dry_run:
            return SendPostsResponse(
                status="success",
                message=f"Found {len(posts)} posts (dry run)",
                posts=[
                    BlogPostResponse(
                        title=post.title,
                        source=post.source,
                        url=post.url,
                        date=post.date,
                    )
                    for post in posts
                ],
            )

        await service.send_posts(posts)
        return SendPostsResponse(
            status="success",
            message=f"Successfully sent {len(posts)} posts to Telegram",
            posts=[
                BlogPostResponse(
                    title=post.title, source=post.source, url=post.url, date=post.date
                )
                for post in posts
            ],
        )

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(
            status_code=500, detail={"status": "error", "message": str(e)}
        )


@app.get("/health", response_model=HealthResponse, tags=["system"])
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse()


def run_http(host: str = "0.0.0.0", port: int = 8000) -> None:
    """Run the HTTP server."""
    logger.info(f"Starting Koran Teknologi HTTP server on {host}:{port}...")
    uvicorn.run(app, host=host, port=port, log_level="info")
