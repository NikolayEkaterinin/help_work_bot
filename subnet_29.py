import sqlite3
from aiogram.types import Message


async def process_sap_request(message: Message, sap: str):
    conn2 = sqlite3.connect('ip_addresses.db')
    cursor2 = conn2.cursor()
    cursor2.execute("SELECT name FROM sqlite_master WHERE type='ip_addresses';")

    # Включение переданного значения sap в SQL-запрос
    cursor2.execute("SELECT subnet_ip FROM ip_addresses WHERE sap = ?",
                    (sap,))
    try:
        rows = cursor2.fetchall()
        last_part = [row[0].split(".")[-1] for row in rows]
        first_part = [row[0].split(".")[:3] for row in rows]
        message_list = []

        for i, row in enumerate(rows):
            ip_parts = first_part[i]  # Первые три октета адреса

            dict_entry = {f'Сервер {i + 1}': '.'.join(
                ip_parts)}  # Создание словаря с именем сервера и адресом
            message_list.append(
                dict_entry)  # Добавление словаря в список message
        # для сети с последним октетом 0
        if int(last_part[0]) == 0:
            message_vlan12 = [
                'VLAN 12 - Для сервера магазина и удаленного управления',
                {
                    'Плата удаленного управления резервного сервера': '.'.join(
                        first_part[0] + ['3'])},
                {'Плата удаленного управления сервером': '.'.join(
                    first_part[0] + ['4'])},
                {'Сервер BO резервный': '.'.join(first_part[0] + ['5'])},
                {'Сервер BP': '.'.join(first_part[0] + ['6'])},
                {'Шлюз': '.'.join(first_part[0] + ['1'])},
                {'Маска': '255.255.255.248'}
            ]
            message_vlan10 = [
                'VLAN 10 - для CashControl',
                {'Сервер CashControl': '.'.join(first_part[0] + ['11'])},
                {'2й Сервер CashControl': '.'.join(
                    first_part[0] + ['12'])},
                {'Шлюз': '.'.join(first_part[0] + ['9'])},
                {'Маска': '255.255.255.248'}
            ]
            message_vlan6 = [
                'VLAN 6 - для касс и КСО',
                {'Кассы': '.'.join(first_part[0] + ['98-112'])},
                {'КСО зоны кофе': '.'.join(first_part[0] + ['113-114'])},
                {'КСО': '.'.join(first_part[0] + ['115-126'])},
                {'Шлюз': '.'.join(first_part[0] + ['97'])},
                {'Маска': '255.255.255.224'}
            ]
            message_vlan4 = [
                'VLAN 4 - для устройств, которым не требуется взаимодействие с сервером BO',
                {'Сервер радио 5': '.'.join(first_part[0] + ['34'])},
                {'Биометрический терминал': '.'.join(
                    first_part[0] + ['44'])},
                {'Сервер для видеоаналитики СБ': '.'.join(
                    first_part[0] + ['45'])},
                {'ЕСУМ (инфокиоск, LED-панель': '.'.join(
                    first_part[0] + ['46-52'])},
                {'Хлебопечи': '.'.join(first_part[0] + ['54-55'])},
                {'Оборудование ПЭС(ЦХМ)': '.'.join(
                    first_part[0] + ['59'])},
                {'Оборудование ПЭС(АСКУЭ)АССД': '.'.join(
                    first_part[0] + ['60'])},
                {'Оборудование ПЭС(Умный щит)': '.'.join(
                    first_part[0] + ['61'])},
                {'Шлюз': '.'.join(first_part[0] + ['33'])},
                {'Маска': '255.255.255.224'}

            ]
            message_vlan8 = [
                'VLAN 8 - для устройств, которым требуется доступ по UDP к системам снаружи магазина и к серверу BO',
                {'МФУ': '.'.join(first_part[0] + ['18'])},
                {'Принтер': '.'.join(first_part[0] + ['19'])},
                {'Сервер электронных ценников ESL': '.'.join(
                    first_part[0] + ['25'])},
                {'Точки доступа электронных ценников': '.'.join(
                    first_part[0] + ['26-30'])},
                {'Шлюз': '.'.join(first_part[0] + ['17'])},
                {'Маска': '255.255.255.240'}
            ]
            message_vlan2 = [
                'VLAN 2 - для устройств, подключаемых по проводу и которым не требуется прямой доступ к внешним системам',
                {'Стационарный термопринтер': '192.168.3.25-26'},
                {
                    'Весы для касс самообслуживания (SWS)(Даркстор)': '192.168.3.30-32'},
                {'Прайсчекер WINCE': '192.168.3.100-103'},
                {'Шлюз': '192.168.3.1'},
                {'Маска': '255.255.255.0'}
            ]
            message_vlan33 = [
                'VLAN 33 - для устройств, подключаемых по Wi-Fi и которым не требуется прямой доступ к внешним системам',
                {'Мобильный принтер': '192.168.1.10-14'},
                {
                    'Весы для касс самообслуживания (SWS)(Даркстор)': '192.168.1.16-18'},
                {'Шлюз': '192.168.1.1'},
                {'Маска': '255.255.255.0'}
            ]
            await message.answer(message_vlan12)
            await message.answer(message_vlan10)
            await message.answer(message_vlan6)
            await message.answer(message_vlan4)
            await message.answer(message_vlan8)
            await message.answer(message_vlan2)
            await message.answer(message_vlan33)

        # для сети с последним октетом 128
        elif int(last_part[0]) == 128:
            message_vlan12 = [
                'VLAN 12 - Для сервера магазина и удаленного управления',
                {
                    'Плата удаленного управления резервного сервера': '.'.join(
                        first_part[0] + ['131'])},
                {'Плата удаленного управления сервером': '.'.join(
                    first_part[0] + ['132'])},
                {'Сервер BO резервный': '.'.join(first_part[0] + ['133'])},
                {'Сервер BP': '.'.join(first_part[0] + ['134'])},
                {'Шлюз': '.'.join(first_part[0] + ['129'])},
                {'Маска': '255.255.255.248'}
            ]
            message_vlan10 = [
                'VLAN 10 - для CashControl',
                {'Сервер CashControl': '.'.join(first_part[0] + ['139'])},
                {'2й Сервер CashControl': '.'.join(
                    first_part[0] + ['140'])},
                {'Шлюз': '.'.join(first_part[0] + ['137'])},
                {'Маска': '255.255.255.248'}
            ]
            message_vlan6 = [
                'VLAN 6 - для касс и КСО',
                {'Кассы': '.'.join(first_part[0] + ['226-240'])},
                {'КСО зоны кофе': '.'.join(first_part[0] + ['241-242'])},
                {'КСО': '.'.join(first_part[0] + ['243-254'])},
                {'Шлюз': '.'.join(first_part[0] + ['225'])},
                {'Маска': '255.255.255.224'}
            ]
            message_vlan4 = [
                'VLAN 4 - для устройств, которым не требуется взаимодействие с сервером BO',
                {'Сервер радио 5': '.'.join(first_part[0] + ['162'])},
                {'Биометрический терминал': '.'.join(
                    first_part[0] + ['172'])},
                {'Сервер для видеоаналитики СБ': '.'.join(
                    first_part[0] + ['173'])},
                {'ЕСУМ (инфокиоск, LED-панель': '.'.join(
                    first_part[0] + ['174-180'])},
                {'Хлебопечи': '.'.join(first_part[0] + ['182-183'])},
                {'Оборудование ПЭС(ЦХМ)': '.'.join(
                    first_part[0] + ['187'])},
                {'Оборудование ПЭС(АСКУЭ)АССД': '.'.join(
                    first_part[0] + ['188'])},
                {'Оборудование ПЭС(Умный щит)': '.'.join(
                    first_part[0] + ['189'])},
                {'Шлюз': '.'.join(first_part[0] + ['161'])},
                {'Маска': '255.255.255.224'}

            ]
            message_vlan8 = [
                'VLAN 8 - для устройств, которым требуется доступ по UDP к системам снаружи магазина и к серверу BO',
                {'МФУ': '.'.join(first_part[0] + ['146'])},
                {'Принтер': '.'.join(first_part[0] + ['147'])},
                {'Сервер электронных ценников ESL': '.'.join(
                    first_part[0] + ['153'])},
                {'Точки доступа электронных ценников': '.'.join(
                    first_part[0] + ['154-158'])},
                {'Шлюз': '.'.join(first_part[0] + ['145'])},
                {'Маска': '255.255.255.240'}
            ]
            message_vlan2 = [
                'VLAN 2 - для устройств, подключаемых по проводу и которым не требуется прямой доступ к внешним системам',
                {'Стационарный термопринтер': '192.168.3.25-26'},
                {
                    'Весы для касс самообслуживания (SWS)(Даркстор)': '192.168.3.30-32'},
                {'Прайсчекер WINCE': '192.168.3.100-103'},
                {'Шлюз': '192.168.3.1'},
                {'Маска': '255.255.255.0'}
            ]
            message_vlan33 = [
                'VLAN 33 - для устройств, подключаемых по Wi-Fi и которым не требуется прямой доступ к внешним системам',
                {'Мобильный принтер': '192.168.1.10-14'},
                {
                    'Весы для касс самообслуживания (SWS)(Даркстор)': '192.168.1.16-18'},
                {'Шлюз': '192.168.1.1'},
                {'Маска': '255.255.255.0'}
            ]
            await message.answer(message_vlan12)
            await message.answer(message_vlan10)
            await message.answer(message_vlan6)
            await message.answer(message_vlan4)
            await message.answer(message_vlan8)
            await message.answer(message_vlan2)
            await message.answer(message_vlan33)
        else:
            await message.answer('Данный объект ещё не переведен')

    except:
        await message.answer('Введенное значение не является SAP')

    conn2.close()