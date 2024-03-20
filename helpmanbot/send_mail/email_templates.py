class EmailTemplates:
    def __init__(self):
        self.templates = {
            "atol_serial_script": "Добрый день!\n\nМы являемся представителями компании X5 Retail Group.\n\nПрошу прислать скрипт для смены ЗН на ФР model.\n\nЗН ККТ в ремонте repair_sn\n\nЗН ККТ подменная substitute_sn\n\nФото тестового прогона во вложении.\n\nИдентификационные данные ККТ корректны;\n\n\"UIN: uin_asc",
            # Другие тексты писем здесь
        }

    def get_template(self, key):
        return self.templates.get(key, "Шаблон письма не найден.")
