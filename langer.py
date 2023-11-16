import os
from dotenv import load_dotenv
import deepl


load_dotenv()


def file_open():
    # read file
    print("Drag and drop the file you want to translate")
    file = input()

    # get file name
    file_name = os.path.basename(file)

    open_file = open(file, "r")

    read_file = open_file.read()

    # split file
    lines = read_file.splitlines()

    return lines, file_name


def choose_lang(file_name):
    # Input the lang code you want to translate
    print("Input the lang code you want to translate for example: es")
    lang = input()
    if not os.path.exists(f"lang/{lang}"):
        os.mkdir(f"lang/{lang}")
    return lang


def get_fields(line):
    split_line = line.split("=")
    # get the var
    var = split_line[0].strip()
    # get the value
    value = split_line[1].strip()
    value = value.replace("'", "")
    value = value.replace('"', "")
    value = value.replace(";", "")

    return var, value


def main():
    lines, file_name = file_open()

    print("Do you want to translate automatically or manually? (auto/man)")

    lang = choose_lang(file_name)

    write_file = open(f"lang/{lang}/{file_name}", "w", encoding="utf8")
    choice = input()
    for line in lines:
        if "$string" in line:
            # split line
            var, value = get_fields(line)
            # select if you want to translate automatically or manually
            if choice == "auto":
                auth_key = os.environ.get("AUTH_KEY")
                translator = deepl.Translator(auth_key)
                value = translator.translate_text(value, target_lang=lang.upper())
            elif choice == "man":
                print(f"Enter translation for {value}:")
                value = input()

            value = translator.translate_text(value, target_lang=lang.upper())

            write_file.write(f"{var} = '{value}';\n")
        else:
            write_file.write(f"{line}\n")
