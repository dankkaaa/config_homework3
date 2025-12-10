"""
Ассемблер для УВМ - Этап 2: Формирование машинного кода
=========================================================

Этап 2 реализует преобразование промежуточного представления в машинный код.

Новые возможности:
- Генерация машинного кода (байтов)
- Сохранение машинного кода в двоичный файл
- Вывод машинного кода в hex и decimal форматах
- Статистика по ассемблированию
"""

import argparse
import sys
from typing import List, Dict, Tuple


class Assembler:
    """Ассемблер для УВМ с поддержкой машинного кода (Этап 2)"""
    
    def __init__(self):
        # Таблица команд (опкоды)
        self.commands = {
            'LOAD':   0x01,
            'STORE':  0x02,
            'ADD':    0x03,
            'SUB':    0x04,
            'MUL':    0x05,
            'DIV':    0x06,
            'MOD':    0x07,
            'JMP':    0x08,
            'JZ':     0x09,
            'JNZ':    0x0a,
            'CMP':    0x0b,
            'CALL':   0x0c,
            'RET':    0x0d,
            'PUSH':   0x0e,
            'POP':    0x0f,
            'HALT':   0x10,
        }
        
        # Таблица регистров
        self.registers = {
            'A': 0x00,
            'B': 0x01,
            'C': 0x02,
            'D': 0x03,
        }
        
        # Внутреннее представление (из Этапа 1)
        self.instructions = []
        self.labels = {}
        self.errors = []
        self.source_lines = []
    
    def assemble(self, input_file: str):
        """Главный метод ассемблирования"""
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            self.source_lines = lines
            
            # Первый проход: поиск меток
            self._first_pass(lines)
            
            # Второй проход: генерация кода
            self._second_pass(lines)
            
            if self.errors:
                print("❌ ОШИБКИ АССЕМБЛИРОВАНИЯ:")
                for error in self.errors:
                    print(f"❌ {error}")
                sys.exit(1)
        
        except FileNotFoundError:
            print(f"❌ Ошибка: файл '{input_file}' не найден")
            sys.exit(1)
    
    def _first_pass(self, lines: List[str]):
        """Первый проход: поиск меток"""
        address = 0
        
        for line_num, line in enumerate(lines, 1):
            # Убрать комментарии
            if ';' in line:
                line = line[:line.index(';')]
            
            line = line.strip()
            
            if not line:
                continue
            
            # Поиск метки
            if ':' in line:
                label_name = line.split(':')[0].strip()
                self.labels[label_name] = address
                continue
            
            # Подсчёт адреса
            parts = line.split()
            if parts:
                command = parts[0].upper()
                if command in self.commands:
                    # Количество байтов для команды
                    if command == 'HALT' or command == 'RET':
                        address += 1
                    elif command in ['PUSH', 'POP']:
                        address += 2
                    else:
                        address += 3
    
    def _second_pass(self, lines: List[str]):
        """Второй проход: генерация машинного кода"""
        address = 0
        
        for line_num, line in enumerate(lines, 1):
            # Убрать комментарии
            if ';' in line:
                line = line[:line.index(';')]
            
            line = line.strip()
            
            if not line:
                continue
            
            # Пропустить метки
            if ':' in line:
                continue

            # Убрать комментарии
            if ';' in line:
                line = line[:line.index(';')]

            # ✅ ДОБАВИТЬ ЭТУ СТРОКУ:
            line = line.replace(',', ' ')

            line = line.strip()

            # Парсинг команды
            parts = line.split()
            if not parts:
                continue
            
            command = parts[0].upper()
            
            if command not in self.commands:
                self.errors.append(f"Строка {line_num}: Неизвестная команда '{command}'")
                continue
            
            # Создать инструкцию
            opcode = self.commands[command]
            operands = []
            
            try:
                # Парсинг операндов в зависимости от команды
                if command == 'HALT' or command == 'RET':
                    # Без операндов
                    pass
                
                elif command in ['PUSH', 'POP']:
                    # Один операнд (регистр)
                    reg = parts[1].upper() if len(parts) > 1 else None
                    if not reg or reg not in self.registers:
                        self.errors.append(f"Строка {line_num}: Неверный регистр '{reg}'")
                        continue
                    operands = [self.registers[reg]]
                
                elif command in ['JMP', 'JZ', 'JNZ', 'CALL']:
                    # Один операнд (метка или адрес)
                    label = parts[1] if len(parts) > 1 else None
                    if not label:
                        self.errors.append(f"Строка {line_num}: Не указана метка для {command}")
                        continue
                    
                    if label in self.labels:
                        addr = self.labels[label]
                    elif label.isdigit():
                        addr = int(label)
                    else:
                        self.errors.append(f"Строка {line_num}: Неизвестная метка '{label}'")
                        continue
                    
                    operands = [addr]
                
                elif command == 'CMP':
                    # Два операнда (два регистра)
                    if len(parts) < 3:
                        self.errors.append(f"Строка {line_num}: CMP требует двух регистров")
                        continue
                    
                    reg1 = parts[1].upper()
                    reg2 = parts[2].upper()
                    
                    if reg1 not in self.registers or reg2 not in self.registers:
                        self.errors.append(f"Строка {line_num}: Неверные регистры для CMP")
                        continue
                    
                    operands = [self.registers[reg1], self.registers[reg2]]

                elif command in ['ADD', 'SUB', 'MUL', 'DIV', 'MOD']:
                    if len(parts) < 3:
                        self.errors.append(f"Строка {line_num}: {command} требует двух операндов")
                        continue

                    reg1 = parts[1].upper()
                    op2_str = parts[2]

                    if reg1 not in self.registers:
                        self.errors.append(f"Строка {line_num}: Неверный регистр '{reg1}' для {command}")
                        continue

                    # второй операнд: либо регистр, либо число
                    if op2_str.upper() in self.registers:
                        op2 = self.registers[op2_str.upper()]
                    elif op2_str.startswith('0x'):
                        op2 = int(op2_str, 16)
                    else:
                        op2 = int(op2_str)

                    if not (0 <= op2 <= 255):
                        self.errors.append(f"Строка {line_num}: Операнд вне диапазона [0-255] для {command}")
                        continue

                    operands = [self.registers[reg1], op2]

                elif command == 'LOAD':
                    # Два операнда (регистр, значение или регистр)
                    if len(parts) < 3:
                        self.errors.append(f"Строка {line_num}: LOAD требует двух операндов")
                        continue
                    
                    reg = parts[1].upper()
                    value_str = parts[2]
                    
                    if reg not in self.registers:
                        self.errors.append(f"Строка {line_num}: Неверный регистр '{reg}'")
                        continue
                    
                    # Парсинг значения
                    if value_str.upper() in self.registers:
                        value = self.registers[value_str.upper()]
                    elif value_str.startswith('0x'):
                        value = int(value_str, 16)
                    else:
                        value = int(value_str)
                    
                    if not (0 <= value <= 255):
                        self.errors.append(f"Строка {line_num}: Значение вне диапазона [0-255]")
                        continue
                    
                    operands = [self.registers[reg], value]
                
                elif command == 'STORE':
                    # Два операнда (регистр, адрес)
                    if len(parts) < 3:
                        self.errors.append(f"Строка {line_num}: STORE требует двух операндов")
                        continue
                    
                    reg = parts[1].upper()
                    addr_str = parts[2]
                    
                    if reg not in self.registers:
                        self.errors.append(f"Строка {line_num}: Неверный регистр '{reg}'")
                        continue
                    
                    # Парсинг адреса
                    if addr_str.startswith('0x'):
                        addr = int(addr_str, 16)
                    else:
                        addr = int(addr_str)
                    
                    if not (0 <= addr <= 65535):
                        self.errors.append(f"Строка {line_num}: Адрес вне диапазона")
                        continue
                    
                    operands = [self.registers[reg], addr & 0xFF, (addr >> 8) & 0xFF]
                
                # Добавить инструкцию
                self.instructions.append({
                    'mnemonic': command,
                    'opcode': opcode,
                    'operands': operands,
                    'line': line_num,
                    'address': address
                })
                
                # Обновить адрес
                address += 1 + len(operands)
            
            except (ValueError, IndexError) as e:
                self.errors.append(f"Строка {line_num}: Ошибка парсинга: {e}")
    
    # ========== НОВЫЕ МЕТОДЫ ДЛЯ ЭТАПА 2 ==========
    
    def get_machine_code(self) -> List[int]:
        """
        Преобразует внутреннее представление в машинный код (список байтов).
        
        Returns:
            List[int]: Список байтов машинного кода
        """
        machine_code = []
        
        for instruction in self.instructions:
            # Добавить опкод
            machine_code.append(instruction['opcode'])
            
            # Добавить операнды
            for operand in instruction['operands']:
                machine_code.append(operand)
        
        return machine_code
    
    def save_to_binary_file(self, filename: str) -> int:
        """
        Сохраняет машинный код в двоичный файл.
        
        Args:
            filename: Имя файла для сохранения
        
        Returns:
            int: Количество сохранённых байтов
        """
        machine_code = self.get_machine_code()
        
        try:
            with open(filename, 'wb') as f:
                f.write(bytes(machine_code))
            
            return len(machine_code)
        
        except IOError as e:
            print(f"❌ Ошибка при сохранении файла: {e}")
            sys.exit(1)
    
    def get_hex_output(self) -> str:
        """
        Возвращает машинный код в шестнадцатеричном формате.
        
        Returns:
            str: Машинный код в формате '01 02 03 04 ...'
        """
        machine_code = self.get_machine_code()
        return ' '.join(f'{byte:02x}' for byte in machine_code)
    
    def get_hex_output_0x(self) -> str:
        """
        Возвращает машинный код в формате с префиксом 0x.
        
        Returns:
            str: Машинный код в формате '0x01 0x02 0x03 ...'
        """
        machine_code = self.get_machine_code()
        return ' '.join(f'0x{byte:02x}' for byte in machine_code)
    
    def get_dec_output(self) -> str:
        """
        Возвращает машинный код в десятичном формате.
        
        Returns:
            str: Машинный код в формате '1 2 3 4 ...'
        """
        machine_code = self.get_machine_code()
        return ' '.join(str(byte) for byte in machine_code)
    
    def get_statistics(self) -> Dict:
        """
        Возвращает статистику ассемблирования.
        
        Returns:
            Dict: Словарь со статистикой
        """
        machine_code = self.get_machine_code()
        
        return {
            'num_instructions': len(self.instructions),
            'num_bytes': len(machine_code),
            'num_labels': len(self.labels),
            'labels': self.labels
        }
    
    def print_test_output(self):
        """Выводит результат в формате теста из спецификации"""
        machine_code = self.get_machine_code()
        
        print("\n" + "="*60)
        print("РЕЗУЛЬТАТ АССЕМБЛИРОВАНИЯ (Этап 2)")
        print("="*60)
        
        # Статистика
        stats = self.get_statistics()
        print(f"\nСтатистика:")
        print(f"  Команд: {stats['num_instructions']}")
        print(f"  Байтов: {stats['num_bytes']}")
        print(f"  Меток: {stats['num_labels']}")
        
        # Машинный код HEX
        print(f"\nМашинный код (hex):")
        print(f"  {self.get_hex_output()}")
        
        # Машинный код DEC
        print(f"\nМашинный код (dec):")
        print(f"  {self.get_dec_output()}")
        
        # Таблица инструкций
        if self.instructions:
            print(f"\nТаблица инструкций:")
            print(f"  {'Адр':<4} {'Команда':<8} {'Опкод':<6} {'Операнды':<20}")
            print(f"  {'-'*50}")
            
            for instr in self.instructions:
                addr = instr['address']
                mnem = instr['mnemonic']
                opcode = f"0x{instr['opcode']:02x}"
                operands = ', '.join(f"0x{op:02x}" for op in instr['operands'])
                
                print(f"  {addr:<4} {mnem:<8} {opcode:<6} {operands:<20}")
        
        # Таблица меток
        if self.labels:
            print(f"\nТаблица меток:")
            for label, addr in self.labels.items():
                print(f"  {label:<20} : {addr}")
        
        print("="*60 + "\n")


