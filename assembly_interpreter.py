from assembly_helpers import *
import colorama
from colorama import Fore, Back, Style
import time
import os
from collections import deque
from sys import argv

# Initialize colorama for cross-platform color support
colorama.init(autoreset=True)

def assembler_interpreter(program, DEBUG=False, STEP_MODE=False, DELAY=0.3):
    """Interprets lines of assembly program and returns a set return code"""

    # Tokenize the lines and filter out whitespace
    program = filter(None, map(process_line, program.split('\n')))

    # Convert to a tuple for indexing w/ the line counter
    program = tuple(program)

    # Error if no end statement in the program
    if all(line[0] != 'end' for line in program):
        print(f"{Fore.RED}Error: No 'end' statement found in program{Style.RESET_ALL}")
        return -1

    # Find all functions/routines for line jumping
    label_lines = {line[0].rstrip(':'): i for i, line in enumerate(program) if line[0][-1] == ':'}

    # Setting auxiliary variables for the language
    memory = dict()
    registers, line_counter = dict(), 0
    prev_lines, return_code = deque(), str()
    compare = [0, 0]  # Initialize compare to avoid UnboundLocalError
    
    # For execution history
    execution_history = []
    
    step_counter = 0
    
    while line_counter < len(program) and program[line_counter][0] != 'end':
        step_counter += 1
        current_line = program[line_counter]
        command = current_line[0]
        
        # Skip label lines - this is the key fix
        if command.endswith(':'):
            line_counter += 1
            continue
            
        other = current_line[1:] if len(current_line) > 1 else []
        
        if STEP_MODE or DEBUG:
            clear_screen()
            print(f"{Fore.CYAN}=== Assembly Interpreter - Step {step_counter} ==={Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Program Counter: {line_counter}{Style.RESET_ALL}")
            
            # Show execution context (5 lines before and after current line)
            print(f"\n{Fore.CYAN}Program Context:{Style.RESET_ALL}")
            for i in range(max(0, line_counter - 5), min(len(program), line_counter + 6)):
                if i == line_counter:
                    print(f"{Fore.GREEN}→ {i:04d}: {' '.join(str(x) for x in program[i])}{Style.RESET_ALL}")
                else:
                    print(f"  {i:04d}: {' '.join(str(x) for x in program[i])}")
            
            # Show registers
            print(f"\n{Fore.CYAN}Registers:{Style.RESET_ALL}")
            if not registers:
                print("  No registers used yet")
            else:
                for reg_name, reg_value in sorted(registers.items()):
                    print(f"  {reg_name}: {reg_value}")
            
            # Show memory
            print(f"\n{Fore.CYAN}Memory (showing up to 10 items):{Style.RESET_ALL}")
            if not memory:
                print("  No memory used yet")
            else:
                for i, (addr, value) in enumerate(sorted(memory.items())):
                    print(f"  {addr}: {value}")
                    if i >= 9:  # Show only 10 memory locations max
                        remaining = len(memory) - 10
                        if remaining > 0:
                            print(f"  ... and {remaining} more locations")
                        break
            
            # Show call stack
            print(f"\n{Fore.CYAN}Call Stack:{Style.RESET_ALL}")
            if not prev_lines:
                print("  Empty stack")
            else:
                for i, addr in enumerate(prev_lines):
                    print(f"  {i}: line {addr}")
            
            # Show compare values
            print(f"\n{Fore.CYAN}Compare Values: {compare}{Style.RESET_ALL}")
            
            # Show current command to be executed
            print(f"\n{Fore.GREEN}Executing: {' '.join(str(x) for x in current_line)}{Style.RESET_ALL}")
            
            # Show last 5 operations
            if execution_history:
                print(f"\n{Fore.CYAN}Last Operations:{Style.RESET_ALL}")
                for hist in execution_history[-5:]:
                    print(f"  {hist}")
            
            if STEP_MODE:
                input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            else:
                time.sleep(DELAY)

        # Record command in history
        execution_history.append(f"Step {step_counter:04d}: " + ' '.join(str(x) for x in current_line))

        # mov command moves either a constant or register value to a register
        if command == 'mov':
            register, value = other
            registers[register] = get_value(value, registers)

        # inc increments the value of a register by 1
        elif command == 'inc':
            register = other[0]
            registers[register] += 1

        # dec decrements the value of a register by 1
        elif command == 'dec':
            register = other[0]
            registers[register] -= 1

        # add adds the contents of a register and a register or constant
        elif command == 'add':
            register, value = other
            registers[register] += get_value(value, registers)

        # sub subtracts the contents of a register and a register or constant
        elif command == 'sub':
            register, value = other
            registers[register] -= get_value(value, registers)

        # mul multiplies the contents of a register and a register or constant
        elif command == 'mul':
            register, value = other
            registers[register] *= get_value(value, registers)

        # div integer divides the contents of a register and a register or constant
        elif command == 'div':
            register, value = other
            divisor = get_value(value, registers)
            if divisor == 0:
                print(f"{Fore.RED}Error: Division by zero at line {line_counter}{Style.RESET_ALL}")
                return -1
            registers[register] //= divisor

        # jmp jumps the line counter to the function/routine provided without storing the old location
        elif command == 'jmp':
            label = other[0]
            if label not in label_lines:
                print(f"{Fore.RED}Error: Unknown label '{label}' at line {line_counter}{Style.RESET_ALL}")
                return -1
            line_counter = label_lines[label]
            continue  # Skip incrementing line_counter

        # call jumps the line counter to the function/routine provided while storing the previous one
        elif command == 'call':
            label = other[0]
            if label not in label_lines:
                print(f"{Fore.RED}Error: Unknown label '{label}' at line {line_counter}{Style.RESET_ALL}")
                return -1
            prev_lines.append(line_counter)
            line_counter = label_lines[label]
            continue  # Skip incrementing line_counter

        # ret returns the line counter to the previous line before a routine was called
        elif command == 'ret':
            if not prev_lines:
                print(f"{Fore.RED}Error: 'ret' with empty call stack at line {line_counter}{Style.RESET_ALL}")
                return -1
            line_counter = prev_lines.pop()

        # cmp stores both values for the next jump comparison
        elif command == 'cmp':
            one, two = other
            compare = [get_value(one, registers),
                      get_value(two, registers)]

        # je jumps to function/routine if the comparison is ==
        elif command == 'je':
            label = other[0]
            if label not in label_lines:
                print(f"{Fore.RED}Error: Unknown label '{label}' at line {line_counter}{Style.RESET_ALL}")
                return -1
            if compare[0] == compare[1]:
                line_counter = label_lines[label]
                continue  # Skip incrementing line_counter

        # ce call to function/routine if the comparison is ==
        elif command == 'ce':
            label = other[0]
            if label not in label_lines:
                print(f"{Fore.RED}Error: Unknown label '{label}' at line {line_counter}{Style.RESET_ALL}")
                return -1
            if compare[0] == compare[1]:
                prev_lines.append(line_counter)
                line_counter = label_lines[label]
                continue  # Skip incrementing line_counter

        # jne jumps to function/routine if the comparison is !=
        elif command == 'jne':
            label = other[0]
            if label not in label_lines:
                print(f"{Fore.RED}Error: Unknown label '{label}' at line {line_counter}{Style.RESET_ALL}")
                return -1
            if compare[0] != compare[1]:
                line_counter = label_lines[label]
                continue  # Skip incrementing line_counter

        # cne call to function/routine if the comparison is !=
        elif command == 'cne':
            label = other[0]
            if label not in label_lines:
                print(f"{Fore.RED}Error: Unknown label '{label}' at line {line_counter}{Style.RESET_ALL}")
                return -1
            if compare[0] != compare[1]:
                prev_lines.append(line_counter)
                line_counter = label_lines[label]
                continue  # Skip incrementing line_counter

        # jge jumps to function/routine if the the comparison is >=
        elif command == 'jge':
            label = other[0]
            if label not in label_lines:
                print(f"{Fore.RED}Error: Unknown label '{label}' at line {line_counter}{Style.RESET_ALL}")
                return -1
            if compare[0] >= compare[1]:
                line_counter = label_lines[label]
                continue  # Skip incrementing line_counter

        # cne call to function/routine if the comparison is >=
        elif command == 'cge':
            label = other[0]
            if label not in label_lines:
                print(f"{Fore.RED}Error: Unknown label '{label}' at line {line_counter}{Style.RESET_ALL}")
                return -1
            if compare[0] >= compare[1]:
                prev_lines.append(line_counter)
                line_counter = label_lines[label]
                continue  # Skip incrementing line_counter

        # jg jumps to function/routine if the the comparison is >
        elif command == 'jg':
            label = other[0]
            if label not in label_lines:
                print(f"{Fore.RED}Error: Unknown label '{label}' at line {line_counter}{Style.RESET_ALL}")
                return -1
            if compare[0] > compare[1]:
                line_counter = label_lines[label]
                continue  # Skip incrementing line_counter

        # cne call to function/routine if the comparison is >
        elif command == 'cg':
            label = other[0]
            if label not in label_lines:
                print(f"{Fore.RED}Error: Unknown label '{label}' at line {line_counter}{Style.RESET_ALL}")
                return -1
            if compare[0] > compare[1]:
                prev_lines.append(line_counter)
                line_counter = label_lines[label]
                continue  # Skip incrementing line_counter

        # jle jumps to function/routine if the comparison is <=
        elif command == 'jle':
            label = other[0]
            if label not in label_lines:
                print(f"{Fore.RED}Error: Unknown label '{label}' at line {line_counter}{Style.RESET_ALL}")
                return -1
            if compare[0] <= compare[1]:
                line_counter = label_lines[label]
                continue  # Skip incrementing line_counter

        # cne call to function/routine if the comparison is <=
        elif command == 'cle':
            label = other[0]
            if label not in label_lines:
                print(f"{Fore.RED}Error: Unknown label '{label}' at line {line_counter}{Style.RESET_ALL}")
                return -1
            if compare[0] <= compare[1]:
                prev_lines.append(line_counter)
                line_counter = label_lines[label]
                continue  # Skip incrementing line_counter

        # jl jumps to function/routine if the comparison is <
        elif command == 'jl':
            label = other[0]
            if label not in label_lines:
                print(f"{Fore.RED}Error: Unknown label '{label}' at line {line_counter}{Style.RESET_ALL}")
                return -1
            if compare[0] < compare[1]:
                line_counter = label_lines[label]
                continue  # Skip incrementing line_counter

        # cne call to function/routine if the comparison is <
        elif command == 'cl':
            label = other[0]
            if label not in label_lines:
                print(f"{Fore.RED}Error: Unknown label '{label}' at line {line_counter}{Style.RESET_ALL}")
                return -1
            if compare[0] < compare[1]:
                prev_lines.append(line_counter)
                line_counter = label_lines[label]
                continue  # Skip incrementing line_counter

        # stw stores a value at a memory address
        elif command == 'stw':
            value, address = other
            address = get_address(address, registers)
            memory[address] = get_value(value, registers)

        # mvw takes a value from a memory address and stores it in a register
        elif command == 'mvw':
            register, address = other
            address = get_address(address, registers)
            registers[register] = memory.get(address, 0)  # Default to 0 if address not in memory

        # msg stores the return output of the program
        elif command == 'msg':
            parts = []
            i = 0
            while i < len(other):
                part = other[i]
                if part.startswith("'") and not part.endswith("'"):
                    # Handle multi-part strings
                    full_str = [part[1:]]  # Remove opening quote
                    i += 1
                    while i < len(other) and not other[i].endswith("'"):
                        full_str.append(other[i])
                        i += 1
                    if i < len(other):
                        full_str.append(other[i][:-1])  # Remove closing quote
                    parts.append(' '.join(full_str))
                elif part.startswith("'") and part.endswith("'"):
                    # Handle complete quoted strings
                    parts.append(part[1:-1])
                elif part == '\\n':
                    # Handle newlines
                    parts.append('\n')
                elif part in registers:
                    # Handle register values
                    parts.append(str(registers[part]))
                else:
                    # Handle other text
                    parts.append(part)
                i += 1
            
            message = ''.join(parts)
            return_code += message
            
            if not message.endswith('\n'):
                return_code += '\n'  # Ensure each msg ends with a newline

            # Display message immediately in step mode
            if STEP_MODE or DEBUG:
                print(f"\n{Fore.MAGENTA}Output: {message}{Style.RESET_ALL}")
        
        else:
            print(f"{Fore.RED}Error: Unknown command '{command}' at line {line_counter}{Style.RESET_ALL}")
            return -1

        line_counter += 1

        # Catches programs that terminate incorrectly
        if line_counter >= len(program):
            print(f"{Fore.RED}Error: Program reached end without 'end' statement{Style.RESET_ALL}")
            return -1

    # Final program state
    if STEP_MODE or DEBUG:
        clear_screen()
        print(f"{Fore.GREEN}=== Program Execution Complete ==={Style.RESET_ALL}")
        print(f"\n{Fore.CYAN}Final Register Values:{Style.RESET_ALL}")
        for reg_name, reg_value in sorted(registers.items()):
            print(f"  {reg_name}: {reg_value}")
        
        print(f"\n{Fore.CYAN}Final Output:{Style.RESET_ALL}")
        print(f"{return_code}")
        
        print(f"\n{Fore.YELLOW}Program executed in {step_counter} steps{Style.RESET_ALL}")
        
        if STEP_MODE:
            input(f"{Fore.YELLOW}Press Enter to exit...{Style.RESET_ALL}")

    return return_code


