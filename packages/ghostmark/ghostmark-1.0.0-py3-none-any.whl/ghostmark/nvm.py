import pyautogui
import time
import random
import string
import subprocess
import os
import shutil

filename = input("Enter the name of the file (without extension): ").strip()
if not filename:
    print("Filename cannot be empty!")
    exit()

filename += '.py'

script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, filename)

with open(file_path, 'w') as f:
    pass

print(f"Created: {file_path}")

# Check if VS Code is installed and 'code' command is available
if shutil.which("code") is not None:
    subprocess.Popen(["code", file_path])
    print("Opening file in VS Code...")
else:
    print("VS Code ('code' command) not found. Please open the file manually.")

time.sleep(5)

def generate_codeline():
    functions = ['process', 'handle', 'generate', 'fetch', 'calculate']
    variables = ['data', 'result', 'value', 'input', 'output']
    operations = ['+', '-', '*', '//', '%']

    templates = [
        f"def {random.choice(functions)}{random.randint(1, 100)}():",
        f"    {random.choice(variables)} = {random.randint(1, 10)} {random.choice(operations)} {random.randint(1, 10)}",
        f"    return {random.choice(variables)}",
        f"{random.choice(variables)} = {random.randint(100, 999)}",
        f"print({random.choice(variables)})"
    ]

    return random.choice(templates)

def type_line_like_human(line):
    for char in line:
        pyautogui.write(char)
        time.sleep(random.uniform(0.03, 0.1))  # Human typing delay
    pyautogui.press('enter')

print("Hacking time started... Press Ctrl+C to stop.")

try:
    while True:
        line = generate_codeline()
        type_line_like_human(line)
        time.sleep(random.uniform(0.3, 0.7))  # Short pause between lines
except KeyboardInterrupt:
    print("\nStopped by user.")
