from fastapi import FastAPI, Depends, HTTPException, Form
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from database import Base, engine, get_db
from schemas import WorkerResponse, WorkerCreate , WorkerUpdate
from services import WorkerManager
from typing import Optional
from fastapi.templating import Jinja2Templates
from fastapi import Request
import qrcode
import qrcode.image.svg
import io
from fastapi.responses import StreamingResponse, RedirectResponse
from datetime import date, timedelta
from starlette.middleware.sessions import SessionMiddleware
from passlib.context import CryptContext
from dotenv import load_dotenv
import os

app = FastAPI(title="Worker Verification System")
Base.metadata.create_all(bind=engine)
template = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# handling authetication
load_dotenv()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD_HASH = pwd_context.hash(os.getenv("ADMIN_PASSWORD"))
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
VERIFY_URL = os.getenv("VERIFY_URL")

# for protecting routes
def get_current_admin(request: Request):
    if not request.session.get("user"):
        raise HTTPException(status_code=307, headers={"Location": "/login"})
    return request.session["user"]

def require_admin_api(request: Request):
    if not request.session.get("user"):
        raise HTTPException(status_code=401, detail="Not authenticated")
    return request.session["user"]

@app.post("/add_worker", response_model=WorkerResponse)
def worker(worker:WorkerCreate,  db: Session = Depends(get_db), admin: str = Depends(require_admin_api)):
    manager = WorkerManager(db)
    return manager.create_worker(worker)


@app.get("/workers/add", )
def add_worker_page(request: Request, admin: str = Depends(get_current_admin)):
    return template.TemplateResponse(request=request, name="add_worker.html", context={
        "user_name": admin
    })

@app.get("/workers/{worker_id}/edit")
def edit_worker_page(worker_id: int, request: Request, db: Session = Depends(get_db), admin: str = Depends(get_current_admin)):
    manager = WorkerManager(db)
    worker = manager.get_worker(worker_id)
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
    return template.TemplateResponse(request=request, name="update_worker.html", context={
        "worker": worker,
        "user_name": admin,
          
    })
    
@app.get("/verify", response_model=list[WorkerResponse])
def verify_worker(name: Optional[str] = None, 
                    card_number: Optional[str] = None, 
                    iqama_no: Optional[str] = None,
                    db: Session = Depends(get_db)):
    manager = WorkerManager(db)
    return manager.verify_worker(name=name, card_number=card_number, iqama_no=iqama_no)
    # if not worker:
    #     return HTTPException(status_code = 404, detail="Worker/Operator Not Found")
@app.get("/worker/{worker_id}", response_model=WorkerResponse)
def read_worker(worker_id: int, db: Session = Depends(get_db), admin: str = Depends(require_admin_api)):
    manager = WorkerManager(db)
    return manager.get_worker(worker_id)

@app.patch("/update/{worker_id}", response_model=WorkerResponse)
def update_worker(worker_id: int, worker_data: WorkerUpdate, db: Session = Depends(get_db), admin: str = Depends(require_admin_api)):
    manager = WorkerManager(db)
    return manager.update_worker(worker_id, worker_data)

@app.get("/workers/{worker_id}/view")
def view_worker_page(worker_id: int, request: Request, db: Session = Depends(get_db), admin: str = Depends(get_current_admin)):
    manager = WorkerManager(db)
    worker = manager.get_worker(worker_id)
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
    return template.TemplateResponse(request=request, name="view_worker.html", context={
        "worker": worker,
        "user_name": admin,
        "verify_url": VERIFY_URL 
    })

@app.delete("/worker/{worker_id}")
def delete_worker(worker_id: int, db: Session = Depends(get_db), admin: str = Depends(require_admin_api)):
    manager = WorkerManager(db)
    return manager.delete_worker(worker_id)

@app.get("/verify-page")
def verify_page(request: Request):
    return template.TemplateResponse(request=request, name="verify.html")

@app.get("/")
def dashboard_page(request: Request, db: Session = Depends(get_db), admin: str = Depends(get_current_admin)):
    manager = WorkerManager(db)
    all_workers = manager.get_all_worker()
    soon_cutoff = date.today() + timedelta(days=30)
    return template.TemplateResponse(request=request, name="dashboard.html", context={
        "total_workers": len(all_workers),
        "active_count": len([w for w in all_workers if w.status == "active"]),
        "cancelled_count": len([w for w in all_workers if w.status == "cancelled"]),
        "suspended_count": len([w for w in all_workers if w.status == "suspended"]),
        "expired_count": len([w for w in all_workers if w.is_expired]),
        "expiring_soon_count": len([w for w in all_workers if not w.is_expired and w.expiry_date <= soon_cutoff]),
        
    })

@app.get("/workers")
def workers_page(request: Request,
                db: Session = Depends(get_db),
                admin: str = Depends(get_current_admin)):
    manager = WorkerManager(db)
    all_workers = manager.get_all_worker()
    return template.TemplateResponse(request=request, name="workers.html", context={
        "workers": all_workers,
        "user_name": admin   # abhi ke liye hardcoded, baad me login system se aayega
    })

@app.get("/workers/search")
def search_workers(q: str = None, status: str = None, db: Session = Depends(get_db), admin: str = Depends(require_admin_api)):
    manager = WorkerManager(db)
    workers = manager.search_workers(q=q, status=status)
    return workers


@app.get("/qr-code/png")
def qr_code_png(admin: str = Depends(get_current_admin)):
    img = qrcode.make(VERIFY_URL)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return StreamingResponse(buffer, media_type="image/png")

@app.get("/qr-code/svg")
def qr_code_svg(admin: str = Depends(get_current_admin)):
    factory = qrcode.image.svg.SvgImage
    img = qrcode.make(VERIFY_URL, image_factory=factory)
    buffer = io.BytesIO()
    img.save(buffer)
    buffer.seek(0)
    return StreamingResponse(buffer, media_type="image/svg+xml")


@app.get("/login")
def login_page(request: Request):
    return template.TemplateResponse(request=request, name="login.html", context={})

@app.post("/login")
def login_submit(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == ADMIN_USERNAME and pwd_context.verify(password, ADMIN_PASSWORD_HASH):
        request.session["user"] = username
        return RedirectResponse(url="/", status_code=303)
    return template.TemplateResponse(request=request, name="login.html", context={
        "error": "Invalid username or password"
    })

@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)

