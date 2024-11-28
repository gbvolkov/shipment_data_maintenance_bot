import re

#def escape_markdown_v2(text):
#    special_chars = r'_*[]()~`>#+=|{}.!-'
#    return ''.join(f'\\{char}' if char in special_chars else char for char in text)

def escape_markdown_v2_old(text):
    # Characters that need escaping
    special_chars = r'_[]()~`>#+=|{}.!-'  # Added '-' to the list

    def escape_char(c):
        return '\\' + c if c in special_chars else c

    def handle_font_formatting(text):
        # Handle bold (asterisks)
        text = re.sub(r'\*\*(.+?)\*\*', r'*\1*', text)  # Replace ** with *
        text = re.sub(r'(?<!\\)\*(.+?)(?<!\\)\*', r'*\1*', text)  # Keep single * as is

        # Handle italic (underscores)
        text = re.sub(r'(?<!\\)_(.+?)(?<!\\)_', r'*\1*', text)  # Replace _ with *

        return text

    # First, handle formatting (bold and italic)
    text = handle_font_formatting(text)

    # Then escape special characters, preserving existing escapes
    result = []
    i = 0
    while i < len(text):
        if text[i] == '\\' and i + 1 < len(text) and text[i+1] in f"{special_chars}*":
            result.append(text[i:i+2])  # Keep existing escapes
            i += 2
        elif text[i] == '*':
            result.append('*')  # Keep * for formatting
            i += 1
        elif text[i] in special_chars:
            result.append('\\' + text[i])  # Escape special chars
            i += 1
        else:
            result.append(text[i])  # Regular character
            i += 1

    return ''.join(result)

def escape_markdown_v2(text):
    # Define the special characters that need to be escaped
    special_chars = r'([_*\[\]()~`>#+\-=|{}.!])'

    # Patterns to identify Markdown constructs
    patterns = {
        'inline_code': r'(`[^`]+`)',  # Inline code
        'code_block': r'(```[\s\S]*?```)',  # Code block
        'bold': r'(\*\*[^*]+\*\*)',
        'italic': r'(_[^_]+_)',
        'underline': r'(__[^_]+__)',
        'strikethrough': r'(~[^~]+~)',
        'spoiler': r'(\|\|[^|]+\|\|)',
        'link': r'(\[([^\]]+)\]\(([^)]+)\))',  # Links
        'mention': r'(\[([^\]]+)\]\((tg://user\?id=\d+)\))',  # User mentions
        'custom_emoji': r'(!\[[^\]]*\]\(tg://emoji\?id=\d+\))',  # Custom emojis
        # Add more patterns as needed
    }

    # Combine all patterns into one regex
    combined_pattern = '|'.join(patterns.values())

    # Split the text into segments: those that match Markdown constructs and those that don't
    segments = re.split(f'({combined_pattern})', text)

    escaped_segments = []
    for segment in segments:
        if not segment:
            continue
        # Check if the segment matches any Markdown construct
        is_markdown = False
        for pattern in patterns.values():
            if re.fullmatch(pattern, segment):
                is_markdown = True
                break
        if is_markdown:
            # Do not escape Markdown constructs
            escaped_segments.append(segment)
        else:
            # Escape special characters in non-Markdown segments
            escaped = re.sub(special_chars, r'\\\1', segment)
            escaped_segments.append(escaped)

    return ''.join(escaped_segments)

