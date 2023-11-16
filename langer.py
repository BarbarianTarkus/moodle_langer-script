from prettytable import PrettyTable
import os
from dotenv import load_dotenv
import deepl
import inquirer
import json

load_dotenv()
# Load the translations from a file
try:
    with open("translation_cache.json", "r") as f:
        translation_cache = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    translation_cache = {}


def get_translation(original, lang):
    """
    Get the translation of a text. If the translation is cached, return the cached version.
    Otherwise, get the translation from DeepL and cache it.
    """
    
    # Check if the translation is in the cache
    if original in translation_cache:
        return translation_cache[original]

    # If not, get the translation from DeepL
    translation = deepl_translate(original, lang)

    # Convert the TextResult object to a string
    translation_str = str(translation)

    # Store the string in the cache
    translation_cache[original] = translation_str

    # Write the cache to a file
    with open("translation_cache.json", "w") as f:
        json.dump(translation_cache, f)

    return translation_str


def file_open():
    """
    Open a file and return its lines and name.
    """
    
    # read file
    print("Drag and drop the PHP file")
    print("The file has to be part of the english lang version of the plugin")
    print("Example: the_best_plugin.php")
    file = input().strip("'")

    # get file name
    file_name = os.path.basename(file)

    open_file = open(file, "r")

    read_file = open_file.read()

    # split file
    lines = read_file.splitlines()

    return lines, file_name


def choose_lang(file_name):
    """
    Ask the user for the language code to translate to and return it.
    """
    
    # Input the lang code you want to translate
    print("Input the lang code you want to translate for example: es")
    lang = input()
    if not os.path.exists("lang"):
        os.mkdir("lang")
    if not os.path.exists(f"lang/{lang}"):
        os.mkdir(f"lang/{lang}")
    return lang


def get_fields(line):
    """
    Split a line into a variable and a value and return them.
    """
    split_line = line.split("=")
    # get the var
    var = split_line[0].strip()
    # get the value
    value = split_line[1].strip()
    value = value.replace("'", "")
    value = value.replace('"', "")
    value = value.replace(";", "")

    return var, value


def build_table(lang):
    """
    Build a PrettyTable with the field names "Original" and "Translated(lang)" and return it.
    """
    table = PrettyTable()
    table.field_names = ["Original", f"Translated({lang})"]
    # Print the table
    return table


def deepl_translate(value, lang):
    """
    Translate a text using DeepL and return the translated text.
    """
    auth_key = os.environ.get("AUTH_KEY")
    translator = deepl.Translator(auth_key)
    value = translator.translate_text(value, target_lang=lang.upper())
    return value


def one_line_translate(value, lang):
    """
    Ask the user how they want to translate a text and return the translated text.
    """
    print(f"How do you want to translate this text: {value}")
    # Define the options
    options = ["[1] Deepl(auto)", "[2] Manual Translation"]

    # Ask the user to select an option
    questions = [
        inquirer.List(
            "choice",
            message=f"[{value}] - Choose translation mode",
            choices=options,
        ),
    ]

    answers = inquirer.prompt(questions)

    # Handle the user's selection
    if answers["choice"].startswith("[2]"):
        print(f"Enter translation for {value}:")
        value = input()
    elif answers["choice"].startswith("[1]"):
        value = get_translation(value, lang)
    return value


def choose_translation_mode():
    """
    Ask the user to choose a translation mode and return the chosen mode.
    """
    print("Choose translation mode")
    
    # Define the options
    options = ["Entire file", "Line by line"]

    # Ask the user to select an option
    questions = [
        inquirer.List(
            "choice",
            message="Choose translation mode",
            choices=options,
        ),
    ]

    answers = inquirer.prompt(questions)

    # Return the user's selection
    return answers["choice"]


def main():
    """
    Main function of the program. Handles the file opening, language selection, translation, and writing to the output file.
    """
    print("Welcome to Langer!")
    
    lines, file_name = file_open()

    lang = choose_lang(file_name)

    write_file = open(f"lang/{lang}/{file_name}", "w", encoding="utf8")

    table = build_table(lang)

    translation_mode = choose_translation_mode()

    print(f"Translating... to {lang}")

    if translation_mode == "Entire file":
        for line in lines:
            if "$string" in line:
                # split line
                var, original = get_fields(line)
                # select if you want to translate automatically or manually

                translation = get_translation(original, lang)

                write_file.write(f"{var} = '{translation}';\n")
                table.add_row([original, translation])
                os.system("cls" if os.name == "nt" else "clear")
                print(table)
            else:
                write_file.write(f"{line}\n")
        write_file.close()
    if translation_mode == "Line by line":
        for line in lines:
            if "$string" in line:
                # split line
                var, original = get_fields(line)
                # select if you want to translate automatically or manually

                translation = one_line_translate(original, lang)

                write_file.write(f"{var} = '{translation}';\n")
                table.add_row([original, translation])
                # Clear the command line output
                os.system("cls" if os.name == "nt" else "clear")

                print(table)
            else:
                write_file.write(f"{line}\n")
        write_file.close()


if __name__ == "__main__":
    main()
