import uvicorn
from fastapi import FastAPI

from routers import user
from fastapi.responses import RedirectResponse

app = FastAPI()

app.include_router(user.router)


@app.get("/")
def read_root():
    return RedirectResponse(url="/signin")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001)
# change the port number as needed
