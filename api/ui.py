from fastapi.responses import HTMLResponse
from pathlib import Path
from api.app import app

ROOT = Path(__file__).resolve().parents[1]
INDEX = (ROOT / "api" / "static" / "index.html").read_text()


@app.get("/", response_class=HTMLResponse)
def web_index():
    return HTMLResponse(content=INDEX, status_code=200)


@app.get('/job_status')
def job_status(job_id: str):
    # look for runs/run_<id>/meta.json
    from pathlib import Path
    import json
    runs = Path(__file__).resolve().parents[2] / 'runs'
    candidate = None
    for p in runs.glob('run_*'):
        meta = p / 'meta.json'
        if meta.exists():
            data = json.loads(meta.read_text())
            if data.get('run_id') == job_id:
                candidate = meta
                break
    if not candidate:
        return {"status":"queued","log":"No run file yet for job."}
    data = json.loads(candidate.read_text())
    status = 'complete'
    # check uploads
    return {"status": status, "log": json.dumps(data, indent=2)}
