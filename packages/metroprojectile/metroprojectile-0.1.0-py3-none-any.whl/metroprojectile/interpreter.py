import sys
from pathlib import Path
from .core import game, physics  # Импорт модулей MP

class MPInterpreter:
    def __init__(self):
        self.variables = {}
        self.functions = {}
        
    def execute(self, code: str):
        """Выполняет MP-код"""
        try:
            # Упрощённый парсер (заглушка)
            for line in code.split('\n'):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Обработка переменных
                if line.startswith('var '):
                    name, value = line[4:].split('=', 1)
                    self.variables[name.strip()] = eval(value.strip(), {}, self.variables)
                
                # Обработка print
                elif line.startswith('print('):
                    expr = line[6:-1]
                    print(eval(expr, {}, self.variables))
                
                # Обработка game/physics
                elif 'game.' in line or 'phys.' in line:
                    eval(line, {'game': game, 'phys': physics, **self.variables})
                    
        except Exception as e:
            print(f"MP Ошибка: {e}")

def run_mp_script(file_path: str):
    """Запускает MP-скрипт из файла"""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Файл {file_path} не найден")
    
    interpreter = MPInterpreter()
    interpreter.execute(path.read_text(encoding='utf-8'))

def main():
    if len(sys.argv) < 2:
        print("Использование: mp <файл.mp>")
        sys.exit(1)
    
    try:
        run_mp_script(sys.argv[1])
    except Exception as e:
        print(f"Ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
