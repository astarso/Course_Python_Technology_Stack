# Урок №6: Циклы и условия в Python

# Задание №1
"""
Подсчет количества чисел, равных нулю.

Сначала вводится число N, затем вводится ровно N целых чисел.
Программа подсчитывает, сколько из них равны нулю, и выводит это количество.

Пример ввода:
Введите число N: 5
Введите число: 0
Введите число: 7
Введите число: 0
Введите число: -3
Введите число: 0

Пример вывода:
Количество чисел, равных нулю: 3
"""

N = int(input("Введите число N: "))
count = 0
i = 0

while i < N:
    num = int(input("Введите число: "))
    if num == 0:
        count += 1
    i += 1

print("Количество чисел, равных нулю:", count)


# Задание №2
"""
Подсчет количества натуральных делителей числа.

Вводится натуральное число X. Программа подсчитывает количество
натуральных делителей числа X (включая 1 и само число).

Ограничение: x ≤ 2e9 (2 миллиарда)

Пример ввода:
Введите натуральное число X: 12

Пример вывода:
Количество натуральных делителей числа 12: 6
"""

X = int(input("Введите натуральное число X: "))
divisors_count = 0

for i in range(1, X + 1):
    if X % i == 0:
        divisors_count += 1

print(f"Количество натуральных делителей числа {X}: {divisors_count}")


# Задание №3
"""
Вывод четных чисел на заданном отрезке.

Вводятся целые числа A и B (гарантируется, что A ≤ B).
Программа выводит все четные числа на заданном отрезке через пробел.

Пример ввода:
Введите число A: 3
Введите число B: 10

Пример вывода:
Четные числа на отрезке [3, 10]: 4 6 8 10
"""

A = int(input("Введите число A: "))
B = int(input("Введите число B: "))

print(f"Четные числа на отрезке [{A}, {B}]:", end=" ")
for num in range(A, B + 1):
    if num % 2 == 0:
        print(num, end=" ")
