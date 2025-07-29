def file_read(file_path, expansion=".txt", encoding="utf-8"):
    reading_file = f"{file_path}{expansion}"
    print(reading_file)
    with open(reading_file, 'r', encoding=encoding) as file:
        content = file.read()
    return content

#Create by Xwared Team and Dovintc, Project SUWWP - Speeding up Work with Python (SUW2P)