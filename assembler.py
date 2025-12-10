#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ассемблер для учебной виртуальной машины (УВМ)
Этап 1: Перевод программы в промежуточное представление

Требования:
1. Ассемблер принимает входные аргументы из командной строки
2. Путь к исходному файлу с текстом программы
3. Путь к выходному файлу-результату (опционально)
4. Режимы тестирования (-t флаг)
5. Проверка правильности синтаксиса ассемблера
6. Описание в документации синтаксиса языка ассемблера
7. Реализация транслятора для преобразования внутреннего представления
8. Вывод внутреннего представления в формате полей и значений
9. Демонстрация уникальных последовательностей полей и значений

Использование:
    python assembler.py <input_file> [-o <output_file>] [-v] [-t]

Примеры:
    python assembler.py program.asm
    python assembler.py program.asm -o output.bin -v
    python assembler.py program.asm -t
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Optional


class Assembler:
    """
    Ассемблер для учебной виртуальной машины (УВМ)
    
    Поддерживаемые команды:
    - LOAD reg, operand  - загрузить значение в регистр
    - STORE reg, addr    - сохранить регистр в памяти
    - ADD reg1, reg2     - сложить два регистра
    - SUB reg1, reg2     - вычесть второй регистр из первого
    - MUL reg1, reg2     - умножить два регистра
    - DIV reg1, reg2     - разделить первый на второй
    - MOD reg1, reg2     - остаток от деления
    - JMP label          - безусловный прыжок на метку
    - JZ label           - прыжок если ноль
    - JNZ label          - прыжок если не ноль
    - CMP reg1, reg2     - сравнение двух регистров
    - CALL label         - вызов подпрограммы
    - RET                - возврат из подпрограммы
    - PUSH reg           - поместить значение в стек
    - POP reg            - извлечь значение из стека
    - HALT               - остановка программы
    
    Регистры: A, B, C, D
    Метки: идентификаторы заканчивающиеся на ':'
    """
    
    def __init__(self):
        # Определение команд и их кодов операций (opcode)
        self.commands = {
            'LOAD': 0x01,
            'STORE': 0x02,
            'ADD': 0x03,
            'SUB': 0x04,
            'MUL': 0x05,
            'DIV': 0x06,
            'MOD': 0x07,
            'JMP': 0x08,
            'JZ': 0x09,
            'JNZ': 0x0A,
            'CMP': 0x0B,
            'CALL': 0x0C,
            'RET': 0x0D,
            'PUSH': 0x0E,
            'POP': 0x0F,
            'HALT': 0x10,
        }
        
        # Определение регистров и их номеров
        self.registers = {
            'A': 0,
            'B': 1,
            'C': 2,
            'D': 3,
        }
        
        self.instructions: List[int] = []
        self.labels: Dict[str, int] = {}
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def is_valid_number(self, s: str) -> bool:
        """Проверка, является ли строка числом (поддерживает hex и decimal)"""
        try:
            int(s, 0)
            return True
        except ValueError:
            return False
    
    def is_valid_identifier(self, s: str) -> bool:
        """Проверка, является ли строка корректным идентификатором"""
        return s.isidentifier() and not s.upper() in self.commands
    
    def parse_operand(self, operand: str) -> Optional[int]:
        """Парсинг операнда: регистр, число или метка"""
        operand = operand.strip().rstrip(',')
        
        if operand in self.registers:
            return self.registers[operand]
        elif self.is_valid_number(operand):
            return int(operand, 0)
        else:
            return None
    
    def first_pass(self, lines: List[str]) -> bool:
        """
        Первый проход анализа:
        - Поиск и регистрация меток
        - Проверка синтаксиса
        - Подсчёт размера программы
        """
        for line_num, line in enumerate(lines, 1):
            # Удаляем комментарии
            if ';' in line:
                line = line.split(';')[0]
            
            line = line.strip()
            if not line:
                continue
            
            # Обработка метки
            if line.endswith(':'):
                label = line[:-1].strip()
                if not self.is_valid_identifier(label):
                    self.errors.append(
                        f"Строка {line_num}: Неверное имя метки '{label}'"
                    )
                    return False
                if label in self.labels:
                    self.errors.append(
                        f"Строка {line_num}: Метка '{label}' уже определена"
                    )
                    return False
                self.labels[label] = len(self.instructions)
                continue
            
            # Проверка команды
            parts = line.split()
            if not parts:
                continue
            
            cmd = parts[0].upper()
            if cmd not in self.commands:
                self.errors.append(f"Строка {line_num}: Неизвестная команда '{cmd}'")
                return False
            
            # Подсчёт размера (простая оценка)
            # Формат: OPCODE [операнд1] [операнд2]
            self.instructions.append(0)  # Placeholder для размера
        
        return True
    
    def second_pass(self, lines: List[str]) -> bool:
        """
        Второй проход:
        - Генерация машинного кода
        - Разрешение адресов меток
        - Финальная проверка ошибок
        """
        self.instructions = []
        
        for line_num, line in enumerate(lines, 1):
            # Удаляем комментарии
            if ';' in line:
                line = line.split(';')[0]
            
            line = line.strip()
            if not line or line.endswith(':'):
                continue
            
            # Разбор команды
            parts = line.split()
            cmd = parts[0].upper()
            
            if cmd not in self.commands:
                continue
            
            # Добавляем opcode
            self.instructions.append(self.commands[cmd])
            
            # Обработка операндов
            operands = parts[1:] if len(parts) > 1 else []
            
            for operand in operands:
                operand_clean = operand.rstrip(',').strip()
                
                if operand_clean in self.labels:
                    # Адрес метки
                    addr = self.labels[operand_clean]
                    self.instructions.append(addr)
                elif operand_clean in self.registers:
                    # Номер регистра
                    self.instructions.append(self.registers[operand_clean])
                elif self.is_valid_number(operand_clean):
                    # Числовое значение
                    val = int(operand_clean, 0)
                    if val > 255:
                        self.warnings.append(
                            f"Строка {line_num}: Значение {val} больше 255, "
                            f"будет использовано {val & 0xFF}"
                        )
                    self.instructions.append(val & 0xFF)
                else:
                    self.errors.append(
                        f"Строка {line_num}: Неверный операнд '{operand_clean}'"
                    )
                    return False
        
        return True
    
    def assemble(self, source_code: str) -> bool:
        """Главный метод ассемблирования"""
        lines = source_code.split('\n')
        
        # Первый проход
        self.instructions = []
        if not self.first_pass(lines):
            return False
        
        # Второй проход
        self.instructions = []
        if not self.second_pass(lines):
            return False
        
        return True
    
    def get_hex_output(self) -> str:
        """Вывод машинного кода в шестнадцатеричном формате"""
        if not self.instructions:
            return "0x"
        hex_bytes = ' '.join(f'{byte:02x}' for byte in self.instructions)
        return f"0x{hex_bytes.replace(' ', '')}"
    
    def get_hex_pretty(self) -> str:
        """Красивый вывод машинного кода (по 16 байт в строке)"""
        result = []
        for i in range(0, len(self.instructions), 16):
            chunk = self.instructions[i:i+16]
            hex_str = ' '.join(f'{byte:02x}' for byte in chunk)
            result.append(hex_str)
        return '\n'.join(result)
    
    def get_detailed_output(self) -> str:
        """Подробный вывод с метаинформацией"""
        output = ["=" * 60]
        output.append("АССЕМБЛИРОВАННАЯ ПРОГРАММА")
        output.append("=" * 60)
        output.append(f"Размер программы: {len(self.instructions)} байт")
        output.append(f"Количество команд: ~{len(self.instructions) // 3}")
        output.append("")
        output.append("Машинный код (hex):")
        output.append(self.get_hex_pretty())
        output.append("")
        output.append("Машинный код (dec):")
        dec_str = ' '.join(str(b) for b in self.instructions)
        for i in range(0, len(dec_str), 60):
            output.append(dec_str[i:i+60])
        
        if self.labels:
            output.append("\nТаблица меток:")
            output.append("-" * 30)
            for label in sorted(self.labels.keys()):
                output.append(f"  {label:16s} : {self.labels[label]:3d}")
        
        if self.warnings:
            output.append("\nПредупреждения:")
            for warning in self.warnings:
                output.append(f"  ⚠  {warning}")
        
        output.append("=" * 60)
        return '\n'.join(output)
    
    def get_errors_output(self) -> str:
        """Форматированный вывод ошибок"""
        if not self.errors:
            return "Ошибок не обнаружено"
        return '\n'.join(f"❌ {error}" for error in self.errors)


