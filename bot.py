import requests
import telebot
import random
import asyncio
import time

bot = telebot.TeleBot('YOUR:TOKEN')

check_get = 0
check_count = 0
check_work = 0
check_not = 0
users_id = []
users = 0


@bot.message_handler(commands=['start'])
def start_message(message):
    global users_id, users
    if message.chat.id not in users_id:
        users_id.append(message.chat.id)
        users += 1
    bot.send_message(message.chat.id, "Добро пожаловать в проксиляндию! \nЗдесь вы можете получить прокси/проверить абсолютно бесплатно!\n Посмотреть команды /help")

# Команда /help
@bot.message_handler(commands=['help'])
def help_message(message):
    bot.send_message(message.chat.id, "Все команды: \n/help - Посмотреть все команды\n/stat - Посмотреть статистику\n/get - Получить бесплатные прокси\n/check - Проверить работоспособность ваших прокси\n\nНа данный момент это все команды!\nGitHub: https://github.com/DarhanGamesYT/proxygrabber-telegram-bot")


@bot.message_handler(commands=['stat'])
def get_handler(message):
    bot.reply_to(message, f'Статистика\n\nВыдали прокси: {check_get}\nПользователей: {users}\nПроверенно прокси: {check_count}\nРаботающие прокси: {check_work}\nНерабочие прокси: {check_not}')

# Обработчик для команды /get
@bot.message_handler(commands=['get'])
def get_handler(message):
    global check_get
    # Получаем 5 рандомных прокси-серверов с помощью API https://gimmeproxy.com
    url = 'https://gimmeproxy.com/api/getProxy?anonymityLevel=1&protocol=http'
    proxies = []
    for i in range(5):
        response = requests.get(url)
        proxy = response.json()['ip'] + ':' + str(response.json()['port'])
        proxies.append(proxy)
    
    check_get += 5
    # Отправляем пользователю список прокси-серверов в формате Моно
    proxies_str = '\n'.join(proxies)
    bot.reply_to(message, f"Вот 5 рандомных прокси:\n\n<code>{proxies_str}</code>", parse_mode='HTML')

# Обработчик для команды /check
@bot.message_handler(commands=['check'])
def check_handler(message):
    # Отправляем сообщение с запросом на прокси
    bot.reply_to(message, 'Пожалуйста, отправьте до 50 прокси в формате ip:port каждую в новой строке')
    
    # Создаем обработчик для следующего сообщения пользователя
    @bot.message_handler(func=lambda m: True)
    def proxy_handler(message):
        # Получаем прокси, которые пользователь отправил
        proxies = message.text.strip().split('\n')
        
        # Ограничиваем количество прокси до 50
        proxies = proxies[:50]

        # Отправляем сообщение с эмодзи песочных часов, чтобы показать, что бот занят
        chat_id = message.chat.id
        action_message = bot.send_message(chat_id, "⌛ Проверка прокси...")
        action_message_id = action_message.message_id
        
        # Проверяем прокси асинхронно
        async def check_proxy(proxy):
            global check_count, check_work, check_not
            
            try:
                response = requests.get('http://httpbin.org/ip', proxies={'http': 'http://' + proxy}, timeout=5)
                if response.status_code == 200:
                    check_count += 1
                    check_work += 1
                    return {'proxy': proxy, 'status': 'work'}
                else:
                    check_count += 1
                    check_not += 1
                    return {'proxy': proxy, 'status': 'not work'}
            except:
                check_count += 1
                check_not += 1
                return {'proxy': proxy, 'status': 'not work'}
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        results = loop.run_until_complete(asyncio.gather(*[check_proxy(proxy) for proxy in proxies]))
        loop.close()
        
        # Формируем ответ пользователю
        work_proxies = [r['proxy'] for r in results if r['status'] == 'work']
        not_work_proxies = [r['proxy'] for r in results if r['status'] == 'not work']
        response = 'Результаты проверки:\n\n'
        response += '<b>work proxy:</b>\n<code>' + '\n'.join(work_proxies) + '</code>\n\n' if work_proxies else ''
        response += '<b>not worked:</b>\n<s><code>' + '\n'.join(not_work_proxies) + '</code></s>' if not_work_proxies else ''
        
        # Удаляем сообщение с эмодзи песочных часов
        bot.delete_message(chat_id, action_message_id)
        
        # Отправляем ответ пользователю
        bot.send_message(chat_id, response, parse_mode='HTML')
        
    # Регистрируем обработчик для следующего сообщения пользователя
    bot.register_next_step_handler(message, proxy_handler)

# Запускаем бота
bot.polling(none_stop=True)
