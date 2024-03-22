class EmailTemplates:
    def __init__(self):
        self.templates = {
            "atol_serial_script": "Добрый день!\n\nМы являемся представителями компании X5 Retail Group.\n\nПрошу прислать скрипт для смены ЗН на ФР model.\n\nЗН ККТ в ремонте repair_sn\n\nЗН ККТ подменная substitute_sn\n\nФото тестового прогона во вложении.\n\nИдентификационные данные ККТ корректны;\n\nUIN: uin_ask",
            "atol_licenses": "Добрый день!\n\nМы являемся представителями компании X5 Retail Group.\n\nПрошу прислать лицензию для работы с ФФД 1.2 и марированными товарами\n\nФР модель model\n\nСерийный номер: serial_nember\n\n Фото с версией прошивки во вложении",
            "atol_uin": "Добрый день!\n\nМы являемся представителями компании X5 Retail Group.\n\nПрошу прислать скрипт для записи UIN на плату.\n\nФР модель: model\n\nСерийный номер: serial_number\n\nИдентификационные данные ККТ не корректны;\n\nUIN:"
        }

    def get_template(self, key):
        return self.templates.get(key, "Шаблон письма не найден.")
