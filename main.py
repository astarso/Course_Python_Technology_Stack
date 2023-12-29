# Урок №11: Функции

import collections

# Словарь с информацией о питомцах
pets = {
    1: {
        "Мухтар": {
            "Вид питомца": "Собака",
            "Возраст питомца": 9,
            "Имя владельца": "Павел"
        }
    },
    2: {
        "Каа": {
            "Вид питомца": "желторотый питон",
            "Возраст питомца": 19,
            "Имя владельца": "Саша"
        }
    }
}

def create():
    last = collections.deque(pets, maxlen=1)[0]
    pet_name = input("Введите имя питомца: ")
    pet_species = input("Введите вид питомца: ")
    pet_age = int(input("Введите возраст питомца: "))
    pet_owner = input("Введите имя владельца: ")
    last += 1
    pets[last] = {pet_name: {"Вид питомца": pet_species, "Возраст питомца": pet_age, "Имя владельца": pet_owner}}

def get_pet(ID):
    return pets[ID] if ID in pets.keys() else False

def get_suffix(age):
    if age == 1:
        return "год"
    elif 1 < age < 5:
        return "года"
    else:
        return "лет"

def pets_list():
    for pet_id, pet_info in pets.items():
        pet_name, pet_data = list(pet_info.items())[0]
        print(f'{pet_name} (ID: {pet_id}): Вид питомца: {pet_data["Вид питомца"]}, '
              f'Возраст питомца: {pet_data["Возраст питомца"]} {get_suffix(pet_data["Возраст питомца"])}, '
              f'Имя владельца: {pet_data["Имя владельца"]}')

def read():
    pet_id = int(input("Введите ID питомца: "))
    pet_info = get_pet(pet_id)
    if pet_info:
        pet_name, pet_data = list(pet_info.items())[0]
        print(f'Это {pet_data["Вид питомца"].lower()} по кличке "{pet_name}". '
              f'Возраст питомца: {pet_data["Возраст питомца"]} {get_suffix(pet_data["Возраст питомца"])}. '
              f'Имя владельца: {pet_data["Имя владельца"]}')
    else:
        print("Питомец с таким ID не найден.")

def update():
    pet_id = int(input("Введите ID питомца для обновления: "))
    pet_info = get_pet(pet_id)
    if pet_info:
        pet_name, pet_data = list(pet_info.items())[0]
        print("Текущая информация:")
        print(f'Это {pet_data["Вид питомца"].lower()} по кличке "{pet_name}". '
              f'Возраст питомца: {pet_data["Возраст питомца"]} {get_suffix(pet_data["Возраст питомца"])}. '
              f'Имя владельца: {pet_data["Имя владельца"]}')
        new_species = input("Введите новый вид питомца (Enter для сохранения текущего значения): ")
        new_age = int(input("Введите новый возраст питомца (Enter для сохранения текущего значения): "))
        new_owner = input("Введите новое имя владельца (Enter для сохранения текущего значения): ")
        if new_species:
            pet_data["Вид питомца"] = new_species
        if new_age:
            pet_data["Возраст питомца"] = new_age
        if new_owner:
            pet_data["Имя владельца"] = new_owner
        print("Информация обновлена.")
    else:
        print("Питомец с таким ID не найден.")

def delete():
    pet_id = int(input("Введите ID питомца для удаления: "))
    pet_info = get_pet(pet_id)
    if pet_info:
        pet_name, pet_data = list(pet_info.items())[0]
        print("Информация о питомце:")
        print(f'Это {pet_data["Вид питомца"].lower()} по кличке "{pet_name}". '
              f'Возраст питомца: {pet_data["Возраст питомца"]} {get_suffix(pet_data["Возраст питомца"])}. '
              f'Имя владельца: {pet_data["Имя владельца"]}')
        confirm = input("Вы уверены, что хотите удалить этого питомца? (y/n): ")
        if confirm.lower() == 'y':
            del pets[pet_id]
            print("Питомец удален.")
        else:
            print("Удаление отменено.")
    else:
        print("Питомец с таким ID не найден.")

# Основной цикл программы
command = ""
while command != 'stop':
    print("\nВыберите команду:")
    print("1. Создать нового питомца")
    print("2. Просмотреть информацию о питомце")
    print("3. Обновить информацию о питомце")
    print("4. Удалить питомца")
    print("5. Показать список всех питомцев")
    print("stop. Завершить программу")
    command = input("Введите номер команды: ")

    if command == '1':
        create()
    elif command == '2':
        read()
    elif command == '3':
        update()
    elif command == '4':
        delete()
    elif command == '5':
        pets_list()

print("Программа завершена.")
