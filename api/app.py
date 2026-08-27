from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import redis
from rq import Queue
import os

app = FastAPI(title="Cinono AI Orchestrator")

# Redis / RQ setup
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_conn = redis.from_url(redis_url)
queue = Queue("cinono-jobs", connection=redis_conn)

class GenerateRequest(BaseModel):
    prompt: str
    platforms: list[str] = ["tiktok", "youtube"]
    aspect: str = "9:16"
    job_name: str | None = None

@app.post("/generate")
def generate(req: GenerateRequest):
    """Enqueue a generation job. Returns job id immediately.
    The worker will process the job on a GPU-equipped machine.
    """
    job = queue.enqueue("pipeline.orchestrator.process_job", req.prompt, req.platforms, req.aspect, job_timeout=36000)
    return {"job_id": job.get_id(), "status": "queued"}

@app.get("/health")
def health():
    return {"status": "ok"}
