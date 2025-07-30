from nicegui import ui
import re
import json

def format_tool_name(tool_name: str) -> str:
    """Convert technical tool names to user-friendly display names."""
    # Remove common prefixes
    if tool_name.startswith('mcp-'):
        tool_name = tool_name[4:]
    if tool_name.startswith('code-editor:'):
        tool_name = tool_name[12:]
    
    # Convert underscores, hyphens, and colons to spaces
    formatted = tool_name.replace('_', ' ').replace('-', ' ').replace(':', ' ')
    
    # Split into words and capitalize each
    words = formatted.split()
    formatted_words = []
    
    for word in words:
        # Handle special cases
        if word.lower() == 'tool':
            continue  # Skip 'tool' suffix
        elif word.lower() == 'diff':
            formatted_words.append('Diff')
        elif word.lower() == 'api':
            formatted_words.append('API')
        elif word.lower() == 'http':
            formatted_words.append('HTTP')
        elif word.lower() == 'get':
            formatted_words.append('GET')
        elif word.lower() == 'post':
            formatted_words.append('POST')
        elif word.lower() == 'put':
            formatted_words.append('PUT')
        elif word.lower() == 'delete':
            formatted_words.append('DELETE')
        elif word.lower() == 'mcp':
            continue  # Skip 'mcp' prefix that might remain
        else:
            formatted_words.append(word.capitalize())
    
    return ' '.join(formatted_words) if formatted_words else 'Herramienta'

def is_structured_response(content: str) -> bool:
    """Check if content contains structured response metadata."""
    return "<!-- RESPONSE_METADATA:" in content

def is_interactive_response(content: str) -> bool:
    """Check if content contains interactive HTML metadata."""
    return "<!-- INTERACTIVE_METADATA:" in content

def extract_response_metadata(content: str):
    """Extract metadata from structured response."""
    if not is_structured_response(content):
        return None
    
    pattern = r'<!-- RESPONSE_METADATA: ({.*?}) -->'
    match = re.search(pattern, content)
    
    if match:
        try:
            metadata_str = match.group(1)
            # Replace single quotes with double quotes for valid JSON
            metadata_str = metadata_str.replace("'", '"')
            # Replace Python boolean values with JSON boolean values
            metadata_str = metadata_str.replace('True', 'true').replace('False', 'false')
            return json.loads(metadata_str)
        except json.JSONDecodeError:
            return None
    return None

def extract_interactive_metadata(content: str):
    """Extract metadata from interactive HTML response."""
    if not is_interactive_response(content):
        return None
    
    pattern = r'<!-- INTERACTIVE_METADATA: (.+?) -->'
    match = re.search(pattern, content)
    
    if match:
        try:
            metadata_str = match.group(1)
            return json.loads(metadata_str)
        except json.JSONDecodeError:
            return None
    return None

def clean_interactive_content(content: str) -> str:
    """Remove interactive metadata comments from content."""
    pattern = r'<!-- INTERACTIVE_METADATA: .*? -->'
    cleaned = re.sub(pattern, '', content)
    return cleaned.strip()

    
    return None

def clean_response_content(content: str) -> str:
    """Remove metadata comments from response content."""
    pattern = r'\n\n<!-- RESPONSE_METADATA: .*? -->'
    cleaned = re.sub(pattern, '', content)
    return cleaned.strip()

def apply_structured_response_style(container, metadata: dict):
    """Apply enhanced styling to container based on metadata with uniform design."""
    if not metadata:
        return
    
    background_color = metadata.get('background_color')
    border_color = metadata.get('border_color')
    text_color = metadata.get('text_color')
    
    # Base styling - always applied for uniformity
    base_style = (
        'padding: 16px; '
        'border-radius: 12px; '
        'margin: 8px 0; '
        'box-shadow: 0 2px 8px rgba(0,0,0,0.1); '
        'transition: all 0.2s ease; '
    )
    
    # Add colors if available
    color_style = ''
    if background_color:
        color_style += f'background-color: {background_color}; '
    if border_color:
        color_style += f'border-left: 5px solid {border_color}; '
    if text_color:
        color_style += f'color: {text_color}; '
    
    # Combine all styles
    full_style = base_style + color_style
    container.style(full_style)


