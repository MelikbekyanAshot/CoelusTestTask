# Решение задачи вымощения ограниченной плоскости 

## Краткая постановка задачи
Необходимо определить, возможно ли выполнить замощение ограниченной плоскости, используя прямоугольные полиомино и П-полиомино с заданными параметрами.

## Решение
Для решения поставленной задачи использовалась библиотека [ortools](https://developers.google.com/optimization/cp/cp_solver). 
В ходе решения не удалось выполнить задачу для П-полиомино. Программа работает только для прямоугольных полиомино. 

## Пример работы
### Положительный пример
Введем размер таблицы 4х6, 2 квадрата 2х2 и 1 прямоугольник 1х4 и получим решение. 
```
Enter table's width and height: 
>> 4 6
Enter total rectangles type amount: 
>> 2
Enter width, height and amount of each rectangle: 
>> 2 2 2
Enter width, height and amount of each rectangle: 
>> 1 4 1
You entered:
table size: (4, 6)
rectangles: [(2, 2), (2, 2), (1, 4)]
Solution is found!
```
![](images/example_solution.png)

### Отрицательный пример
Приведем пример отсутствия решения
В таблицу 4х6 невозможно упаковать 2 квадрата 2х2 и прямоугольник 1х7.
```
Enter table's width and height: 4 6
Enter total rectangles type amount: 2
Enter width, height and amount of each rectangle: 2 2 2
Enter width, height and amount of each rectangle: 1 7 1
You entered:
table size: (4, 6)
rectangles: [(2, 2), (2, 2), (1, 7)]
Solution is not found!
```