from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy import select, update, ScalarResult, func, or_

from .models import Books, Genres

from typing import Union, List
from datetime import datetime, timedelta



# Детальная информация о книге
async def get_detail_book(session : async_sessionmaker, unique_hash):
    async with session as session:
        book_ = await session.execute(select(Books).where(Books.unique_hash == unique_hash))
        book_detail = book_.scalars().all()
        for book in book_detail:
            genre = await session.execute(select(Genres).where(Genres.id == book.genre_id))
            genre = genre.scalar_one_or_none()
            
 
        return [book_detail, genre.name]


# Получаем список книг
async def get_books_list(session: async_sessionmaker):
    # async with session.begin() :
    async with session as session :
        books_all = await session.execute(select(Books))
        books =  books_all.scalars().all()

        return books
    

# Получаем список книг по определенным полям
async def get_books_list_search(session: async_sessionmaker, text):
    # async with session.begin() :
    async with session as session :
        books_all = await session.execute(select(Books).where(or_(Books.name.ilike(text), Books.author.ilike(text))))
        books =  books_all.scalars().all()

        return books


# Получаем список жанров
async def get_genres_list(session: async_sessionmaker):
    # async with session.begin() :
    async with session as session :
        genres_all = await session.execute(select(Genres))
        genres = genres_all.scalars().all()

        return genres


# Получаем жанр
async def get_genre_obj(session: async_sessionmaker, name):
    # async with session.begin() :
    async with session as session :
        genre_ = await session.execute(select(Genres).where(Genres.name == name))
        genre = genre_.scalar_one_or_none()
        return genre


# Создаем книгу
async def create_book(session: async_sessionmaker, state_data, unique_hash : str, genre : Genres):
    # async with session.begin() :
    async with session as session :
        book = Books(
            author=state_data['author'],
            name=state_data['name'],
            description=state_data['description'],
            unique_hash=unique_hash,
            genre_id=genre.id
        )
        # session.add(book)
        await session.merge(book)
        await session.commit()
        return book


# Создаем жанр если его нет, в ином случае достаем существующий
async def get_or_create_genre(session : async_sessionmaker, name : str):
    # async with session.begin():
    async with session as session:
        genre_ = await session.execute(select(Genres).where(Genres.name.ilike(name)))
        # genre_ = await session.execute(select(Genres).where(Genres.name == name))
        genre = genre_.scalar_one_or_none()
        
        if genre is None:
            genre_obj = Genres(
                name=name
            )
            session.add(genre_obj)
            await session.merge(genre_obj)
            await session.commit()
            genre_ = await session.execute(select(Genres).where(Genres.name.ilike(name)))
            genre = genre_.scalar_one_or_none()
            # return genre

    return genre


# Удаление книги
async def delete_book_bd(session : AsyncSession, book_hash):
    book = await session.execute(select(Books).where(Books.unique_hash == book_hash))
    res = book.scalars().one()
    await session.delete(res)
    await session.commit()


# Выводим книги с определенным жанром
async def get_books_by_genre(session: AsyncSession, genre_name: str):
    async with session as session:
        query = select(Books).join(Genres).filter(Genres.name == genre_name)
        result = await session.execute(query)
        books = result.scalars().all()

    return books