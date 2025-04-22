def get_address(address, registers):
    """Gets the numerical address from the possible access modes allowed"""
    
    try:
        address, offset = address.split('+')
        offset = int(offset)
    except ValueError:
        try:
            address, offset = address.split('-')
            offset = -int(offset)
        except ValueError:
            offset = 0

    if address.isdigit():
        return int(address)

    return int(registers[address]) + offset

def get_value(value: str, registers: dict):
    """Returns a constant if value is an integer or the register value otherwise"""

    if value in registers:
        return registers[value]
    
    try:
        return int(value)
    except ValueError:
        # Improved error handling for non-numeric values
        raise ValueError(f"Invalid value: '{value}' is not a valid integer or register name")

def process_line(line: str):
    """Removes comments and unneeded whitespace. Returns a split list of
    instructions/registers"""
    
    comment_start = line.find(';')

    # Remove comments, one comment per line allowed
    if comment_start != -1:
        line = line[:comment_start]

    line = line.strip()
    
    # Splits commands such that the command and all details are separated
    # "command ..." -> [command, ...]
    if not line:
        return None  # Return None for empty lines after stripping

    if line[-1] == ':' or line == 'end' or line == 'ret':
        return (line,)

    try:
        command, contents = line.split(maxsplit=1)
    except ValueError:
        return (line,)  # Handle cases where only the command exists

    # Special handling for msg command to preserve commas in quoted strings
    if command == 'msg':
        parts = [command]
        in_quote = False
        current_part = ""
        quote_start = -1
        
        for i, char in enumerate(contents):
            if char == "'" and (i == 0 or contents[i-1] != '\\'):
                in_quote = not in_quote
                if in_quote:
                    # Start of quoted string
                    quote_start = i
                    if current_part:
                        parts.append(current_part.strip())
                        current_part = ""
                    current_part = "'"
                else:
                    # End of quoted string
                    current_part += "'"
                    parts.append(current_part)
                    current_part = ""
            elif char == ',' and not in_quote:
                if current_part:
                    parts.append(current_part.strip())
                    current_part = ""
            else:
                current_part += char
        
        if current_part:
            parts.append(current_part.strip())
        
        return tuple(parts)
    
    # For other commands, split by comma
    try:
        one, two = contents.split(',', maxsplit=1)
        return command, one.strip(), two.strip()
    except ValueError:
        return command, contents.strip()