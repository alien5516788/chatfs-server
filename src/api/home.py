from fastapi import APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse

router = APIRouter()


@router.get("/home")
def home():
    return RedirectResponse(url="/")


@router.get("/")
def server():
    with open("src/notice.html") as notice:
        return HTMLResponse(notice.read())
