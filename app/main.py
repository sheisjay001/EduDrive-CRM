from fastapi import FastAPI

# Minimal app for testing deployment
app = FastAPI(title="EduDrive CRM API", version="0.1.0")

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "EduDrive CRM API"}

# TODO: Gradually add back routes and middleware
