from aiogram.filters.callback_data import CallbackData

# --- CallbackData для Демо-задачи (Arq) ---
# Мы создаем отдельный класс для каждого функционального блока.
# Это гарантирует безопасность: кнопки от "Отчета" никогда не вызовут хэндлеры "Рассылки" или "Настроек".
#
# prefix="demo" — это пространство имен. В строке это будет выглядеть как "demo:confirm".
class DemoTaskCallback(CallbackData, prefix="demo"):
    action: str  # Поле для действия, например: "confirm" или "cancel"