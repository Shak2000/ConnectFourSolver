from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os

from main import Board, ConnectFourSolver

solver = ConnectFourSolver(Board())
app = FastAPI()


class BoardConfig(BaseModel):
    height: int
    width: int
    win: int


class MoveRequest(BaseModel):
    column: int


@app.get("/")
async def get_ui():
    return FileResponse("index.html")


@app.get("/styles.css")
async def get_styles():
    return FileResponse("styles.css")


@app.get("/script.js")
async def get_script():
    return FileResponse("script.js")


@app.post("/create_board")
async def create_board(config: BoardConfig):
    if config.height < config.win or config.width < config.win:
        raise HTTPException(
            status_code=400,
            detail="The number of tokens in a row required for victory "
                   "must not exceed either dimension of the board."
        )

    global solver
    solver = ConnectFourSolver(Board(config.height, config.width, config.win))
    return solver.board.__dict__


@app.get("/get_board")
async def get_board():
    return solver.board.__dict__


@app.post("/reset")
async def reset():
    solver.board.reset()
    return solver.board.__dict__


@app.post("/undo_move")
async def undo_move():
    if not solver.board.undo_move():
        raise HTTPException(status_code=400, detail="No moves to undo")
    return solver.board.__dict__


@app.get("/get_best_move")
async def get_best_move():
    best_move = solver.get_best_move()
    if best_move is None:
        raise HTTPException(status_code=400, detail="No valid moves available")
    return best_move


@app.post("/make_move")
async def make_move(move: MoveRequest):
    if not solver.board.is_valid_move(move.column):
        raise HTTPException(status_code=400, detail="Invalid move")

    result = solver.board.make_move(move.column)

    # Update game over status based on result
    board_dict = solver.board.__dict__
    if result is not None:
        board_dict['game_over'] = True
        board_dict['winner'] = result
    else:
        board_dict['game_over'] = False
        board_dict['winner'] = None

    return board_dict
