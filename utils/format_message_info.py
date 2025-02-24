from aiogram.types import Message, CallbackQuery


def format_message_info(message: Message) -> str:
    """
    Формирует текст на основе объекта Message.
    """
    return (
        f'Пользователь с id={message.chat.id}, ником: @{message.chat.username} и именем: {message.chat.full_name} '
        f'отправил сообщение:\n\n{message.text}\n\n<code>/send {message.chat.id} </code>')


def format_callback_query_info(callback_query: CallbackQuery) -> str:
    """
    Формирует текст на основе объекта CallbackQuery.
    """
    return (f'Пользователь с id={callback_query.message.chat.id}, ником: @{callback_query.message.chat.username}  '
            f'и именем: {callback_query.message.chat.full_name} нажал на кнопку:'
            f'\n\n{callback_query.message.text}\n\n<code>/send {callback_query.message.chat.id} </code>')