def parse_and_render_message(message: str, container) -> None:
    """
    Parse a message and render it with proper code block formatting.
    
    Detects code blocks marked with triple backticks (```) and renders them
    using ui.code component, while rendering regular text as ui.markdown.
    
    Args:
        message: The message content to parse
        container: The UI container to add elements to
    """
    if not message or not message.strip():
        return
    
    # Check if this is an interactive HTML response
    interactive_metadata = extract_interactive_metadata(message)
    if interactive_metadata:
        # Clean the message content by removing metadata comments
        message = clean_interactive_content(message)
        
        # Render the interactive HTML
        render_interactive_html(container, interactive_metadata, message)
        return
    
    # Check if this is a structured response with metadata
    metadata = extract_response_metadata(message)
    if metadata:
        # Clean the message content by removing metadata comments
        message = clean_response_content(message)
        
        # Apply structured response styling to the container
        apply_structured_response_style(container, metadata)
        
        # Add enhanced icon if present
        icon = metadata.get('icon')
        icon_bg = metadata.get('icon_bg')
        if icon:
            with container:
                # Create icon container with background
                with ui.row().classes('items-center mb-3'):
                    icon_style = (
                        'display: inline-flex; '
                        'align-items: center; '
                        'justify-content: center; '
                        'width: 32px; '
                        'height: 32px; '
                        'border-radius: 50%; '
                        'font-size: 16px; '
                        'margin-right: 8px; '
                    )
                    if icon_bg:
                        icon_style += f'background-color: {icon_bg}; '
                    
                    ui.label(icon).style(icon_style)
    
    # Pattern to match code blocks with optional language specification
    # Matches: ```language\ncode\n``` or ```\ncode\n```
    code_block_pattern = r'```(\w+)?\s*\n?(.*?)\n?\s*```'
    
    # Find all code blocks and their positions
    matches = list(re.finditer(code_block_pattern, message, re.DOTALL))
    
    if not matches:
        # No code blocks found, render as regular markdown
        with container:
            ui.markdown(message)
        return
    
    # Process message with code blocks
    last_end = 0
    
    with container:
        for match in matches:
            start, end = match.span()
            language = match.group(1) or 'python'  # Default to python if no language specified
            code_content = match.group(2).strip()
            
            # Render text before code block (if any)
            if start > last_end:
                text_before = message[last_end:start].strip()
                if text_before:
                    ui.markdown(text_before)
            # Render code block
            if code_content:
                ui.code(code_content, language=language).classes('w-full my-2 overflow-x-auto')
            
            
            last_end = end
        
        # Render remaining text after last code block (if any)
        if last_end < len(message):
            text_after = message[last_end:].strip()
            if text_after:
                ui.markdown(text_after)

def render_tool_call_with_metadata(tool_call, tool_result=None, container=None):
    """
    Render a tool call with metadata in an enhanced UI format.
    
    Args:
        tool_call: Tool call object with function name and arguments
        tool_result: Optional tool result object
        container: UI container to render in (optional)
    """
    def render_content():
        # Extract tool information
        function_info = tool_call.get('function', {})
        tool_name = function_info.get('name', 'Unknown Tool')
        arguments_str = function_info.get('arguments', '{}')
        
        try:
            arguments = json.loads(arguments_str)
        except json.JSONDecodeError:
            arguments = {}
        
        # Extract metadata from arguments or tool result
        intention = arguments.get('intention', tool_call.get('_intention', 'No especificado'))
        success_criteria = arguments.get('success_criteria', tool_call.get('_success_criteria', 'No especificado'))
        
        # If tool_result has metadata, use that instead
        if tool_result and '_tool_metadata' in tool_result:
            metadata = tool_result['_tool_metadata']
            intention = metadata.get('intention', intention)
            success_criteria = metadata.get('success_criteria', success_criteria)
            tool_name = metadata.get('tool_name', tool_name)
        
        # Tool call container (integrated, no card)
        with ui.column().classes('border-l-4 border-blue-300 bg-blue-50/30 pl-4 pr-2 py-3 mb-2 w-full rounded-r'):
            # Header with tool name (more integrated)
            with ui.row().classes('w-full items-center mb-2'):
                ui.icon('build').classes('text-blue-600 mr-2 text-sm')
                ui.label(format_tool_name(tool_name)).classes('font-semibold text-blue-700 text-sm')
            
            # Content area (more compact)
            with ui.column().classes('space-y-2'):
                # Intention section (more integrated)
                with ui.row().classes('w-full'):
                    ui.label('Intención:').classes('font-medium text-blue-700 text-sm min-w-[100px]')
                    ui.label(intention).classes('text-gray-700 text-sm flex-1')
                
                # Success criteria section (more integrated)
                with ui.row().classes('w-full'):
                    ui.label('Criterio:').classes('font-medium text-blue-700 text-sm min-w-[100px]')
                    ui.label(success_criteria).classes('text-gray-700 text-sm flex-1')
                
                # Arguments and Result sections (more compact)
                details_row = ui.row().classes('w-full gap-2 mt-2')
                with details_row:
                    # Arguments section (compact)
                    if arguments:
                        # Filter out metadata fields for display
                        display_args = {k: v for k, v in arguments.items() 
                                      if k not in ['intention', 'success_criteria']}
                        if display_args:
                            with ui.expansion('Args', icon='code').classes('flex-1').props('dense'):
                                ui.code(json.dumps(display_args, indent=2, ensure_ascii=False)).classes('text-xs w-full')
                    
                    # Result section (compact, formatted like args)
                    if tool_result:
                        result_content = tool_result.get('content', str(tool_result))
                        with ui.expansion('Resultado', icon='check_circle').classes('flex-1').props('dense'):
                            # Format result as JSON-like for consistency with args
                            try:
                                # Try to parse as JSON first
                                if result_content.strip().startswith(('{', '[')):
                                    parsed_result = json.loads(result_content)
                                    ui.code(json.dumps(parsed_result, indent=2, ensure_ascii=False)).classes('text-xs w-full')
                                else:
                                    # If not JSON, format as simple string in code block
                                    ui.code(result_content).classes('text-xs w-full')
                            except (json.JSONDecodeError, AttributeError):
                                # Fallback: show as code block (consistent with args formatting)
                                ui.code(str(result_content)).classes('text-xs w-full')
    
    if container:
        with container:
            render_content()
    else:
        render_content()

