# app/routes/reports.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db
from datetime import date

router = APIRouter(prefix="/reportes", tags=["Reportes"])

@router.post("/", response_model=schemas.ReporteOut)
def crear_reporte(reporte: schemas.ReporteCreate, db: Session = Depends(get_db)):
    # Use model_dump() for Pydantic v2 compatibility
    nuevo = models.Reporte(**reporte.model_dump(exclude_unset=True))
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@router.get("/", response_model=list[schemas.ReporteOut])
def listar_reportes(db: Session = Depends(get_db)):
    return db.query(models.Reporte).all()
