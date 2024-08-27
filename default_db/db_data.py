import datetime

from werkzeug.security import generate_password_hash

default_data = {
    'GroupSi': [
        {'name': 'Радиотехнические и радиоэлектронные измерения'},
        {'name': 'Измерения электрических и магнитных величин'},
        {'name': 'Измерения параметров потока, расхода, уровня, объма веществ'},
        {'name': 'Теплофизические и температурные измерения'},
        {'name': 'Измерения давления, вакуумные измерения'},
        {'name': 'Измерения времени и частоты'},
        {'name': 'Измерения механических величин'},
        {'name': 'Измерения физико-химического состава и свойств веществ'},
        {'name': 'Оптические и оптико-физические измерения'},
        {'name': 'Виброакустические измерения'},
        {'name': 'Измерения характеристик ионизирующих излучений и ядерных констант'},
        {'name': 'Измерения электрических и магнитных величин, радиотехнические и радиоэлектронныя измерения'},
        {'name': 'Геометрические измерения'},
    ],
    'NameSi': [
        {'name': 'Амперметр'},
        {'name': 'Анализатор '},
        {'name': 'Вакуумметр'},
        {'name': 'Весы'},
        {'name': 'Вольтметр'},
        {'name': 'Генератор'},
        {'name': 'Дозиметр'},
        {'name': 'Источник питания'},
        {'name': 'Магазин емкости'},
        {'name': 'Манометр'},
        {'name': 'Мегаомметр'},
        {'name': 'Мультиметр'},
        {'name': 'Осциллограф'},
        {'name': 'Радиометр'},
        {'name': 'Спектрофотометр'},
        {'name': 'Тераомметр'},
        {'name': 'Частотомер'},
        {'name': 'Штангенциркуль'},
    ],
    'TypeSi': [
        {'name': 'АТН-1333'},
        {'name': 'SPS-3610'},
        {'name': 'MPS-6005L-1'},
        {'name': 'GPR-30H10D'},
        {'name': 'GPR-50H15D'},
        {'name': 'GPR-6030D'},
        {'name': 'GPS-4303'},
        {'name': 'GPS-3030DD'},
        {'name': 'GPS-4304'},
        {'name': 'GPS-3030D'},
        {'name': 'HY3005D-2'},
        {'name': 'GPR-3030DD'},
        {'name': 'GPR-30Н10D'},
        {'name': 'АКИП-1105'},
        {'name': 'GPR-711H30D'},
        {'name': 'PWS 4205'},
        {'name': 'APS-7205L'},
        {'name': '6633В'},
        {'name': 'Е3631А'},
        {'name': 'N6751А'},
        {'name': 'NI PXI-4110'},
    ],
    'ServiceType': [
        {'name': 'Аттестация'},
        {'name': 'Калибровка'},
        {'name': 'Поверка'},
    ],
    'ServiceInterval': [
        {'name': 12},
        {'name': 24},
        {'name': 30},
        {'name': 36},
        {'name': 48},
        {'name': 60},
        {'name': 120},
    ],
    'DescriptionMethod': [
        {'name': 'описание типа 1'},
        {'name': 'описание типа 2'},
        {'name': 'описание типа 3'},
    ],
    'Place': [
        {'name': 'Собственная база'},
        {'name': 'Сторонняя организация'},
    ],
    'Room': [
        {'name': '082'},
        {'name': '283'},
        {'name': '286'},
        {'name': '287'},
    ],
    'StatusService': [
        {'name': 'В ремонте'},
        {'name': 'Забракован'},
        {'name': 'Готово к выдачи'},
        {'name': 'На обслуживании'},
    ],
    'Division': [
        {'name': 'Отдел'},
        {'name': 'Сектор'},
        {'name': 'Лаборатория'},
        {'name': 'Управление'},
        {'name': 'Группа'},
    ],
    'Employee': [
        {
            'last_name': 'Гфамилия',
            'first_name': 'Аимя',
            'middle_name': 'Уотчество',
            'email': 'a@a.ru',
            'division_id': 1,
        },
        {
            'last_name': 'Уфамилия',
            'first_name': 'Димя',
            'middle_name': 'Ботчество',
            'email': 'b@a.ru',
            'division_id': 2,
        },
        {
            'last_name': 'Кфалилия',
            'first_name': 'Пимя',
            'middle_name': 'Мотчество',
            'email': 'c@a.ru',
            'division_id': 3,
        },
    ],
    'Si': [
        {
            'group_si_id': 1,
            'name_si_id': 1,
            'type_si_id': 1,
            'number': 'C012177',
            'service_type_id': 1,
            'service_interval_id': 1,
            'etalon': 0,
            'category_etalon': '2',
            'year_production': 1999,
            'nomenclature': '1111',
            'room_use_etalon': 1,
            'description_method_id': 1,
            'place_id': 1,
            'control_vp': True,
            'room_delivery_id': 1,
            'employee_id': 1,
            'date_last_service': datetime.datetime(2000, 0o1, 0o2),
            'date_next_service': datetime.datetime(2001, 0o1, 0o2),
            'is_service': False,
        },
        {
            'group_si_id': 2,
            'name_si_id': 2,
            'type_si_id': 2,
            'number': 'У010258',
            'service_type_id': 1,
            'service_interval_id': 1,
            'etalon': False,
            'category_etalon': '2',
            'year_production': 2010,
            'nomenclature': '2222',
            'room_use_etalon': 2,
            'description_method_id': 1,
            'place_id': 1,
            'control_vp': True,
            'room_delivery_id': 1,
            'employee_id': 2,
            'date_last_service': datetime.datetime(2010, 0o1, 0o2),
            'date_next_service': datetime.datetime(2011, 0o1, 0o2),
            'is_service': True,
        },
        {
            'group_si_id': 3,
            'name_si_id': 3,
            'type_si_id': 3,
            'number': '216103515060337',
            'service_type_id': 1,
            'service_interval_id': 1,
            'etalon': 0,
            'category_etalon': '2',
            'year_production': 2020,
            'nomenclature': '3333',
            'room_use_etalon': 1,
            'description_method_id': 1,
            'place_id': 1,
            'control_vp': True,
            'room_delivery_id': 1,
            'employee_id': 3,
            'date_last_service': datetime.datetime(2020, 0o1, 0o2),
            'date_next_service': datetime.datetime(2021, 0o1, 0o2),
            'is_service': True,
        },
        {
            'group_si_id': 4,
            'name_si_id': 4,
            'type_si_id': 4,
            'number': 'GCQ860140',
            'service_type_id': 1,
            'service_interval_id': 1,
            'etalon': 0,
            'category_etalon': '2',
            'year_production': 2020,
            'nomenclature': '4444',
            'room_use_etalon': 3,
            'description_method_id': 1,
            'place_id': 1,
            'control_vp': True,
            'room_delivery_id': 1,
            'employee_id': 2,
            'date_last_service': datetime.datetime(2020, 0o1, 0o2),
            'date_next_service': datetime.datetime(2021, 0o1, 0o2),
            'is_service': False,
        },
        {
            'group_si_id': 5,
            'name_si_id': 5,
            'type_si_id': 5,
            'number': '19629/19339',
            'service_type_id': 1,
            'service_interval_id': 1,
            'etalon': 0,
            'category_etalon': '2',
            'year_production': 2020,
            'nomenclature': '5555',
            'room_use_etalon': 2,
            'description_method_id': 1,
            'place_id': 1,
            'control_vp': True,
            'room_delivery_id': 1,
            'employee_id': 3,
            'date_last_service': datetime.datetime(2020, 0o1, 0o2),
            'date_next_service': datetime.datetime(2021, 0o1, 0o2),
            'is_service': False,
        },
    ],
    'Service': [
        {
            'si_id': 1,
            'date_in_service': datetime.datetime(2001, 0o1, 0o2),
            'is_out': True,
        },
        {
            'si_id': 1,
            'date_in_service': datetime.datetime(2002, 0o1, 0o2),
            'is_out': True,
        },
        {
            'si_id': 1,
            'date_in_service': datetime.datetime(2003, 0o1, 0o2),
            'is_out': True,
        },
        {
            'si_id': 2,
            'date_in_service': datetime.datetime(2010, 0o1, 0o2),
            'is_out': False,
        },
        {
            'si_id': 3,
            'date_in_service': datetime.datetime(2020, 0o1, 0o2),
            'is_out': False,
        },
    ],
    'UserProfile': [
        {
            'username': 'admin',
            'password': generate_password_hash('123'),
            'last_name': 'фамилия админа',
            'first_name': 'Имя админа',
            'middle_name': 'Отчество админа',
            'email': 'admin@si.ru',
            'is_active': True,
        },
        {
            'username': 'user',
            'password': generate_password_hash('123'),
            'last_name': 'фамилия юзера',
            'first_name': 'Имя юзера',
            'middle_name': 'Отчество юзера',
            'email': 'user@si.ru',
            'is_active': True,
        },
    ],
}