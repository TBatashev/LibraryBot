from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from .callback_factory import UserActionCall, UserAction
from db import Books, Genres
from db import crud


# Клавиатура в главном меню
async def get_start_kb():
    start_kb = InlineKeyboardBuilder()
    start_kb.add(
        InlineKeyboardButton(text='Список книг', callback_data=UserActionCall(action=UserAction.list_book).pack()),
        InlineKeyboardButton(text='Поиск книги', callback_data=UserActionCall(action=UserAction.search_book).pack()),
        InlineKeyboardButton(text='Добавить книгу', callback_data=UserActionCall(action=UserAction.add_book).pack())  )

    start_kb.adjust(2)
    return start_kb.as_markup()



# Выбор режима поиска книг
async def get_choice_search():
    kb = InlineKeyboardBuilder()
    kb.add(
        InlineKeyboardButton(text='По полям', callback_data=UserActionCall(action=UserAction.search_book_name).pack()),
        InlineKeyboardButton(text='По жанру', callback_data=UserActionCall(action=UserAction.search_genre_name).pack()) )

    return kb.as_markup()


# Удаление книг
async def delete_book(session : AsyncSession, book_hash):
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text='Удалить', callback_data=UserActionCall(action=UserAction.delete_book, book_hash=book_hash).pack()))

    return kb.as_markup()





# Выводим список жанров
async def get_genres(session : async_sessionmaker):
    async with session as session:
        genres_list = await crud.get_genres_list(session)
        if len(genres_list) == 0 :
            kb = InlineKeyboardBuilder()
            kb.add(InlineKeyboardButton(text='Нет доступных', callback_data=UserActionCall(action=UserAction.dont_genres).pack()))
            return kb.as_markup()
        else :
            keyboard = InlineKeyboardBuilder()
            for genre in genres_list:
                keyboard.add(InlineKeyboardButton(
                    text=genre.name, callback_data=UserActionCall(action=UserAction.genre, genre=genre.name).pack()
                ))
            keyboard.adjust(5)
            return keyboard.as_markup()


async def build_books_list(session: async_sessionmaker, book_list):
    books_list = InlineKeyboardBuilder()
    books_count: int = 0
    for book in book_list:
        books_count += 1
        books_list.button(
            text=book.name,
            callback_data=UserActionCall(
                action=UserAction.detail_book,
                book_hash=book.unique_hash,
            ).pack()
        )
    return books_list.as_markup()

async def get_list_books(session: async_sessionmaker):
    book_list_ = await crud.get_books_list(session=session)
    return await build_books_list(session, book_list_)

async def get_list_search(session: async_sessionmaker, text: str):
    book_list_ = await crud.get_books_list_search(session, text)
    return await build_books_list(session, book_list_)

async def get_genre_list_book(session: async_sessionmaker, text: str):
    book_list_ = await crud.get_books_by_genre(session, text)
    return await build_books_list(session, book_list_)