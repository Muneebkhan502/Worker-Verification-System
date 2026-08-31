from schemas import WorkerCreate, WorkerResponse, WorkerUpdate
from sqlalchemy import select, or_
from models import Worker
from fastapi import HTTPException
from typing import Optional
class WorkerManager():
    def __init__(self, db):
        self.db = db

    def create_worker(self, worker: WorkerCreate,):
        existing_card = self.db.execute(select(Worker).where(Worker.card_number == worker.card_number)).scalars().first()
        if existing_card:
            raise HTTPException(status_code=400, detail="This card number is already registered!")
        
        existing_iqama = self.db.execute(select(Worker).where(Worker.iqama_no == worker.iqama_no)).scalars().first()
        if existing_iqama:
            raise HTTPException(status_code=400, detail="This iqama number is already registered!")
        
        try:
            new_worker = Worker(
            card_number=worker.card_number,
            name=worker.name,
            iqama_no=worker.iqama_no,
            company_name=worker.company_name,
            trade_course=worker.trade_course,
            issued_date=worker.issued_date,
            expiry_date=worker.expiry_date,
            status=worker.status
            )
            self.db.add(new_worker)
            self.db.commit()
            self.db.refresh(new_worker)
            return new_worker
        except HTTPException(status_code=500, detail="Worker data has not been saved"):
                return self.db.rollback()

    def verify_worker(self,name: Optional[str] = None, card_number: Optional[str] = None, iqama_no: Optional[str] = None):
        query = select(Worker)  # to get all workers
        conditions = []
        if name:
            conditions.append(Worker.name.ilike(f"%{name}%"))
        if card_number:
            conditions.append(Worker.card_number == card_number)
        if iqama_no:
            conditions.append(Worker.iqama_no == iqama_no)

        if conditions:
            query = query.where(or_(*conditions))
        return self.db.execute(query).scalars().all()

    def get_all_worker(self):
        workers = self.db.execute(select(Worker)).scalars().all()
        return workers
    
    def get_worker(self, worker_id: int):
        #  Search Worker With Specific ID 
        worker = self.db.execute(select(Worker).where(Worker.id == worker_id)).scalars().first()
        if not worker:
            raise HTTPException(status_code=404, detail="Worker Not Found!")
        return worker

    def update_worker(self, worker_id: int, worker_data:WorkerUpdate):
        #check existance
        worker = self.db.execute(select(Worker).where(Worker.id == worker_id)).scalars().first()
        if not worker:
            raise HTTPException(status_code=404, detail="Worker does not found!")
        # just those field which user sent
        update_data = worker_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(worker, key, value)

        self.db.commit()
        self.db.refresh(worker)
        return worker

   

    def delete_worker(self, worker_id: int):
        # 1. Check Existance
        worker = self.db.execute(select(Worker).where(Worker.id == worker_id)).scalars().first()
        
        if not worker:
            raise HTTPException(status_code=404, detail="Worker Does Not Found!")

        
        self.db.delete(worker)
        self.db.commit()

        return {"status": "success", "message": f"Worker ID {worker_id} successfully delete."}

    def search_workers(self, q: str = None, status: str = None):
        query = select(Worker)

        if q:
            query = query.where(or_(
                Worker.name.ilike(f"%{q}%"),
                Worker.card_number == q,
                Worker.iqama_no == q,
                Worker.company_name.ilike(f"%{q}%")
            ))

        if status:
            query = query.where(Worker.status.ilike(status))

        return self.db.execute(query).scalars().all()