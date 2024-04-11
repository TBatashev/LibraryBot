from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, ContentType, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.filters.magic_data import MagicData
from aiogram.filters import Filter

from keyboard import UserAction, UserActionCall, get_list_books, get_start_kb, get_genres, get_list_search, delete_book, get_choice_search, get_genre_list_book
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from states import AddBook, SearchBook

from db import crud, Books
from uuid import uuid4


user_router = Router()


@user_router.message(F.text == '/start')
async def start_command(msg : Message):
    """
    Команда '/start'
    :params msg : Message:
    :return start keyboard:
    """
    await msg.answer(text='Добро пожаловать в главное меню', reply_markup=await get_start_kb())


@user_router.callback_query(
        UserActionCall.filter(F.action == UserAction.list_book)
)
async def list_book(call : CallbackQuery, callback_data : UserActionCall, session : async_sessionmaker):
    """
    Отображает список книг
    """
    try :
        await call.answer()
        await call.message.answer(text='Список доступных книг', reply_markup=await get_list_books(session))
    except Exception as ex:
        await call.message.answer(text=f'Не удалось отобразить список книг: {ex}')



@user_router.callback_query(
        UserActionCall.filter(F.action == UserAction.detail_book)
)
async def get_detail_book(call : CallbackQuery, callback_data : UserActionCall, session : async_sessionmaker):
    try :
        """
        Детальная информация о книге
        """
        await call.answer()
        book_info : Books = await crud.get_detail_book(session, callback_data.book_hash)
        for book in book_info[0]:
            await call.message.answer(text=f'Подробная информация о выбранной книге:\n\n'
                                    f'Название: {book.name}\n'
                                    f'Автор: {book.author}\n'
                                    f'Жанр: {book_info[1]}\n'
                                    f'Описание: {book.description}', reply_markup=await delete_book(session, callback_data.book_hash))

    except Exception as ex:
        await call.message.answer(text=f'Не удалось посмотреть детальную информацию о книге: {ex}')


@user_router.callback_query(
        UserActionCall.filter(F.action == UserAction.delete_book)
)
async def delete_book_handler(call : CallbackQuery, callback_data : UserActionCall, session : async_sessionmaker):
    try :
        """
        Удаляем книгу
        """
        await call.message.delete()
        await crud.delete_book_bd(session, callback_data.book_hash)

        await call.message.answer('Книга успешно удалена')

    
    except Exception as ex:
        await call.message.answer(f'Ошибка при удалении книги: {ex}')




@user_router.callback_query(
    UserActionCall.filter(F.action == UserAction.add_book)
)
async def add_book(call : CallbackQuery, state : FSMContext):
    """
    Добавление книги старт. Просим ввести название книги
    """
    try :
        await call.answer()
        await call.message.answer('Отлично. Введите название книги')
        await state.set_state(AddBook.name)
    except Exception as ex:
        await call.message.answer(f'Ошибка: {ex}')

@user_router.message(AddBook.name)
async def add_name_book(msg : Message, state : FSMContext):
    """
    Просим ввести автора книги
    """
    try :
        name = msg.text
        await state.update_data(name=name)
        await state.set_state(AddBook.author)

        await msg.answer('Укажите автора книги')
    
    except Exception as ex:
        await msg.answer(f'Не удалось добавить название книги: {ex}')
        await state.clear()



@user_router.message(AddBook.author)
async def add_name_book(msg : Message, state : FSMContext):
    """
    Просим ввести описание книги
    """
    try :
        author = msg.text
        await state.update_data(author=author)
        await msg.answer('Введите описание')
        await state.set_state(AddBook.description)

    
    except Exception as ex:
        await msg.answer(f'Не удалось добавить автора: {ex}')
        await state.clear()



@user_router.message(AddBook.description)
async def add_name_book(msg : Message, state : FSMContext, session : async_sessionmaker):
    """
    Просим указать жанр книги
    """
    try :
        description = msg.text
        await state.update_data(description=description)
        await msg.answer('Укажите жанр книги.\nВы можете выбрать один из доступных', reply_markup=await get_genres(session))

        await state.set_state(AddBook.genre)
    
    except Exception as ex:
        await msg.answer(text=f'Не удалось добавить описание: {ex}')
        await state.clear()


