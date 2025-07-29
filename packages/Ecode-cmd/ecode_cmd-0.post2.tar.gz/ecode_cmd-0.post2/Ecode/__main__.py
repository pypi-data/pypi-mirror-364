#Ecode\__main__.py
import argparse
import random
import os
import subprocess
import sys
import time
from datetime import datetime
import pyttsx3
from termcolor import colored
def main():
    parser = argparse.ArgumentParser(description="Do you need a helpfull cmd? use Ecode.")
    subparsers = parser.add_subparsers(dest="command")

    # print
    print_parser = subparsers.add_parser("print", help="show a text.")
    print_parser.add_argument("text", nargs="+", help="text for show.")
    print_parser.add_argument("color",help="color of your text.",choices=["black", "red", "green", "yellow", "blue", "magenta", "cyan", "white", "light_grey", "dark_grey", "light_red", "light_green", "light_yellow", "light_blue","light_magenta", "light_cyan"],default="white")

    # rannumber
    subparsers.add_parser("rannumber", help="select a random number from 1 to 100.")

    # .
    subparsers.add_parser(".", help="show credits of Ecode")
    # run
    run_parser = subparsers.add_parser("run", help="run a command.")
    run_parser.add_argument("cmd",nargs=argparse.REMAINDER, help="command for run.")

    # open
    open_parser = subparsers.add_parser("open", help="open a file in Vscode.")
    open_parser.add_argument("filename", help="name of file")

    # create
    create_parser = subparsers.add_parser("create", help="create a file")
    create_parser.add_argument("filename", help="name of file")

    #remove
    remove_parser = subparsers.add_parser("remove", help="remove a file")
    remove_parser.add_argument("filename", help="name of file")

    #makedir
    makedir_parser = subparsers.add_parser("makedir",help="create a folder.")
    makedir_parser.add_argument("dirname", help="name of folder.")

    #say
    say_parser = subparsers.add_parser("say",help="say a text.")
    say_parser.add_argument("text",nargs=argparse.REMAINDER,help="text for say.")

    # env
    env_parser = subparsers.add_parser("env", help="Virtual Environment")
    env_parser.add_argument("venv_path", help="venv path")

    # save
    save_parser = subparsers.add_parser("save", help="save a file.")
    save_parser.add_argument("filename", help="output file.")

    # load
    load_parser = subparsers.add_parser("load", help="load a file.")
    load_parser.add_argument("filename", help="snapshot file.")

    # clear
    subparsers.add_parser("clear", help="clear cmd.")

    # time
    subparsers.add_parser("time", help="show the time")

    # listfiles
    subparsers.add_parser("listfiles", help="a list of files in the path")

    edit_parser = subparsers.add_parser("edit", help="edit a file.")
    edit_parser.add_argument("filename", help="file name for edit")

    start_parser = subparsers.add_parser("startfile", help="open a file.")
    start_parser.add_argument("path", help="path of the file.")
    # Parse
    args = parser.parse_args()

    # اجرای دستورات
    
    if args.command == "print":
        
        text=">>>", " ".join(args.text)
        print()

    elif args.command == "rannumber":
        print("🎲random number:", random.randint(1, 100))

    elif args.command == ".":
        print("credits:")
       
        print(colored("Amirali","green"))
        print(colored("Amirali","green"))
        print(colored("Amirali","green"))
        print(colored("Amirali","green"))
        print(colored("Amirali","green"))
        print(colored("Amirali","green"))
        print(colored("Batman🦇","white"))
        print(colored("Amirali","green"))
        print(colored("Amirali","green"))
        print(colored("Amirali","green"))
        print(colored("Amirali","green"))
        print(colored("Amirali","green"))
    elif args.command == "run":
        full_cmd = " ".join(args.cmd)
        print("command is running:", full_cmd)
        os.system(full_cmd)

    elif args.command == "edit":
        print(f"📝 open file {args.filename} in notpad.")
        try:
            os.system(f'notepad "{args.filename}"')  # فقط برای ویندوز
        except Exception as e:
            print("❌ error:", e)
    elif args.command == "startfile":
        print(f"📂 open file: {args.path}")
        try:
            os.startfile(args.path)  # فقط ویندوز
        except AttributeError:
            # اگر ویندوز نبود
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, args.path])
        except Exception as e:
            print("❌ error:", e)
    elif args.command == "open":
        print(f"📂 open file: {args.filename}")
        os.system(f'code "{args.filename}"')

    elif args.command == "create":
        with open(args.filename, "w", encoding="utf-8") as f:
            f.write("")  # فایل خالی
        print(f"📄 file is created: {args.filename}")
    elif args.command == "remove":
        print(f"🗑️ file removed:{args.filename}")
        os.remove(args.filename)
    elif args.command == "makedir":
        os.mkdir(args.dirname)

    elif args.command == "say":
        engine=pyttsx3.Engine()
        engine.say(str(args.text))
        engine.runAndWait()

    elif args.command == "env":
        path = os.path.join(args.venv_path, "Scripts", "activate")
        print(f"🔧 code: {path}")
        os.system(path)


    elif args.command == "save":
        with open(args.filename, "w", encoding="utf-8") as f:
            f.write("# Snapshot Example\n")
            f.write(f"# time of saveL {datetime.now()}\n")
            f.write(f"# files:\n")
            for item in os.listdir():
                f.write(f"- {item}\n")
        print(f"💾 snapshot ذخیره شد در: {args.filename}")

    elif args.command == "load":
        if not os.path.exists(args.filename):
            print("⛔ can't find your file.")
        else:
            with open(args.filename, "r", encoding="utf-8") as f:
                print("📄 data of snapshot:")
                print(f.read())

    elif args.command == "clear":
        os.system("cls" if os.name == "nt" else "clear")

    elif args.command == "time":
        now = datetime.now()
        print("🕒 now time:", now.strftime("%Y-%m-%d %H:%M:%S"))

    elif args.command == "listfiles":
        files = os.listdir()
        print("📂 list of files:")
        for f in files:
            print("-", f)
    else:
        parser.print_help()
if __name__=="__main__":
    main()
else:
    print(colored("Ecode-CMD vertion 0.2","green"))
    print(colored("Do you need a help full cmd? use Ecode script.","yellow"))

