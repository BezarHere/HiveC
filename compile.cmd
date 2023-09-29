:: makes the script look cool d:
@color 20

:: changes the cur dir to the bat file dir 
@pushd "%~dp0"

:: set PYTHONOPTIMIZE=2
@pyinstaller --noconfirm --onefile --console --clean  "main.py"

@copy /y dist\main.exe C:\Windows\hivec.exe