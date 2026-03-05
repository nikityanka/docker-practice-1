from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, BigInteger
from sqlalchemy.orm import declarative_base, sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@db:5432/scores_db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Score(Base):
    __tablename__ = "scores"

    id = Column(Integer, primary_key=True, index=True)
    player = Column(String, nullable=False, index=True)
    game = Column(String, nullable=False, index=True)
    score = Column(BigInteger, nullable=False)


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Game Leaderboard API")


class ScoreCreate(BaseModel):
    player: str
    game: str
    score: int


SEED_DATA = [
    {"player": "madmax",   "game": "digdug",   "score": 751300},
    {"player": "Misha",    "game": "digdug",   "score": 540000},
    {"player": "shadow99", "game": "digdug",   "score": 430200},
    {"player": "retro_k",  "game": "digdug",   "score": 310500},
    {"player": "neon_ace", "game": "digdug",   "score": 275000},
    {"player": "madmax",   "game": "pacman",   "score": 980000},
    {"player": "Misha",    "game": "pacman",   "score": 820000},
    {"player": "ghost_x",  "game": "pacman",   "score": 760000},
    {"player": "retro_k",  "game": "galaga",   "score": 650000},
    {"player": "neon_ace", "game": "galaga",   "score": 520000},
    {"player": "shadow99", "game": "galaga",   "score": 490000},
]


@app.on_event("startup")
def seed_database():
    db = SessionLocal()
    try:
        if db.query(Score).count() == 0:
            db.bulk_insert_mappings(Score, SEED_DATA)
            db.commit()
            print(f"[seed] Inserted {len(SEED_DATA)} records")
        else:
            print("[seed] Database already has data, skipping")
    finally:
        db.close()


@app.post("/scores", status_code=201)
def add_score(payload: ScoreCreate):
    db = SessionLocal()
    try:
        record = Score(player=payload.player, game=payload.game, score=payload.score)
        db.add(record)
        db.commit()
        db.refresh(record)
        return {"id": record.id, "player": record.player, "game": record.game, "score": record.score}
    finally:
        db.close()


@app.get("/scores/top")
def get_top_scores(
    game: str = Query(..., description="Game name"),
    limit: int = Query(10, ge=1, le=100)
):
    db = SessionLocal()
    try:
        rows = (
            db.query(Score)
            .filter(Score.game == game)
            .order_by(Score.score.desc())
            .limit(limit)
            .all()
        )
        return [
            {"rank": i + 1, "player": r.player, "game": r.game, "score": r.score}
            for i, r in enumerate(rows)
        ]
    finally:
        db.close()


@app.get("/scores/player/{name}")
def get_player_scores(name: str):
    db = SessionLocal()
    try:
        rows = (
            db.query(Score)
            .filter(Score.player == name)
            .order_by(Score.score.desc())
            .all()
        )
        if not rows:
            raise HTTPException(status_code=404, detail=f"No scores found for player '{name}'")
        return [{"game": r.game, "score": r.score} for r in rows]
    finally:
        db.close()
