import os
import telebot
from config import *
from logic import *

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "Привет! Я бот, который может показывать города на карте. Напиши /help для списка команд.")

@bot.message_handler(commands=['help'])
def handle_help(message):
    commands_text = (
        "Доступные команды:\n"
        "/start - Начать работу с ботом\n"
        "/help - Показать список команд\n"
        "/show_city <Название_города> - Показать город на карте\n"
        "/remember_city <Название_города> - Сохранить город в избранное\n"
        "/show_my_cities - Показать все сохраненные вами города на общей карте"
    )
    bot.send_message(message.chat.id, commands_text)

@bot.message_handler(commands=['show_city'])
def handle_show_city(message):
    try:
        city_name = message.text.split(maxsplit=1)[-1].strip().title()
    except IndexError:
        bot.send_message(message.chat.id, "Пожалуйста, укажите название города. Пример: `/show_city London`", parse_mode="Markdown")
        return

    coordinates = manager.get_coordinates(city_name)
    if not coordinates:
        bot.send_message(message.chat.id, "Такого города я не знаю. Убедись, что он написан на английском!")
        return

    image_path = f"city_{message.chat.id}.png"
    
    try:
        manager.create_graph(image_path, [city_name])
        with open(image_path, 'rb') as photo:
            bot.send_photo(message.chat.id, photo, caption=f"Вот город {city_name} на карте!")
        if os.path.exists(image_path):
            os.remove(image_path)
    except Exception as e:
        bot.send_message(message.chat.id, "Произошла ошибка при отрисовке карты.")
        print(f"Ошибка в handle_show_city: {e}")

@bot.message_handler(commands=['remember_city'])
def handle_remember_city(message):
    user_id = message.chat.id
    try:
        city_name = message.text.split(maxsplit=1)[-1].strip().title()
    except IndexError:
        bot.send_message(message.chat.id, "Пожалуйста, укажите название города. Пример: `/remember_city Paris`", parse_mode="Markdown")
        return

    if manager.add_city(user_id, city_name):
        bot.send_message(message.chat.id, f'Город {city_name} успешно сохранен!')
    else:
        bot.send_message(message.chat.id, 'Такого города я не знаю. Убедись, что он написан на английском!')

@bot.message_handler(commands=['show_my_cities'])
def handle_show_visited_cities(message):
    user_id = message.chat.id
    cities = manager.select_cities(user_id)
    
    if not cities:
        bot.send_message(message.chat.id, "Вы еще не сохранили ни одного города! Используйте команду `/remember_city <город>`.", parse_mode="Markdown")
        return

    image_path = f"my_cities_{user_id}.png"
    
    try:
        manager.create_graph(image_path, cities)
        with open(image_path, 'rb') as photo:
            bot.send_photo(message.chat.id, photo, caption="Вот все ваши сохраненные города на карте!")
        if os.path.exists(image_path):
            os.remove(image_path)
    except Exception as e:
        bot.send_message(message.chat.id, "Произошла ошибка при сборке карты ваших городов.")
        print(f"Ошибка в handle_show_visited_cities: {e}")

if __name__ == "__main__":
    manager = DB_Map(DATABASE)
    manager.create_user_table()
    print("Бот успешно запущен и слушает команды...")
    bot.polling(none_stop=True)