def escape_markdown_v3(text):
    # Characters that need escaping in most contexts
    special_chars = r'_[]()~`>#+=|{}.!-'  # Added '-' to the list

    def escape_char(c):
        return '\\' + c if c in special_chars else c

    def handle_code_blocks(text):
        # Handle inline code
        text = re.sub(r'(?<!`)`(?!`)(.+?)(?<!`)`(?!`)', lambda m: '`' + m.group(1).replace('\\', '\\\\').replace('`', '\\`') + '`', text)
        
        # Handle multi-line code blocks
        text = re.sub(r'```(.+?)```', lambda m: '```' + m.group(1).replace('\\', '\\\\').replace('`', '\\`') + '```', text, flags=re.DOTALL)
        
        return text

    def handle_urls(text):
        # Handle inline URLs
        return re.sub(r'\[(.+?)\]\((.+?)\)', lambda m: f'[{m.group(1)}]({escape_url(m.group(2))})', text)

    def escape_url(url):
        # Escape parentheses, backslashes and minus signs in URLs
        return re.sub(r'([()\\-])', r'\\\1', url)

    def handle_formatting(text):
        # Handle bold (double asterisks)
        text = re.sub(r'\*\*(.+?)\*\*', lambda m: f'*{m.group(1)}*', text)
        
        # Handle italic (single asterisks or underscores)
        text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', lambda m: f'*{m.group(1)}*', text)
        text = re.sub(r'(?<!_)_(?!_)(.+?)(?<!_)_(?!_)', lambda m: f'_{m.group(1)}_', text)
        
        # Handle underline
        text = re.sub(r'__(.+?)__', lambda m: f'__{m.group(1)}__', text)
        
        # Handle strikethrough
        text = re.sub(r'~(.+?)~', lambda m: f'~{m.group(1)}~', text)
        
        # Handle spoiler
        text = re.sub(r'\|\|(.+?)\|\|', lambda m: f'||{m.group(1)}||', text)
        
        return text

    def handle_block_quotes(text):
        # Handle block quotes
        return re.sub(r'^>(.+)$', r'>\1', text, flags=re.MULTILINE)

    # First, handle code blocks (they have different escaping rules)
    text = handle_code_blocks(text)
    
    # Then handle URLs
    text = handle_urls(text)
    
    # Handle block quotes
    text = handle_block_quotes(text)
    
    # Handle formatting
    text = handle_formatting(text)

    # Escape remaining special characters, preserving existing escapes and formatting
    result = []
    i = 0
    while i < len(text):
        if text[i] == '\\' and i + 1 < len(text) and text[i+1] in special_chars:
            result.append(text[i:i+2])  # Keep existing escapes
            i += 2
        elif text[i] == '*':
            if i == 0 or text[i-1].isspace():
                # This is likely a bullet point or start of a line, keep it as is
                result.append('*')
            elif i + 1 < len(text) and text[i+1].isspace():
                # This is likely the end of a bullet point, keep it as is
                result.append('*')
            elif i > 0 and i + 1 < len(text) and text[i-1].isalnum() and text[i+1].isalnum():
                # This is likely used for emphasis within a word, escape it
                result.append('\\*')
            else:
                # This is likely formatting, keep it as is
                result.append('*')
            i += 1
        elif text[i] in special_chars:
            result.append('\\' + text[i])  # Escape special chars, including minus sign
            i += 1
        else:
            result.append(text[i])  # Regular character
            i += 1

    return ''.join(result)

def format_table_as_list(table_text):
    lines = table_text.strip().split('\n')
    if len(lines) < 3:
        return table_text  # Not enough lines for a table

    # Check if the second line contains only dashes and pipes
    if not re.match(r'^[\s\|\-]+$', lines[1]):
        return table_text  # Not a table

    headers = [cell.strip() for cell in lines[0].split('|') if cell.strip()]
    formatted_output = []

    for line in lines[2:]:  # Skip header and separator lines
        cells = [cell.strip() for cell in line.split('|') if cell.strip()]
        if len(cells) != len(headers):
            continue  # Skip malformed lines

        item_output = []
        for i, cell in enumerate(cells):
            if i == 0:
                item_output.append(f"{headers[i]}: {cell}")
            else:
                item_output.append(f"• {headers[i]}: {cell}")
        
        formatted_output.append('\n'.join(item_output))

    return '\n\n'.join(formatted_output)

def split_string(text, max_length=4096):
    chunks = []
    lines = text.split('\n')
    current_chunk = ""

    for line in lines:
        if len(current_chunk) + len(line) + 1 > max_length:
            chunks.append(current_chunk.strip())
            current_chunk = line
        else:
            if current_chunk:
                current_chunk += '\n'
            current_chunk += line

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

def process_text_with_tables(text):
    # Find all tables in the text
    table_pattern = r'\n(\|.+\|\n\|[-\s|]+\|\n(?:\|.+\|\n)+)'
    table_matches = list(re.finditer(table_pattern, text))
    
    if not table_matches:
        return text

    formatted_parts = []
    last_end = 0

    for match in table_matches:
        # Process text before the table
        before_table = text[last_end:match.start()]
        formatted_parts.append(before_table)

        # Process the table
        table = match.group(1)
        formatted_parts.append(format_table_as_list(table))

        last_end = match.end()

    # Process text after the last table
    after_last_table = text[last_end:]
    formatted_parts.append(after_last_table)
    return '\n\n'.join(part for part in formatted_parts if part.strip())

import traceback 

def format_for_telegram(model_output):
    try:
        # Process the entire text, including embedded tables

        try:
            formatted_model_output = process_text_with_tables(model_output)
        except Exception as e:
            print(f"Error during table formatting: {str(e)}")
            #traceback.print_exc() 
            return model_output# escape_markdown_v2(model_output)
        #return escape_markdown_v3(formatted_model_output)
        return formatted_model_output
    except Exception as e:
        print(f"Error during formatting: {str(e)}")
        traceback.print_exc() 
        # If there's an error, return the original text split into chunks, with all formatting removed
        #return split_string(re.sub(r'[*_`\-\.]', '', model_output))
        return model_output