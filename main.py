# Урок №7: Строки

# Задание №1
"""
Определение палиндрома.

На вход подается 1 строка без пробелов. Программа определяет,
является ли строка палиндромом, и выводит "yes", если это так,
и "no" в противном случае.

Пример ввода:
Введите строку: radar

Пример вывода:
yes
"""

input_string = input("Введите строку: ")
reversed_string = input_string[::-1]

if input_string == reversed_string:
    print("yes")
else:
    print("no")


# Задание №2
"""
Удаление лишних пробелов.

Дана строка, длина которой не превосходит 1000. Программа
преобразует все идущие подряд пробелы в один и выводит
измененную строку.

Пример ввода:
Введите строку: Hello     world!   How   are you?

Пример вывода:
Hello world! How are you?
"""

input_string = input("Введите строку: ")
formatted_string = ' '.join(input_string.split())

print(formatted_string)
