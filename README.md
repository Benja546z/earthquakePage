# earthquakePage paso a paso

## Clonar el repositorio [Requiere Git Bash]
- Ubicar el archivo con `cd [lugar]`
- Clonar el repositorio con `git clone https://github.com/Benja546z/earthquakePage.git`
- Entrar a la carpeta clonada con `cd earthquakePage`
- Descargar los archivos pesados (Requiere Git LFS) con `git lfs pull`
- Abrir el editor con `code .`

## Terminal Visual Studio Code
- Crear una nueva terminal

Escribir en orden los siguientes comandos:
- `py -m venv .venv`
- `Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process`
- `.\.venv\Scripts\Activate.ps1`
- `py -m pip install --upgrade pip`
- `pip install Django==5.1.14`
- `pip install -r requirements.txt`
- Iniciar servidor con `py manage.py runserver`
