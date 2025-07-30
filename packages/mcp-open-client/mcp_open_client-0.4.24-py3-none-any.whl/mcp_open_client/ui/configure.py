from nicegui import ui, app
from mcp_open_client.config_utils import load_initial_config_from_files
from mcp_open_client.api_client import APIClient
import asyncio

# Global API client instance for updates
_api_client_instance = None

def get_api_client():
    """Get or create API client instance"""
    global _api_client_instance
    if _api_client_instance is None:
        _api_client_instance = APIClient()
    return _api_client_instance

def show_content(container):
    """Display configuration UI with consistent styling"""
    container.clear()
    container.classes('q-pa-md')
    
    with container:
        ui.label('Configuración').classes('text-2xl font-bold mb-6')
        
        # Overview card
        with ui.card().classes('w-full mb-6'):
            ui.label('Configuración del Sistema').classes('text-lg font-semibold mb-3')
            ui.label('Configura tu proveedor de IA, modelo preferido y comportamiento del sistema. Los cambios se guardan automáticamente y se aplican a futuras conversaciones.').classes('text-sm text-gray-600 mb-4')
        # Function to get current config (always fresh from storage)
        def get_current_config():
            try:
                result = app.storage.user.get('user-settings', {})
                return result
            except Exception as e:
                return {}

        # Load current configuration
        config = get_current_config()

        # API Configuration card
        with ui.card().classes('w-full mb-6'):
            with ui.row().classes('w-full items-center justify-between mb-3'):
                with ui.row().classes('items-center'):
                    ui.icon('key').classes('mr-2 text-primary')
                    ui.label('Configuración de API').classes('text-lg font-semibold')
            
            with ui.column().classes('w-full gap-4'):
                # API Key
                ui.label('Clave API').classes('text-sm text-gray-600')
                # Safe handling of API key value
                api_key_value = config.get('api_key', '')
                # Truncate very long API keys for display
                if len(api_key_value) > 100:
                    api_key_value = api_key_value[:100]
                
                api_key_input = ui.input(
                    placeholder='Ingresa tu clave API',
                    value=api_key_value,
                    password=True,
                    password_toggle_button=True
                ).classes('w-full')
                
                # Base URL
                ui.label('URL Base').classes('text-sm text-gray-600')
                base_url_input = ui.input(
                    placeholder='http://localhost:8080 o https://api.openai.com/v1',
                    value=config.get('base_url', 'http://192.168.58.101:8123')
                ).classes('w-full')
                
                # Info tip
                with ui.row().classes('w-full items-center'):
                    ui.icon('lightbulb').classes('mr-2 text-amber-600')
                    ui.label('Haz clic en "Cargar Modelos" después de cambiar la configuración para obtener modelos disponibles').classes('text-sm text-gray-600')

        # System Prompt card
        with ui.card().classes('w-full mb-6'):
            with ui.row().classes('w-full items-center justify-between mb-3'):
                with ui.row().classes('items-center'):
                    ui.icon('psychology').classes('mr-2 text-secondary')
                    ui.label('Prompt del Sistema').classes('text-lg font-semibold')
            
            ui.label('Define cómo debe comportarse el asistente').classes('text-sm text-gray-600 mb-2')
            
            system_prompt_input = ui.textarea(
                value=config.get('system_prompt', 'You are a helpful assistant.'),
                placeholder='Describe cómo quieres que se comporte el asistente...'
            ).classes('w-full').props('rows=8')
            
            # Info tip
            with ui.row().classes('w-full items-center mt-2'):
                ui.icon('info').classes('mr-2 text-blue-600')
                ui.label('El prompt del sistema define el comportamiento y personalidad del asistente. Se envía como primer mensaje en cada conversación.').classes('text-sm text-gray-600')

        # Advanced Settings card
        with ui.card().classes('w-full mb-6'):
            with ui.row().classes('w-full items-center justify-between mb-3'):
                with ui.row().classes('items-center'):
                    ui.icon('settings').classes('mr-2 text-secondary')
                    ui.label('Configuración Avanzada').classes('text-lg font-semibold')
            
            with ui.column().classes('w-full gap-4'):
                # Tool Choice Required
                ui.label('Forzar Uso de Herramientas').classes('text-sm text-gray-600')
                
                tool_choice_required_switch = ui.switch(
                    text='Forzar uso de herramientas cuando estén disponibles',
                    value=config.get('tool_choice_required', False)
                ).classes('w-full')
                
                # Info tip for tool choice
                with ui.row().classes('w-full items-center mt-2'):
                    ui.icon('info').classes('mr-2 text-blue-600')
                    ui.label('Cuando está activado, el LLM estará obligado a usar una herramienta en cada respuesta si hay herramientas disponibles. Útil para asegurar que el asistente siempre use las herramientas MCP cuando sea posible.').classes('text-sm text-gray-600')

        # Model Selection card
        with ui.card().classes('w-full mb-6'):
            with ui.row().classes('w-full items-center justify-between mb-3'):
                with ui.row().classes('items-center'):
                    ui.icon('smart_toy').classes('mr-2 text-accent')
                    ui.label('Selección de Modelo').classes('text-lg font-semibold')
                
                # Model selection - Dynamic loading
                model_select_container = ui.column().classes('w-full')
                model_select = None
                
                async def load_models():
                    nonlocal model_select
                    model_select_container.clear()
                    
                    # Default fallback models
                    default_models = ['gpt-3.5-turbo', 'gpt-4', 'claude-3-5-sonnet', 'claude-3-opus']
                    # Get current config from user storage (updated)
                    current_config = get_current_config()
                    current_model = current_config.get('model', 'claude-3-5-sonnet')
                    
                    with model_select_container:
                        # Show loading state
                        loading_container = ui.row().classes('w-full items-center q-pa-md')
                        with loading_container:
                            ui.spinner('dots', size='sm').classes('q-mr-sm')
                            ui.label('Loading available models...')
                        
                        # Save current config to restore later
                        original_config = get_current_config()
                        
                        try:
                            # Temporarily update API client with current form settings for testing
                            temp_config = {
                                'api_key': api_key_input.value,
                                'base_url': base_url_input.value,
                                'model': current_model
                            }
                            app.storage.user['user-settings'] = temp_config
                            
                            # Try to get models from API with timeout
                            api_client = get_api_client()
                            api_client.update_settings()
                            
                            # Add timeout to prevent hanging
                            models_data = await asyncio.wait_for(
                                api_client.list_models(), 
                                timeout=10.0  # 10 second timeout
                            )
                            
                            # Extract model names/IDs
                            if models_data:
                                model_options = []
                                for model in models_data:
                                    # Handle different response formats
                                    if isinstance(model, dict):
                                        model_name = model.get('id') or model.get('name') or model.get('model')
                                        if model_name:
                                            model_options.append(model_name)
                                
                                if not model_options:
                                    model_options = default_models
                                    ui.notify('No models found in API response, using defaults', color='warning', position='top')
                                else:
                                    ui.notify(f'Loaded {len(model_options)} models from API', color='positive', position='top')
                            else:
                                model_options = default_models
                                ui.notify('Empty response from API, using default models', color='warning', position='top')
                                
                        except asyncio.TimeoutError:
                            model_options = default_models
                            ui.notify('API request timed out (10s), using default models', color='warning', position='top')
                        except Exception as e:
                            print(f"Error loading models from API: {str(e)}")
                            model_options = default_models
                            ui.notify('Failed to load models from API, using defaults', color='warning', position='top')
                        finally:
                            # Restore original config (don't auto-save test settings)
                            app.storage.user['user-settings'] = original_config
                            api_client = get_api_client()
                            api_client.update_settings()
                        
                        # Always ensure we have model_options (even if API failed)
                        if 'model_options' not in locals():
                            model_options = default_models
                            ui.notify('Using default models due to API error', color='warning', position='top')
                        
                        # Clear loading state
                        loading_container.clear()
                        
                        # Create model select with loaded options
                        # Ensure current model is in options, if not add it
                        if current_model not in model_options:
                            model_options.insert(0, current_model)
                        
                        # Always create the model_select (never leave it as None)
                        model_select = ui.select(
                            label='Model', 
                            options=model_options, 
                            value=current_model
                        ).classes('w-full')
                        
                        # Add refresh button
                        with ui.row().classes('w-full items-center q-mt-md q-col-gutter-sm'):
                            ui.button('🔄 Refresh Models', on_click=load_models).props('size=sm color=secondary outline').classes('col-auto')
                            ui.label('Reload models using current API settings').classes('col text-caption text-grey-6')
                
                # Create initial model selector with defaults (no API call)
                def create_initial_model_select():
                    nonlocal model_select
                    model_select_container.clear()
                    
                    default_models = ['gpt-3.5-turbo', 'gpt-4', 'claude-3-5-sonnet', 'claude-3-opus']
                    # Get current config from user storage (updated)
                    current_config = get_current_config()
                    current_model = current_config.get('model', 'claude-3-5-sonnet')
                    
                    # Ensure current model is in options
                    if current_model not in default_models:
                        default_models.insert(0, current_model)
                    
                    with model_select_container:
                        model_select = ui.select(
                            label='Model', 
                            options=default_models, 
                            value=current_model
                        ).classes('w-full')
                        
                        # Add info and refresh button
                        with ui.row().classes('w-full items-center q-mt-md q-col-gutter-sm'):
                            ui.button('🔄 Load Models from API', on_click=load_models).props('size=sm color=primary outline').classes('col-auto')
                            ui.label('Click to load available models from your API').classes('col text-caption text-grey-6')
                        
                        with ui.row().classes('w-full q-mt-sm items-center'):
                            ui.icon('info').classes('q-mr-sm text-blue-6')
                            ui.label('Using default models. Click "Load Models from API" to get models from your server.').classes('text-caption text-grey-7')
                
                # Create initial state
                create_initial_model_select()
            
            # Auto-refresh fields on page load to ensure they reflect current storage
            def auto_refresh_on_load():
                current_config = get_current_config()
                if current_config:  # Only if there's saved config
                    api_key_input.value = current_config.get('api_key', '')
                    base_url_input.value = current_config.get('base_url', 'http://192.168.58.101:8123')
                    system_prompt_input.value = current_config.get('system_prompt', 'You are a helpful assistant.')
                    tool_choice_required_switch.value = current_config.get('tool_choice_required', False)
                    # Force UI update
                    api_key_input.update()
                    base_url_input.update()
                    system_prompt_input.update()
                    tool_choice_required_switch.update()
            
            # Call auto-refresh
            auto_refresh_on_load()
            
            def save_config():
                # Check if model_select is available (should always be available now)
                if model_select is None:
                    ui.notify('Error: Model selector not initialized. Try refreshing models first.', color='warning', position='top')
                    return
                
                # Create new user config (independent from MCP config)
                new_user_config = {
                    'api_key': api_key_input.value,
                    'base_url': base_url_input.value,
                    'model': model_select.value,
                    'system_prompt': system_prompt_input.value,
                    'tool_choice_required': tool_choice_required_switch.value
                }
                
                # Update user storage - automatically persistent
                app.storage.user['user-settings'] = new_user_config
                
                # Update API client with new settings
                try:
                    api_client = get_api_client()
                    api_client.update_settings()
                    ui.notify('Configuration saved and API client updated successfully!', color='positive', position='top')
                except Exception as e:
                    print(f"Error updating API client: {str(e)}")
                    ui.notify('Configuration saved, but API client update failed', color='warning', position='top')
            
            # Add a button to reset configuration to defaults
            def reset_to_factory():
                # Check if model_select is available (should always be available now)
                if model_select is None:
                    ui.notify('Error: Model selector not initialized. Try refreshing models first.', color='warning', position='top')
                    return
                    
                try:
                    initial_configs = load_initial_config_from_files()
                    initial_config = initial_configs.get('user-settings', {})
                    
                    # Update input fields
                    api_key_input.value = initial_config.get('api_key', '')
                    base_url_input.value = initial_config.get('base_url', 'http://192.168.58.101:8123')
                    model_select.value = initial_config.get('model', 'claude-3-5-sonnet')
                    system_prompt_input.value = initial_config.get('system_prompt', 'You are a helpful assistant.')
                    tool_choice_required_switch.value = initial_config.get('tool_choice_required', False)
                    
                    # Update user storage with initial configuration
                    app.storage.user['user-settings'] = initial_config
                    
                    # Force UI update
                    api_key_input.update()
                    base_url_input.update()
                    model_select.update()
                    system_prompt_input.update()
                    tool_choice_required_switch.update()
                    
                    # Update API client with new settings
                    api_client = get_api_client()
                    api_client.update_settings()
                    
                    ui.notify('Configuration reset to factory settings and API client updated successfully!', color='positive', position='top')
                    
                except Exception as e:
                    print(f"Error during factory reset: {str(e)}")
                    ui.notify(f'Error resetting configuration: {str(e)}', color='negative', position='top')

            def confirm_reset():
                with ui.dialog() as dialog, ui.card().classes('q-pa-lg'):
                    with ui.column().classes('items-center text-center q-gutter-md'):
                        ui.icon('warning', size='lg').classes('text-orange-6')
                        ui.label('Reset to Factory Settings').classes('text-h6 text-weight-bold')
                        ui.label('This will overwrite your current configuration with the factory defaults.').classes('text-body2 text-grey-7')
                        
                        with ui.row().classes('q-gutter-md justify-center'):
                            ui.button('Cancel', on_click=dialog.close).props('color=secondary outline')
                            ui.button('🔄 Confirm Reset', on_click=lambda: [reset_to_factory(), dialog.close()]).props('color=negative')
                dialog.open()

        # Actions card
        with ui.card().classes('w-full mb-6'):
            with ui.row().classes('w-full items-center justify-between mb-3'):
                with ui.row().classes('items-center'):
                    ui.icon('save').classes('mr-2 text-positive')
                    ui.label('Guardar Configuración').classes('text-lg font-semibold')
            
            ui.label('Los cambios se aplicarán inmediatamente a nuevas conversaciones').classes('text-sm text-gray-600 mb-4')
            
            with ui.row().classes('gap-4'):
                ui.button('Guardar Configuración', icon='save', on_click=save_config).props('color=primary')
                ui.button('Restablecer por Defecto', icon='refresh', on_click=confirm_reset).props('color=warning outline')