def clear_screen():
    """Clears the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')


def display_help():
    """Displays help information for the program"""
    print(f"{Fore.CYAN}=== Assembly Interpreter Help ==={Style.RESET_ALL}")
    print(f"\n{Fore.YELLOW}Usage:{Style.RESET_ALL}")
    print("  assembly_interpreter.py [file] [options]")
    
    print(f"\n{Fore.YELLOW}Options:{Style.RESET_ALL}")
    print("  -h, --help     Show this help message")
    print("  -d, --debug    Run in debug mode (shows program state)")
    print("  -s, --step     Run in step mode (pause after each instruction)")
    print("  --delay=N      Set delay between instructions in debug mode (seconds)")
    
    print(f"\n{Fore.YELLOW}Commands:{Style.RESET_ALL}")
    print("  mov reg, val    Move value to register")
    print("  inc reg         Increment register")
    print("  dec reg         Decrement register")
    print("  add reg, val    Add value to register")
    print("  sub reg, val    Subtract value from register")
    print("  mul reg, val    Multiply register by value")
    print("  div reg, val    Divide register by value")
    print("  cmp v1, v2      Compare values")
    print("  jmp label       Jump to label")
    print("  je label        Jump if equal")
    print("  jne label       Jump if not equal")
    print("  jg label        Jump if greater")
    print("  jl label        Jump if less")
    print("  jge label       Jump if greater or equal")
    print("  jle label       Jump if less or equal")
    print("  call label      Call subroutine")
    print("  ret             Return from subroutine")
    print("  stw val, addr   Store value at memory address")
    print("  mvw reg, addr   Move value from memory to register")
    print("  msg ...         Output message")
    print("  end             End program")
    
    print(f"\n{Fore.YELLOW}Examples:{Style.RESET_ALL}")
    print("  assembly_interpreter.py test.asm")
    print("  assembly_interpreter.py test.asm -s")
    print("  assembly_interpreter.py test.asm -d --delay=0.5")


if __name__ == '__main__':
    # Initialize colorama for cross-platform color support
    colorama.init(autoreset=True)
    
    # Parse command line arguments
    if len(argv) < 2 or argv[1] in ['-h', '--help']:
        display_help()
        exit(0)
    
    assembly_file = argv[1]
    
    # Process options
    DEBUG = False
    STEP_MODE = False
    DELAY = 0.3
    
    for arg in argv[2:]:
        if arg in ['-d', '--debug']:
            DEBUG = True
        elif arg in ['-s', '--step']:
            STEP_MODE = True
        elif arg.startswith('--delay='):
            try:
                DELAY = float(arg.split('=')[1])
            except ValueError:
                print(f"{Fore.RED}Error: Invalid delay value{Style.RESET_ALL}")
                exit(1)
    
    try:
        with open(assembly_file) as program:
            print(f"{Fore.GREEN}Loading program: {assembly_file}{Style.RESET_ALL}")
            output = assembler_interpreter(program.read(), DEBUG=DEBUG, STEP_MODE=STEP_MODE, DELAY=DELAY)
            
            if output == -1:
                print(f"{Fore.RED}Program execution failed{Style.RESET_ALL}")
                exit(1)
            
            if not (DEBUG or STEP_MODE):
                print(f"{Fore.GREEN}Program Output:{Style.RESET_ALL}")
                print(output)
            
    except FileNotFoundError:
        print(f"{Fore.RED}Error: File '{assembly_file}' not found.{Style.RESET_ALL}")
        exit(1)  # Exit with error code