from aiogram.fsm.state import StatesGroup, State


class AddBook(StatesGroup):
    name = State()
    author = State()
    description = State()
    genre = State()


class SearchBook(StatesGroup):
    name = State()
    genre = State()