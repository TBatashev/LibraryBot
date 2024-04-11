from aiogram.filters.callback_data import CallbackData
from enum import Enum

from typing import Optional




class UserAction(str, Enum):
    add_book = 'add_book'
    delete_book = 'delete_book'
    check_book = 'check_book'
    list_book = 'list_book'
    search_book = 'search_book'

    # genre_search = 'genre_search'

    detail_book = 'detail_book'
    genre = 'genre'

    dont_genres = 'dont_genres'

    search_book_name = 'search_book_name'
    search_genre_name = 'search_genre_name'


class UserActionCall(CallbackData, prefix='user'):
    action: UserAction
    genre : Optional[str] = None
    book_hash : Optional[str] = None

    