def create_parser():
    """Создаёт парсер аргументов командной строки"""
    parser = argparse.ArgumentParser(
        description='Ассемблер для УВМ (Этап 2: Машинный код)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python assembler-stage2.py program.asm
  python assembler-stage2.py program.asm -o output.bin
  python assembler-stage2.py program.asm -t
  python assembler-stage2.py program.asm -v -t -o result.bin
        """
    )
    
    parser.add_argument(
        'input_file',
        help='Путь к исходному файлу ассемблера (.asm)'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Сохранить машинный код в двоичный файл'
    )
    
    parser.add_argument(
        '-t', '--test',
        action='store_true',
        help='Режим тестирования (выводить детальную информацию)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Подробный вывод'
    )
    
    return parser


def main():
    """Главная функция"""
    parser = create_parser()
    args = parser.parse_args()
    
    # Ассемблирование
    assembler = Assembler()
    assembler.assemble(args.input_file)
    
    # Получить машинный код
    machine_code = assembler.get_machine_code()
    stats = assembler.get_statistics()
    
    # Вывести информацию
    print(f"✓ Ассемблировано команд: {stats['num_instructions']}")
    print(f"✓ Размер машинного кода: {stats['num_bytes']} байт")
    
    # Вывести машинный код
    if args.verbose:
        print(f"\nМашинный код (hex):")
        print(assembler.get_hex_output())
    else:
        print(f"\n{assembler.get_hex_output()}")
    
    # Режим тестирования
    if args.test:
        assembler.print_test_output()
    
    # Сохранение в файл
    if args.output:
        num_bytes = assembler.save_to_binary_file(args.output)
        print(f"✓ Машинный код сохранён в '{args.output}' ({num_bytes} байт)")


if __name__ == '__main__':
    main()
