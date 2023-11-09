from fastapi import APIRouter, Depends, HTTPException
from fastapi import Request, Form, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import database
import models
import oauth2
import schemas
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.api_route("/signin", methods=["GET", "POST"], response_class=HTMLResponse)
async def signin(request: Request, username: str = Form(None), password: str = Form(None),
                 db: Session = Depends(database.get_db)):
    if request.method == "GET":
        return templates.TemplateResponse("signin.html", {"request": request})
    else:  # POST
        # Check if user exists and password is correct
        user = db.query(models.User).filter(models.User.username == username).first()
        if not user or not oauth2.verify_password(password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
            )
        # User is authenticated, render dashboard
        return templates.TemplateResponse("dashboard.html", {"request": request})


@router.get("/signup", response_class=HTMLResponse)
def signup_form(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})


@router.post("/signup")
def signup(user_in: schemas.UserIn, db: Session = Depends(database.get_db)):
    # Check if user already exists
    user = db.query(models.User).filter(models.User.username == user_in.username).first()
    if user:
        raise HTTPException(status_code=400, detail="Username already taken")

    # Create new user
    hashed_password = oauth2.get_password_hash(user_in.password)
    new_user = models.User(username=user_in.username, password=hashed_password)
    db.add(new_user)
    db.commit()

    return {"message": "User created successfully"}


@router.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = database.get_user(db, form_data.username)
    if not user or not oauth2.verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=400, detail="Incorrect username or password"
        )
    # generate and return JWT token
