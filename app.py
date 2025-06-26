from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from main import Board, ConnectFourSolver

solver = ConnectFourSolver(Board())
app = FastAPI()


@app.get("/")
async def get_ui():
    return FileResponse("index.html")


@app.post("/create_board")
async def create_board(height: int = 6, width: int = 7, win: int = 4):
    if height < win or width < win:
        raise HTTPException(
            status_code=400,
            detail="The number of tokens in a row required for victory"
                   "must not exceed either dimension of the board."
        )

    global solver
    solver = ConnectFourSolver(Board(height, width, win))
    return solver.board


@app.get("/get_board")
async def get_board():
    return solver.board


@app.post("/reset")
async def reset():
    solver.board.reset()
    return solver.board


@app.post("/undo_move")
async def undo_move():
    solver.board.undo_move()
    return solver.board


@app.get("/get_best_move")
async def get_best_move():
    return solver.get_best_move()


@app.post("/make_move")
async def make_move():
    solver.board.make_move()
    return solver.board
