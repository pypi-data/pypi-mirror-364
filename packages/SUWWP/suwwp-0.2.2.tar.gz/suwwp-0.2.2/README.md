## **📦 SUWWP V0.2.01 - Speeding up Work with Python (SUW2P)**
# Create by Xwared Team and Dovintc, Project SUWWP - Speeding up Work with Python (SUW2P)

Инструмент для ускоренной работы
с данными в Python

## Функции:

# 1. time_now(format="YHMS", sep="str", help="bool"):

print(time_now(format="HM")) 
выводит время в формате HH:MM
вывод: 09:33

print(time_now(format="jHM"))
выдаст ошибку "ValueError("Invalid format character")"

print(time_now(format="HM", sep=" / "))
меняет разделитель на /, 
вывод: 09 / 33

print(time_now(format="YHMS", sep=":::"))
потдерживает любые форматы!
вывод: 2025:::09:::33:::53

print(time_now(format="MSв", help=True))
потдержка вспомогательных символов для более 
точного понятия часов минут и т.д. 
вывод: 33M:53S

# 2. file_read(file_path=str, expansion=".txt", encoding="utf-8"):
content = file_read(file_path="./file.txt")
вернет весь текст из файла 

# 3. structure_project(folder_path = ".", Mode="files", WMode=True):
structure_project(folder_path=".")
вернет только файлы (только их названия)

structure_project(folder_path=".", Mode="file-directory")
вернет не только файлы но и папки (также только их название)

structure_project(folder_path=".", Mode="file-directory", WMode=False)
вернет Mode вместе с папками и файлами в виде списка


# **Project SUWWP is being created by: *Xwared|Dovintc and Tooch1c*** 
**MIT License: *[LICENSE](https://github.com/Dovintc32/SUWWP?tab=MIT-1-ov-file)***