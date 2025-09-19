from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from services import models, schemas
from services.database import get_db

router = APIRouter(prefix="/admin/teams", tags=["Admin Team Management"])

@router.post("/", response_model=schemas.Team, status_code=201)
def create_team(team: schemas.TeamCreate, db: Session = Depends(get_db)):
    db_team = models.Team(**team.dict())
    db.add(db_team)
    db.commit()
    db.refresh(db_team)
    return db_team

@router.get("/", response_model=List[schemas.Team])
def list_teams(db: Session = Depends(get_db)):
    return db.query(models.Team).all()