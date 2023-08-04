import sqlite3
from fastapi import FastAPI, HTTPException, status, Query, Request
from sqlmodel import select, Session

import db_internal
from models import User, Farmer, Practice
# from utils import get_practice, practice_data, process_records

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    db_internal.create_db()


@app.get("/users", response_model=list[User])
async def get_users():
    with Session(db_internal.engine) as session:
        statement = select(User)
        results = session.execute(statement)
        results = list(i[0] for i in results.all())
    if len(results) == 0:
        return []
    return results


@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int):
    with Session(db_internal.engine) as session:
        row = session.get(User, user_id)
        if not row:
            raise HTTPException(status_code=404, detail="user_id not found")
        session.delete(row)
        session.commit()
        return


@app.post("/users", status_code=status.HTTP_201_CREATED, response_model=User)
async def create_user(user: User):
    with Session(db_internal.engine) as session:
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

# ---------------------------
@app.get("/farmers/{user_id}")
async def get_farmers_by_userid(user_id:int, year: str = Query(None), season: str = Query(None)):
    with Session(db_internal.engine) as session:
        stmt =  session.query(Farmer, Practice).join(Practice, Farmer.id == Practice.farmer_id).filter(Farmer.user_id == user_id)
        if year:
            stmt =  stmt.filter(Farmer.year == year)
        if season:
            stmt =  stmt.filter(Farmer.season == season)
        results = session.execute(stmt)
        results = list(i for i in results.all())        
    if len(results) == 0:
        return []
    return results



"""
sample payload : {
        "Farmer": {           
            "is_tillage": false,
            "is_crop": true,
            "year": 1998,
            "season": "test",
            "user_id": 2
        },
        "Practice": {
            "crop": "test",            
            "tillage_depth": null,
            "tilage_type": null,           
            "crop_variety": "test"
        }
    }
"""
@app.post("/farmers/")
async def create_farmers(request: Request):
    with Session(db_internal.engine) as session:
        data = await request.json()
        farmer = data.get('Farmer')
        print(farmer)
        data_far= Farmer(**farmer)
        session.add(data_far)
        session.flush()
        session.refresh(data_far)
        new_farmer = data_far
        print(new_farmer.id)
        
        practice = data.get('Practice')
        practice['farmer_id'] = new_farmer.id
        data_pra= Practice(**practice)
        session.add(data_pra)        
        session.commit()

        stmt =  session.query(Farmer, Practice).join(Practice, Farmer.id == Practice.farmer_id).filter(Farmer.id == new_farmer.id)
        results = session.execute(stmt)
        results = list(i for i in results.all())        
        if len(results) == 0:
            return []
        return results
