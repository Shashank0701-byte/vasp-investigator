import os

from sqlalchemy import JSON, Column, String, create_engine, select
from sqlalchemy.orm import Session, declarative_base

Base = declarative_base()


class CaseRecord(Base):
    __tablename__ = "cases"
    id = Column(String(40), primary_key=True)
    created_at = Column(String(40), nullable=False, index=True)
    payload = Column(JSON, nullable=False)


class CaseStore:
    def __init__(self, url=None):
        url = url or os.getenv("DATABASE_URL", "sqlite:///./investigations.db")
        self.engine = create_engine(
            url,
            connect_args={"check_same_thread": False}
            if url.startswith("sqlite")
            else {},
        )
        Base.metadata.create_all(self.engine)

    def save(self, case):
        with Session(self.engine) as session:
            session.add(
                CaseRecord(id=case["id"], created_at=case["created_at"], payload=case)
            )
            session.commit()

    def get(self, case_id):
        with Session(self.engine) as session:
            record = session.get(CaseRecord, case_id)
            return record.payload if record else None

    def list(self):
        with Session(self.engine) as session:
            records = session.scalars(
                select(CaseRecord).order_by(CaseRecord.created_at.desc()).limit(100)
            )
            return [
                {
                    "id": r.id,
                    "title": r.payload["title"],
                    "created_at": r.created_at,
                    "target": r.payload["analysis"]["target"],
                    "chain": r.payload["analysis"]["chain"],
                    "mode": r.payload["analysis"]["mode"],
                }
                for r in records
            ]
