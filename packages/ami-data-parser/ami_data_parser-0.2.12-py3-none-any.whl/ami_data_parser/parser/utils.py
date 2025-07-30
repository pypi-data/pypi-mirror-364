
def set_output_format(line: str) -> str:
    words_except_list = [
        'Output:',
        'Response:',
        'Privilege:',
        'ActionID:',
        'Message:',
        'END COMMAND'
    ]

    for word in words_except_list:
        if word in line:
            return line
    
    return f'Output:    {line}'