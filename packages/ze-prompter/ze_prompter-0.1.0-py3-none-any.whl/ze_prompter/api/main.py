from fastapi import FastAPI, Request, Depends, HTTPException, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
import os

from ..models import init_db, get_db
from ..core.auth import AuthManager
from .routes import auth, prompts, models


app = FastAPI(title="Ze Prompter", description="A library for managing prompt templates with versioning")

# Initialize database
init_db()

# Mount static files and templates
templates_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dashboard", "templates")
templates = Jinja2Templates(directory=templates_dir)

# Include API routes
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(prompts.router, prefix="/api/prompts", tags=["prompts"])
app.include_router(models.router, prefix="/api/models", tags=["models"])


@app.get("/", response_class=HTMLResponse)
async def dashboard_home(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
async def login_post(
        request: Request,
        username: str = Form(...),
        password: str = Form(...),
        db: Session = Depends(get_db)
):
    auth_manager = AuthManager(db)
    user = auth_manager.authenticate_user(username, password)

    if not user:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Invalid username or password"}
        )

    # In a real application, you would set a session cookie here
    return RedirectResponse(url="/dashboard", status_code=302)


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/prompts", response_class=HTMLResponse)
async def prompts_page(request: Request):
    return templates.TemplateResponse("prompts.html", {"request": request})


@app.get("/models", response_class=HTMLResponse)
async def models_page(request: Request):
    return templates.TemplateResponse("models.html", {"request": request})




if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)