def render_interactive_html(container, metadata: dict, message: str):
    """Render interactive HTML with click handlers that send user choices back to chat.
    
    Note: This function depends on window.sendMessageToChat being defined by chat_interface.py
    """
    interaction_id = metadata.get('interaction_id', 'unknown')
    html_content = metadata.get('html_content', '')
    
    # Remove any script tags from html_content
    clean_html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
    
    with container:
        # Render the message text first (if any)
        if message and message.strip():
            ui.markdown(message)
        
        # Define JavaScript function for handling user choices - SINGLE DEFINITION
        ui.run_javascript('''
            window.sendUserChoice = function(choice, buttonElement) {
                console.log('🚀 INICIO CLICK - sendUserChoice ejecutándose!');
                console.log('📋 Parámetros recibidos:', {choice: choice, buttonElement: buttonElement});
                console.log('🔵 sendUserChoice llamada con:', choice);
                console.log('🔵 Elemento del botón:', buttonElement);
                
                // Disable all choice buttons to prevent multiple selections
                const choiceButtons = document.querySelectorAll('[data-choice]');
                console.log('🔵 Botones encontrados:', choiceButtons.length);
                choiceButtons.forEach(btn => {
                    btn.disabled = true;
                    btn.style.opacity = '0.6';
                });
                
                // Highlight selected button
                buttonElement.style.backgroundColor = '#10b981';
                buttonElement.style.borderColor = '#10b981';
                buttonElement.innerHTML = '✓ ' + choice;
                console.log('🔵 Botón actualizado visualmente');
                
                // Usar sendMessageToChat como mecanismo principal
                if (window.sendMessageToChat) {
                    console.log('✅ sendMessageToChat disponible, enviando:', choice);
                    
                    // Llamar a sendMessageToChat y agregar logs para debug
                    try {
                        console.log('🔵 Llamando a sendMessageToChat...');
                        const result = window.sendMessageToChat(choice);
                        console.log('🟢 sendMessageToChat ejecutado sin errores, resultado:', result);
                    } catch (error) {
                        console.error('🔴 Error al ejecutar sendMessageToChat:', error);
                        console.error('🔴 Stack trace:', error.stack);
                        alert('Error específico: ' + error.message);
                    }
                    
                    // Mostrar una breve notificación al usuario
                    const notification = document.createElement('div');
                    notification.textContent = 'Enviando: ' + choice;
                    notification.style.cssText = `
                        position: fixed;
                        top: 20px;
                        right: 20px;
                        background: #10b981;
                        color: white;
                        padding: 12px 20px;
                        border-radius: 8px;
                        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
                        z-index: 10000;
                        font-family: system-ui, -apple-system, sans-serif;
                    `;
                    document.body.appendChild(notification);
                    
                    // Eliminar la notificación después de 1 segundo
                    setTimeout(() => {
                        if (notification.parentNode) {
                            notification.parentNode.removeChild(notification);
                        }
                    }, 1000);
                } else {
                    console.error('❌ No se encontró mecanismo para enviar mensaje');
                    console.log('🔵 window.sendMessageToChat existe?', typeof window.sendMessageToChat);
                    
                    // Mostrar una notificación de error
                    const notification = document.createElement('div');
                    notification.textContent = 'Error: No se pudo enviar el mensaje';
                    notification.style.cssText = `
                        position: fixed;
                        top: 20px;
                        right: 20px;
                        background: #ef4444;
                        color: white;
                        padding: 12px 20px;
                        border-radius: 8px;
                        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
                        z-index: 10000;
                        font-family: system-ui, -apple-system, sans-serif;
                    `;
                    document.body.appendChild(notification);
                    
                    // Eliminar la notificación después de 3 segundos
                    setTimeout(() => {
                        if (notification.parentNode) {
                            notification.parentNode.removeChild(notification);
                        }
                    }, 3000);
                }
            };
            
            console.log('🟡 sendUserChoice definida, tipo:', typeof window.sendUserChoice);
            console.log('🟡 window.sendMessageToChat existe?', typeof window.sendMessageToChat);
        ''')        
        
        # Render the interactive HTML without script tags
        ui.html(clean_html_content).classes('interactive-choice w-full')
