import locale
import os

def clear_screen():
    """
    Clear screen

    You can use this function to clear console, and it can adapt to different OS.
    """
    if os.name == 'nt': # 如果是Windows
        os.system('cls')
    else: # 如果是Mac或Linux
        os.system('clear')


def menu(menu_list: list) -> int:
    """
    Menu

    This is a console tool

    It can receive a menu list and display it in the form of menu.

    When the user uses the keyboard to make a choice, it will return user’s choice.

    It contains a loop, so it returns the value entered by the user only if the user enters a correct number
    """
    default_locale = locale.getlocale()
    default_language = default_locale[0]

    choice_num = 0

    while True:
        num = 0
        for item in menu_list:
            num += 1
            print(f"{num}.{item}")
        if "English" in default_language:
            print("0.Quit")
        elif "Chinese" in default_language:
            print("0.退出")

        try:
            choice_str = ""
            if "English" in default_language:
                choice_str = input("Please input a number:")
            elif "Chinese" in default_language:
                choice_str = input("请输入序号：")
            choice_num = int(choice_str)
            if choice_num > len(menu_list):
                if "English" in default_language:
                    print("Number out of range.")
                elif "Chinese" in default_language:
                    print("输入超出范围。")
                continue
            break
        except KeyboardInterrupt:
            os.system("cls")
            print("程序结束\n")
            return 0
        except ValueError:
            print("输入数字不为整数，请重新输入")

    return choice_num