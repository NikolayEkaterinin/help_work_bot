from django.http import JsonResponse
from .models import IPAddresses
import time

# Расчет 29 сети
def chunks(lst, n):
    """Разбивает список на куски по n элементов."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def format_vlan_messages(messages):
    formatted_messages = []
    for message in messages:
        vlan = message["VLAN"]
        devices = message["Devices"]
        description = message["Description"]
        device_text = "\n".join([f"{device['Device']}: {device['IP']}" for device in devices])
        formatted_messages.append(f"VLAN {vlan}: {description}\n{device_text}")
    return formatted_messages


def send_vlan_messages(bot, chat_id, vlan_messages):
    chunk_size = 7  # Ограничение на количество сообщений в одной порции
    for chunk in chunks(vlan_messages, chunk_size):
        messages_text = "\n\n".join(format_vlan_messages(chunk))
        # Проверка длины сообщения
        if len(messages_text) <= 4096:
            bot.send_message(chat_id, messages_text)
            time.sleep(0.2)
        else:
            # Если сообщение слишком длинное, разделите его на более короткие части и отправьте их по очереди
            for sub_message in chunks(messages_text.split("\n\n"), chunk_size):
                bot.send_message(chat_id, "\n\n".join(sub_message))
                time.sleep(0.2)


def process_29_network(sap, bot, chat_id):
    sap = sap.upper()
    try:
        ip_addresses = IPAddresses.objects.filter(sap=sap)
        last_part = [ip.subnet_mag.split(".")[-1] for ip in ip_addresses]
        first_part = [ip.subnet_mag.split(".")[:3] for ip in ip_addresses]
        vlan_messages = []

        for part in [0, 128]:
            if int(last_part[0]) == part:
                # VLAN 12
                vlan_12_devices = [
                    {"Device": "Плата удаленного управления резервного сервера",
                     "IP": '.'.join(first_part[0]) + '.' + str(int(last_part[0]) + 3)},
                    {"Device": "Плата удаленного управления сервером",
                     "IP": '.'.join(first_part[0]) + '.' + str(int(last_part[0]) + 4)},
                    {"Device": "Сервер BO резервный", "IP": '.'.join(first_part[0]) + '.' + str(int(last_part[0]) + 5)},
                    {"Device": "Сервер BP", "IP": '.'.join(first_part[0]) + '.' + str(int(last_part[0]) + 6)},
                    {"Device": "Шлюз", "IP": '.'.join(first_part[0]) + '.' + str(int(last_part[0]) + 1)},
                    {"Device": "Маска", "IP": "255.255.255.248"}
                ]

                vlan_messages.append({
                    "VLAN": 12,
                    "Description": "Для сервера магазина и удаленного управления",
                    "Devices": vlan_12_devices
                })

                # VLAN 10
                vlan_10_devices = [
                    {"Device": "Сервер CashControl", "IP": '.'.join(first_part[0]) + '.' + str(int(last_part[0]) + 11)},
                    {"Device": "2й Сервер CashControl", "IP": '.'.join(first_part[0]) + '.' + str(int(last_part[0]) + 12)},
                    {"Device": "Шлюз", "IP": '.'.join(first_part[0]) + '.' + str(int(last_part[0]) + 9)},
                    {"Device": "Маска", "IP": "255.255.255.248"}
                    ]
                vlan_messages.append({
                    "VLAN": 10,
                    "Description": "Для CashControl",
                    "Devices": vlan_10_devices
                })

                # VLAN 6
                vlan_6_devices = [
                    {"Device": "Кассы",
                     "IP": '.'.join(first_part[0]) + '.' + str(int(last_part[0]) + 98) + "-" + '.'.join(first_part[0]) + '.' + str(int(last_part[0]) + 112)},
                    {"Device": "КСО зоны кофе",
                     "IP": '.'.join(first_part[0]) + '.' + str(int(last_part[0]) + 113) + "-" + '.'.join(first_part[0]) + '.' + str(int(last_part[0]) + 114)},
                    {"Device": "КСО", "IP": '.'.join(first_part[0]) + '.' + str(int(last_part[0]) + 115) + "-" + '.'.join(first_part[0]) + '.' + str(int(last_part[0]) + 126)},
                    {"Device": "Шлюз",
                     "IP": '.'.join(first_part[0]) + '.' + str(int(last_part[0]) + 97)},
                    {"Device": "Маска", "IP": "255.255.255.224"}
                ]
                vlan_messages.append({
                    "VLAN": 6,
                    "Description": "Для касс и КСО",
                    "Devices": vlan_6_devices
                })

                # VLAN 4
                vlan_4_devices = [
                    {"Device": "Сервер радио 5", "IP": '.'.join(first_part[0]) + '.' + str(int(last_part[0]) + 34)},
                    {"Device": "Биометрический терминал", "IP": '.'.join(first_part[0]) + '.' + str(int(last_part[0]) + 44)},
                    {"Device": "Сервер для видеоаналитики СБ", "IP": '.'.join(first_part[0]) + '.' + str(int(last_part[0]) + 45)},
                    {"Device": "ЕСУМ (инфокиоск, LED-панель",
                     "IP": '.'.join(first_part[0]) + '.' + str(int(last_part[0]) + 46) + "-" + '.'.join(first_part[0]) + '.' + str(int(last_part[0]) + 52)},
                    {"Device": "Хлебопечи",
                     "IP": '.'.join(first_part[0]) + '.' + str(int(last_part[0]) + 54) + "-" + '.'.join(first_part[0]) + '.' + str(int(last_part[0]) + 55)},
                    {"Device": "Оборудование ПЭС(ЦХМ)", "IP": '.'.join(first_part[0]) + '.' + str(int(last_part[0]) + 59)},
                    {"Device": "Оборудование ПЭС(АСКУЭ)АССД", "IP": '.'.join(first_part[0]) + '.' + str(int(last_part[0]) + 60)},
                    {"Device": "Оборудование ПЭС(Умный щит)", "IP": '.'.join(first_part[0]) + '.' + str(int(last_part[0]) + 61)},
                    {"Device": "Шлюз", "IP": '.'.join(first_part[0]) + '.' + str(int(last_part[0]) + 33)},
                    {"Device": "Маска", "IP": "255.255.255.224"}
                ]
                vlan_messages.append({
                    "VLAN": 4,
                    "Description": "Для устройств, которым не требуется взаимодействие с сервером BO",
                    "Devices": vlan_4_devices
                })

                # VLAN 8
                vlan_8_devices = [
                    {"Device": "МФУ", "IP": '.'.join(first_part[0]) + '.' + str(int(last_part[0]) + 18)},
                    {"Device": "Принтер", "IP": '.'.join(first_part[0]) + '.' + str(int(last_part[0]) + 19)},
                    {"Device": "Сервер электронных ценников ESL", "IP": '.'.join(first_part[0]) + '.' + str(int(last_part[0]) + 25)},
                    {"Device": "Точки доступа электронных ценников",
                     "IP": '.'.join(first_part[0]) + '.' + str(int(last_part[0]) + 26) + "-" + '.'.join(first_part[0]) + '.' + str(int(last_part[0]) + 30)},
                    {"Device": "Шлюз", "IP": '.'.join(first_part[0]) + '.' + str(int(last_part[0]) + 17)},
                    {"Device": "Маска", "IP": "255.255.255.240"}
                ]
                vlan_messages.append({
                    "VLAN": 8,
                    "Description": "Для устройств, которым требуется доступ по UDP к системам снаружи магазина и к серверу BO",
                    "Devices": vlan_8_devices
                })

                # VLAN 2
                vlan_2_devices = [
                    {"Device": "Стационарный термопринтер", "IP": "192.168.3.25-26"},
                    {"Device": "Весы для касс самообслуживания (SWS)(Даркстор)", "IP": "192.168.3.30-32"},
                    {"Device": "Прайсчекер WINCE", "IP": "192.168.3.100-103"},
                    {"Device": "Шлюз", "IP": "192.168.3.1"},
                    {"Device": "Маска", "IP": "255.255.255.0"}
                ]
                vlan_messages.append({
                    "VLAN": 2,
                    "Description": "Для устройств, подключаемых по проводу и которым не требуется прямой доступ к внешним системам",
                    "Devices": vlan_2_devices
                })

                # VLAN 33
                vlan_33_devices = [
                    {"Device": "Мобильный принтер", "IP": "192.168.1.10-14"},
                    {"Device": "Весы для касс самообслуживания (SWS)(Даркстор)", "IP": "192.168.1.16-18"},
                    {"Device": "Шлюз", "IP": "192.168.1.1"},
                    {"Device": "Маска", "IP": "255.255.255.0"}
                ]
                vlan_messages.append({
                    "VLAN": 33,
                    "Description": "Для устройств, подключаемых по Wi-Fi и которым не требуется прямой доступ к внешним системам",
                    "Devices": vlan_33_devices
                })

        send_vlan_messages(bot, chat_id, vlan_messages)
        return JsonResponse({"messages": vlan_messages}, safe=False)

    except Exception:
        return "Что то пошло не так! Данное значение не является SAP или объект ещё не внесен в базу!"