@user_router.message(
        AddBook.genre
)
async def create_new_genre(msg : Message, session : AsyncSession, state : FSMContext):
    """
    Указываем свой жанр
    """
    try :
        genre = msg.text
        genre_obj = await crud.get_or_create_genre(session, genre)
        await state.update_data(genre=genre)

        unique_hash = uuid4()
        data = await state.get_data()

        await crud.create_book(session, data, str(unique_hash), genre_obj)
        await msg.answer(text=f'Вы успешно добавили книгу:\n'
                                    f'Название: {data["name"]}\n'
                                    f'Автор: {data["author"]}\n'
                                    f'Жанр: {data["genre"]}\n'
                                    f'Описание: {data["description"]}')
        await state.clear()
    except Exception as ex:
        await msg.answer(f'Ошибка при добавлении нового жанра: {ex}')
        await state.clear()


@user_router.callback_query(
    AddBook.genre,
    UserActionCall.filter(F.action == UserAction.genre)
)
async def select_genre_from_list(call : CallbackQuery, callback_data : UserActionCall, state : FSMContext, session : async_sessionmaker):
    """
    Пользователь выбирает жанр из доступных
    """
    try :
        await call.answer()
        genre = callback_data.genre
        await state.update_data(genre=genre)
        unique_hash = uuid4()
        
        data = await state.get_data()
        genre = await crud.get_genre_obj(session, data['genre'])
        
        await crud.create_book(session, data, str(unique_hash), genre)
        await call.message.answer(text=f'Вы успешно добавили книгу:\n'
                                  f'Название: {data["name"]}\n'
                                  f'Автор: {data["author"]}\n'
                                  f'Жанр: {data["genre"]}\n'
                                  f'Описание: {data["description"]}')
        await state.clear()
    
    except Exception as ex:
        await call.message.answer(f'Не удалось добавить книгу: {ex}')
        await state.clear()




@user_router.callback_query(
    UserActionCall.filter(F.action == UserAction.search_book)
)
async def search_start_book(call : CallbackQuery, callback_data : UserActionCall, state : FSMContext):
    """
    Выбор режима поиска. Ждем ответа юзера
    """
    try :
        await call.message.answer(text='Выберите один из вариантов', reply_markup=await get_choice_search() )
        await call.answer()


    except Exception as ex:
        await call.message.answer(f'Не удалось выбрать режим поиска: {ex}')




@user_router.callback_query(
    UserActionCall.filter(F.action == UserAction.search_genre_name)
)
async def search_start_book(call : CallbackQuery, callback_data : UserActionCall, state : FSMContext):
    """
    Начинаем поиск книги по жанру. Ждем ответа юзера
    """
    try :
        await call.answer()
        await call.message.answer('Введите названия жанра для поиска')
        await state.set_state(SearchBook.genre)


    except Exception as ex:
        await call.message.answer(f'Не удалось начать поиск по жанру: {ex}')



@user_router.message(
    SearchBook.genre
)
async def search_book(msg : Message, state : FSMContext, session : async_sessionmaker):
    try :
    
        text = msg.text
        await msg.answer(text=f'Книги по запросу: {text}', reply_markup=await get_genre_list_book(session, text))
        await state.clear()
    
    except Exception as ex:
        await msg.answer(f'Ошибка при поиске книги: {ex}')



@user_router.callback_query(
    UserActionCall.filter(F.action == UserAction.search_book_name)
)
async def search_start_book(call : CallbackQuery, callback_data : UserActionCall, state : FSMContext):
    """
    Начинаем поиск книги по полям. Ждем ответа юзера
    """
    try :
        await call.answer()
        await call.message.answer('Введите ключевое слово для поиска')
        await state.set_state(SearchBook.name)


    except Exception as ex:
        await call.message.answer(f'Не удалось начать поиск по полям: {ex}')


@user_router.message(
    SearchBook.name
)
async def search_book(msg : Message, state : FSMContext, session : async_sessionmaker):
    try :
    
        text = msg.text
        await msg.answer(text=f'Книги по запросу: {text}', reply_markup=await get_list_search(session, text))
        await state.clear()
    
    except Exception as ex:
        await msg.answer(f'Ошибка при поиске книги: {ex}')