class AssemblerCLI:
    """Интерфейс командной строки для ассемблера"""
    
    @staticmethod
    def create_parser() -> argparse.ArgumentParser:
        """Создание парсера аргументов командной строки"""
        parser = argparse.ArgumentParser(
            description='Ассемблер для учебной виртуальной машины (УВМ)',
            prog='assembler.py',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Примеры использования:
  python assembler.py program.asm
  python assembler.py program.asm -o output.bin
  python assembler.py program.asm -v -o output.bin
            """
        )
        
        parser.add_argument('input_file',
                          help='Путь к исходному файлу ассемблера')
        parser.add_argument('-o', '--output',
                          dest='output_file',
                          help='Файл для записи результата')
        parser.add_argument('-v', '--verbose',
                          action='store_true',
                          help='Подробный вывод с метаинформацией')
        parser.add_argument('-t', '--test',
                          action='store_true',
                          help='Режим тестирования')
        
        return parser
    
    @staticmethod
    def main(argv=None):
        """Главная функция CLI"""
        parser = AssemblerCLI.create_parser()
        args = parser.parse_args(argv)
        
        # Проверка входного файла
        input_path = Path(args.input_file)
        if not input_path.exists():
            print(f"❌ Ошибка: файл '{args.input_file}' не найден", file=sys.stderr)
            return 1
        
        # Чтение исходного кода
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
        except Exception as e:
            print(f"❌ Ошибка при чтении файла: {e}", file=sys.stderr)
            return 1
        
        # Ассемблирование
        assembler = Assembler()
        if not assembler.assemble(source_code):
            print("❌ ОШИБКИ АССЕМБЛИРОВАНИЯ:", file=sys.stderr)
            print(assembler.get_errors_output(), file=sys.stderr)
            return 1
        
        # Вывод результата
        if args.verbose:
            print(assembler.get_detailed_output())
        else:
            print(assembler.get_hex_output())
        
        # Запись в выходной файл
        if args.output_file:
            try:
                with open(args.output_file, 'w', encoding='utf-8') as f:
                    if args.verbose:
                        f.write(assembler.get_detailed_output())
                    else:
                        f.write(assembler.get_hex_output())
                if args.verbose:
                    print(f"\n✓ Результат записан в '{args.output_file}'")
            except Exception as e:
                print(f"❌ Ошибка при записи файла: {e}", file=sys.stderr)
                return 1
        
        if args.verbose:
            print("✓ Ассемблирование завершено успешно")
        
        return 0


if __name__ == '__main__':
    sys.exit(AssemblerCLI.main())
