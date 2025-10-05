from fastapi import FastAPI, File, UploadFile, Form, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Optional, List
import shutil
import os
from datetime import datetime
import uuid

from database import SessionLocal, engine, Base
import models
import schemas

# Импорт для генерации карты
import pandas as pd
import folium
from folium.plugins import HeatMap
import requests

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/static", StaticFiles(directory="static"), name="static")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ========== ГЕНЕРАЦИЯ КАРТЫ ==========
def generate_russia_map():
    """Генерация карты из CSV файла"""
    try:
        # Импортируем функции из вашего скрипта
        from generate_map import create_stylish_map, REGION_COORDINATES
        
        # Читаем CSV
        df = pd.read_csv('russian_regions_81.csv')
        df['Колво на 100к'] = (df['Кол-во заявок'] / df['Население']) * 100000
        df['latitude'] = df['Регион'].map(lambda x: REGION_COORDINATES.get(x, [55.7558, 37.6173])[0])
        df['longitude'] = df['Регион'].map(lambda x: REGION_COORDINATES.get(x, [55.7558, 37.6173])[1])
        
        # Создаем карту
        stylish_map = create_stylish_map(df)
        stylish_map.save('static/stylish_russia_map.html')
        print("✅ Карта успешно сгенерирована в static/stylish_russia_map.html")
        return True
    except Exception as e:
        print(f"❌ Ошибка генерации карты: {e}")
        return False


# ========== ГЛАВНАЯ СТРАНИЦА ==========
@app.get("/", response_class=HTMLResponse)
async def home():
    try:
        with open("templates/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Ошибка: index.html не найден в templates/</h1>", status_code=500)


# ========== API ENDPOINTS ==========

@app.get("/api/statistics")
def get_statistics(db: Session = Depends(get_db)):
    active = db.query(models.MissingPerson).filter(models.MissingPerson.status == "active").count()
    found = db.query(models.MissingPerson).filter(models.MissingPerson.status == "found").count()
    volunteers = db.query(models.Volunteer).filter(models.Volunteer.status == "active").count()
    
    return {
        "active_searches": active,
        "found_persons": found,
        "total_volunteers": volunteers,
        "regions_covered": 83
    }


@app.post("/api/volunteers/register", response_model=schemas.VolunteerResponse)
async def register_volunteer(
    name: str = Form(...),
    role: str = Form(...),
    description: str = Form(...),
    experience_years: int = Form(...),
    operations_count: int = Form(...),
    emoji_icon: str = Form("👤"),
    photo: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    photo_url = None
    if photo:
        ext = photo.filename.split(".")[-1]
        filename = f"{uuid.uuid4()}.{ext}"
        path = f"uploads/volunteers/{filename}"
        with open(path, "wb") as f:
            shutil.copyfileobj(photo.file, f)
        photo_url = f"/{path}"
    
    volunteer = models.Volunteer(
        name=name, role=role, description=description,
        experience_years=experience_years, operations_count=operations_count,
        emoji_icon=emoji_icon, photo_url=photo_url, created_at=datetime.utcnow()
    )
    db.add(volunteer)
    db.commit()
    db.refresh(volunteer)
    return volunteer


@app.get("/api/volunteers", response_model=List[schemas.VolunteerResponse])
def get_volunteers(db: Session = Depends(get_db)):
    return db.query(models.Volunteer).filter(models.Volunteer.status == "active").all()


@app.post("/api/missing-persons/create", response_model=schemas.MissingPersonResponse)
async def create_missing(
    full_name: str = Form(...),
    age: int = Form(...),
    gender: str = Form(...),
    last_seen_location: str = Form(...),
    last_seen_date: str = Form(...),
    description: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    contact_name: str = Form(...),
    contact_phone: str = Form(...),
    contact_email: Optional[str] = Form(None),
    height: Optional[int] = Form(None),
    weight: Optional[int] = Form(None),
    clothing: Optional[str] = Form(None),
    distinguishing_features: Optional[str] = Form(None),
    photo: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    photo_url = None
    if photo:
        ext = photo.filename.split(".")[-1]
        filename = f"{uuid.uuid4()}.{ext}"
        path = f"uploads/missing_persons/{filename}"
        with open(path, "wb") as f:
            shutil.copyfileobj(photo.file, f)
        photo_url = f"/{path}"
    
    person = models.MissingPerson(
        full_name=full_name, age=age, gender=gender,
        last_seen_location=last_seen_location,
        last_seen_date=datetime.strptime(last_seen_date, "%Y-%m-%d"),
        description=description, latitude=latitude, longitude=longitude,
        contact_name=contact_name, contact_phone=contact_phone,
        contact_email=contact_email, height=height, weight=weight,
        clothing=clothing, distinguishing_features=distinguishing_features,
        photo_url=photo_url, status="active", created_at=datetime.utcnow()
    )
    db.add(person)
    db.commit()
    db.refresh(person)
    return person


@app.get("/api/missing-persons", response_model=List[schemas.MissingPersonResponse])
def get_missing(db: Session = Depends(get_db)):
    return db.query(models.MissingPerson).order_by(models.MissingPerson.created_at.desc()).all()


@app.get("/api/map/markers")
def get_map_markers(db: Session = Depends(get_db)):
    """Получить метки активных пропавших для карты"""
    active_persons = db.query(models.MissingPerson).filter(
        models.MissingPerson.status == "active"
    ).all()
    
    markers = []
    for person in active_persons:
        markers.append({
            "id": person.id,
            "latitude": person.latitude,
            "longitude": person.longitude,
            "name": person.full_name,
            "age": person.age,
            "gender": person.gender,
            "last_seen": person.last_seen_location,
            "photo_url": person.photo_url,
            "description": person.description,
            "contact_phone": person.contact_phone
        })
    
    return {"markers": markers}


@app.get("/api/generate-map")
def regenerate_map():
    """Перегенерировать карту"""
    success = generate_russia_map()
    if success:
        return {"status": "success", "message": "Карта успешно сгенерирована"}
    return {"status": "error", "message": "Ошибка генерации карты"}


@app.get("/health")
def health():
    return {"status": "ok"}


# Генерация карты при запуске сервера
@app.on_event("startup")
async def startup_event():
    print("🚀 Запуск сервера...")
    print("📍 Генерация карты России...")
    generate_russia_map()