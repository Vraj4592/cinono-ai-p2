"""RQ worker launcher for Cinono AI P2.

Run this on your GPU server (where CUDA and model dependencies are installed):

    python worker/worker.py

It will start an RQ worker that listens to the 'cinono-jobs' queue and calls
pipeline.orchestrator.process_job(job_prompt, platforms, aspect).
"""
from rq import Worker, Queue, Connection
import redis
import os

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_conn = redis.from_url(redis_url)

if __name__ == "__main__":
    with Connection(redis_conn):
        qs = ["cinono-jobs"]
        worker = Worker(qs)
        print("Starting RQ worker for queues:", qs)
        worker.work()
