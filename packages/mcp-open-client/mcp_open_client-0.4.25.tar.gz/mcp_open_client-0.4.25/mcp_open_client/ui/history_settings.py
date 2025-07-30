"""
Simple History Settings UI - Rolling Window Configuration
"""

from nicegui import ui
from .history_manager import history_manager

def create_history_settings_ui(container):
    """
    UI for configuring rolling window history with consistent styling
    """
    container.clear()
    container.classes('q-pa-md')
    
    with container:
        ui.label('Configuración de Historial').classes('text-2xl font-bold mb-6')

        
        # Overview card
        with ui.card().classes('w-full mb-6'):
            ui.label('Gestión de Historial de Conversaciones').classes('text-lg font-semibold mb-3')
            ui.label('Configura el límite de mensajes para optimizar el rendimiento. Cuando se supera el límite, los mensajes más antiguos se eliminan automáticamente preservando las secuencias de herramientas.').classes('text-sm text-gray-600 mb-4')
        
        # Configuration card
        with ui.card().classes('w-full mb-6'):
            with ui.row().classes('w-full items-center justify-between mb-3'):
                with ui.row().classes('items-center'):
                    ui.icon('tune').classes('mr-2 text-primary')
                    ui.label('Configuración de Límites').classes('text-lg font-semibold')
            
            # Max messages configuration
            ui.label('Máximo de mensajes por conversación').classes('text-sm text-gray-600 mb-2')
            
            with ui.row().classes('w-full items-center gap-4 mb-4'):
                # Obtener valor actual al momento de crear la UI
                current_max_messages = history_manager.max_messages
                
                max_messages_input = ui.number(
                    value=current_max_messages,
                    min=10,
                    max=200,
                    step=10
                ).classes('flex-1')
                
                # Etiqueta que se actualizará dinámicamente
                max_messages_label = ui.label(f'Actual: {current_max_messages} mensajes').classes('text-sm text-gray-600')
                
            # Max tokens configuration
            ui.separator().classes('q-my-md')
            ui.label('Máximo de tokens por conversación').classes('text-sm text-gray-600 mb-2')
            
            with ui.row().classes('w-full items-center gap-4 mb-4'):
                # Obtener valor actual al momento de crear la UI
                settings = history_manager.settings
                current_max_tokens = settings.get('max_tokens_per_conversation', 50000)
                
                max_tokens_input = ui.number(
                    value=current_max_tokens,
                    min=10000,
                    max=200000,
                    step=1000
                ).classes('flex-1')
                
                # Etiqueta que se actualizará dinámicamente
                max_tokens_label = ui.label(f'Actual: {current_max_tokens:,} tokens').classes('text-sm text-gray-600')
            
            # Update button
            def update_settings():
                # Obtener valores actuales de los inputs
                new_max_messages = int(max_messages_input.value)
                new_max_tokens = int(max_tokens_input.value)
                
                # Actualizar configuración
                success1 = history_manager.update_max_messages(new_max_messages)
                success2 = history_manager.update_setting('max_tokens_per_conversation', new_max_tokens)
                
                
                if success1 and success2:
                    # Get updated settings para verificar
                    updated_settings = history_manager.settings
                    
                    # Verificar que los valores se guardaron correctamente
                    saved_max_messages = history_manager.max_messages
                    saved_max_tokens = updated_settings.get('max_tokens_per_conversation')
                    
                    
                    # Actualizar las etiquetas en la UI
                    max_messages_label.text = f'Actual: {saved_max_messages} mensajes'
                    max_tokens_label.text = f'Actual: {saved_max_tokens:,} tokens'
                    ui.notify(
                        f'✅ Configuración actualizada correctamente:\n'
                        f'- Máximo {saved_max_messages} mensajes\n'
                        f'- Máximo {saved_max_tokens:,} tokens',
                        color='positive',
                        timeout=3000
                    )
                else:
                    ui.notify(
                        f'❌ Error al guardar configuración:\n'
                        f'- Max messages: {"✅" if success1 else "❌"}\n'
                        f'- Max tokens: {"✅" if success2 else "❌"}',
                        color='negative',
                        timeout=5000
                    )
            
            ui.button('Actualizar Configuración', icon='save', on_click=update_settings).props('color=primary')
        
        # Current status card
        with ui.card().classes('w-full mb-6'):
            with ui.row().classes('w-full items-center justify-between mb-3'):
                with ui.row().classes('items-center'):
                    ui.icon('analytics').classes('mr-2 text-info')
                    ui.label('Estado de la Conversación Actual').classes('text-lg font-semibold')
            
            from .chat_handlers import get_current_conversation_id
            conv_id = get_current_conversation_id()
            
            if conv_id:
                conv_stats = history_manager.get_conversation_size(conv_id)
                
                with ui.row().classes('w-full gap-8 mb-4'):
                    with ui.column().classes('flex-1'):
                        ui.label('Mensajes').classes('text-sm text-gray-600')
                        ui.label(f"{conv_stats['message_count']}").classes('text-2xl font-bold text-primary')
                    
                    with ui.column().classes('flex-1'):
                        ui.label('Tokens').classes('text-sm text-gray-600')
                        ui.label(f"{conv_stats['total_tokens']:,}").classes('text-2xl font-bold text-accent')
                
                # Message progress bar
                msg_progress = min(100, (conv_stats['message_count'] / history_manager.max_messages) * 100)
                ui.label(f'Uso del límite de mensajes: {msg_progress:.1f}%').classes('text-sm text-gray-600 mb-2')
                ui.linear_progress(msg_progress / 100).classes('w-full mb-4')
                
                # Token progress bar
                settings = history_manager.settings
                max_tokens = settings.get('max_tokens_per_conversation', 50000)
                token_progress = min(100, (conv_stats['total_tokens'] / max_tokens) * 100)
                
                # Color changes based on percentage
                progress_color = 'primary'
                if token_progress > 90:
                    progress_color = 'negative'
                elif token_progress > 70:
                    progress_color = 'warning'
                    
                ui.label(f'Uso del límite de tokens: {token_progress:.1f}% ({conv_stats["total_tokens"]:,}/{max_tokens:,})').classes('text-sm text-gray-600 mb-2')
                ui.linear_progress(token_progress / 100).props(f'color={progress_color}').classes('w-full mb-4')
                
                # Cleanup button
                def cleanup_now():
                    cleaned = history_manager.cleanup_conversation_if_needed(conv_id)
                    if cleaned:
                        ui.notify('Conversación limpiada', color='positive')
                        ui.navigate.reload()
                    else:
                        ui.notify('No es necesaria limpieza', color='info')
                
                if msg_progress > 80:
                    ui.button('Limpiar Ahora', icon='cleaning_services', on_click=cleanup_now).props('color=warning')
                else:
                    ui.button('Limpiar Ahora', icon='cleaning_services', on_click=cleanup_now).props('color=secondary flat')
            else:
                ui.label('No hay conversación activa').classes('text-sm text-gray-600 text-center p-8')
                ui.label('Inicia una conversación en el chat para ver las estadísticas').classes('text-sm text-gray-600 text-center')

