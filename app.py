from fastapi import FastAPI, Depends, Request, Form, status
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates
from sqlalchemy.orm import Session
import datetime
import models
from database import SessionLocal, engine

# Create tables in the database
models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory='templates')

app = FastAPI()

# Helper function to access the database
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get('/')
def home(request: Request, db: Session = Depends(get_db)):
    todos = db.query(models.Todo).all()

    return templates.TemplateResponse('base.html', {
        'request': request,
        'todo_list': todos,
    })

# Ellipsis "..." means that the field is required
@app.post('/add')
def add(request: Request, title: str = Form(...), description: str = Form(None), db: Session = Depends(get_db)):
    new_todo = models.Todo(title=title, description=description)
    db.add(new_todo)
    db.commit()

    url = app.url_path_for('home')
    return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)


@app.get('/update/{todo_id}')
def update(request: Request, todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    todo.complete = not todo.complete
    todo.modified_at = datetime.datetime.utcnow()
    db.commit()

    url = app.url_path_for('home')
    return RedirectResponse(url=url, status_code=status.HTTP_302_FOUND)


@app.get('/delete/{todo_id}')
def update(request: Request, todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    db.delete(todo)
    db.commit()

    url = app.url_path_for('home')
    return RedirectResponse(url=url, status_code=status.HTTP_302_FOUND)
