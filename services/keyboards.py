from aiogram.utils.keyboard import InlineKeyboardBuilder

kb_start = InlineKeyboardBuilder()
kb_start.button(text='📈 Заказано товаров', callback_data=f'products_ordered')
kb_start.adjust(1)

kb_back = InlineKeyboardBuilder()
kb_back.button(text='⬅️ Назад', callback_data=f'kb_back')

kb_cancel = InlineKeyboardBuilder()
kb_cancel.button(text='❌ Отмена', callback_data=f'kb_cancel')

kb_products_ordered_menu = InlineKeyboardBuilder()
kb_products_ordered_menu.button(text='За сегодня', callback_data=f'kb_po_menu_today')
kb_products_ordered_menu.button(text='За вчера', callback_data=f'kb_po_menu_yesterday')
kb_products_ordered_menu.button(text='За неделю', callback_data=f'kb_po_menu_week')
kb_products_ordered_menu.button(text='За месяц', callback_data=f'kb_po_menu_month')
kb_products_ordered_menu.button(text='Ввести даты вручную', callback_data='kb_po_menu_custom_date')
kb_products_ordered_menu.button(text='⬅️ Назад', callback_data=f'kb_back')
kb_products_ordered_menu.adjust(2, 2, 1, 1)
