from nicegui import ui, app
import asyncio
from mcp_open_client.config_utils import load_initial_config_from_files
from mcp_open_client.mcp_client import mcp_client_manager

# File operations removed - using only app.storage.user which is persistent
# Configuration is automatically saved by NiceGUI's storage system

def show_content(container):
    """Main function to display the MCP servers management UI"""
    container.clear()
    container.classes('q-pa-md')
    
    with container:
        ui.label('MCP Servers').classes('text-2xl font-bold mb-6')
        
        # Get the current MCP configuration from user storage
        mcp_config = app.storage.user.get('mcp-config', {})
        
        # If no configuration exists in user storage, initialize with default
        if not mcp_config:
            mcp_config = {"mcpServers": {}}
            app.storage.user['mcp-config'] = mcp_config
        
        servers = mcp_config.get("mcpServers", {})
        
        # Actions card
        with ui.card().classes('w-full mb-6'):
            ui.label('Gestión de Servidores').classes('text-lg font-semibold mb-3')
            ui.label('Conecta herramientas externas a través del protocolo MCP para expandir las capacidades de tu IA.').classes('text-sm text-gray-600 mb-4')
            
            with ui.row().classes('w-full gap-4'):
                ui.button('Agregar Servidor Local', icon='computer', on_click=lambda: show_add_local_dialog()).props('color=primary')
                ui.button('Agregar Servidor Remoto', icon='cloud', on_click=lambda: show_add_remote_dialog()).props('color=info')
                ui.button('Restaurar por Defecto', icon='refresh', on_click=lambda: reset_to_default()).props('color=warning')
                
                def reset_tools_config():
                    from mcp_open_client.config_utils import reset_tools_config as reset_config
                    reset_config()
                    ui.notify('Configuración de tools restablecida - todas las tools están habilitadas', color='positive')
                    # No necesitamos refresh aquí porque las funciones de toggle ya manejan el estado
                
                ui.button('Resetear Tools', icon='settings_backup_restore', on_click=lambda: reset_tools_config()).props('color=secondary').tooltip('Habilitar todas las tools individuales')
        
        # Status overview card
        with ui.card().classes('w-full mb-6'):
            ui.label('Estado Actual').classes('text-lg font-semibold mb-3')
            
            if servers:
                total_count = len(servers)
                ui.label(f'Servidores configurados: {total_count}').classes('text-sm text-gray-600')
                ui.label('Gestiona herramientas individuales en las secciones de abajo.').classes('text-sm text-gray-600')
            else:
                ui.label('No hay servidores configurados').classes('text-sm text-gray-600')
        
        # Meta Tools List Card
        with ui.card().classes('w-full mb-6'):
            ui.label('Meta Tools Disponibles').classes('text-lg font-semibold mb-3')
            ui.label('Activa o desactiva herramientas individuales que el LLM puede usar para interactuar con el sistema.').classes('text-sm text-gray-600 mb-2')
            
            # Obtener todas las meta tools disponibles
            from mcp_open_client.meta_tools import meta_tool_registry
            from mcp_open_client.config_utils import is_tool_enabled, set_tool_enabled
            
            # Mostrar lista de meta tools con switches
            if meta_tool_registry.tools:
                # Crear una tabla manual con divs
                with ui.element('div').classes('w-full border rounded').style('max-height: 300px; overflow-y: auto;'):
                    # Encabezados
                    with ui.element('div').classes('bg-primary text-white flex'):
                        with ui.element('div').classes('p-2 w-16'):
                            ui.label('Estado')
                        with ui.element('div').classes('p-2 w-1/3'):
                            ui.label('Nombre')
                        with ui.element('div').classes('p-2 w-1/2'):
                            ui.label('Descripción')
                    
                    # Filas con switches
                    for name, schema in meta_tool_registry.tool_schemas.items():
                        with ui.element('div').classes('flex border-b hover:bg-gray-100 items-center'):
                            with ui.element('div').classes('p-2 w-16'):
                                def toggle_meta_tool(enabled, tool_name=name):
                                    set_tool_enabled(tool_name, enabled, 'meta')
                                    ui.notify(f"Meta tool '{tool_name}' {'habilitada' if enabled else 'deshabilitada'}", color='positive')
                                
                                ui.switch(
                                    value=is_tool_enabled(name, 'meta'),
                                    on_change=lambda e, tool_name=name: toggle_meta_tool(e.value, tool_name)
                                ).props('color=primary size=sm')
                            
                            with ui.element('div').classes('p-2 font-mono text-xs w-1/3'):
                                ui.label(name)
                            with ui.element('div').classes('p-2 text-sm w-1/2'):
                                ui.label(schema['description'])
            else:
                ui.label('No hay Meta Tools registradas').classes('text-sm italic text-gray-500')
        
        # MCP Tools Management Card
        mcp_tools_container = ui.column().classes('w-full')
        
        def refresh_mcp_tools_list():
            """Refresh the MCP tools list UI"""
            mcp_tools_container.clear()
            
            with mcp_tools_container:
                with ui.card().classes('w-full mb-6'):
                    ui.label('MCP Tools Disponibles').classes('text-lg font-semibold mb-3')
                    ui.label('Activa o desactiva herramientas individuales de los servidores MCP conectados.').classes('text-sm text-gray-600 mb-2')
                    
                    # Obtener todas las MCP tools disponibles
                    from mcp_open_client.config_utils import is_tool_enabled, set_tool_enabled
                    
                    # Función asíncrona para obtener tools
                    async def get_mcp_tools_for_ui():
                        try:
                            if not mcp_client_manager.is_connected():
                                return []
                            
                            mcp_tools = await mcp_client_manager.list_tools()
                            
                            # Crear lista de tools individuales extrayendo servidor del nombre
                            individual_tools = []
                            
                            for tool in mcp_tools:
                                full_tool_name = tool.get('name') if isinstance(tool, dict) else getattr(tool, 'name', '')
                                tool_desc = tool.get('description') if isinstance(tool, dict) else getattr(tool, 'description', '')
                                
                                # Extraer servidor y nombre real de la tool
                                # Formato: "servidor_nombre_tool" -> servidor="servidor", tool="nombre_tool"
                                if '_' in full_tool_name:
                                    # Buscar el primer _ para separar servidor del resto
                                    parts = full_tool_name.split('_', 1)
                                    server_name = parts[0]
                                    actual_tool_name = parts[1]
                                else:
                                    # Si no tiene _, asumir que no tiene prefijo de servidor
                                    server_name = 'unknown'
                                    actual_tool_name = full_tool_name
                                
                                tool_id = f"{server_name}:{actual_tool_name}"
                                individual_tools.append({
                                    'tool_name': actual_tool_name,
                                    'server_name': server_name,
                                    'tool_id': tool_id,
                                    'description': tool_desc
                                })
                            
                            return individual_tools
                        except Exception as e:
                            print(f"Error getting MCP tools: {e}")
                            return []
                    
                    # Obtener tools de forma síncrona para la UI
                    import asyncio
                    try:
                        # Crear un contenedor para las tools
                        mcp_tools_list_container = ui.column().classes('w-full')
                        
                        # Cargar tools de forma asíncrona
                        async def load_and_display_tools():
                            tools_list = await get_mcp_tools_for_ui()
                            
                            mcp_tools_list_container.clear()
                            
                            with mcp_tools_list_container:
                                if tools_list:
                                    # Crear tabla de MCP tools
                                    with ui.element('div').classes('w-full border rounded').style('max-height: 400px; overflow-y: auto;'):
                                        # Encabezados
                                        with ui.element('div').classes('bg-secondary text-white flex'):
                                            with ui.element('div').classes('p-2 w-16'):
                                                ui.label('Estado')
                                            with ui.element('div').classes('p-2 w-1/4'):
                                                ui.label('Servidor')
                                            with ui.element('div').classes('p-2 w-1/4'):
                                                ui.label('Tool')
                                            with ui.element('div').classes('p-2 w-1/3'):
                                                ui.label('Descripción')
                                        
                                        # Filas con switches - cada tool individual
                                        for tool_info in tools_list:
                                            with ui.element('div').classes('flex border-b hover:bg-gray-100 items-center'):
                                                with ui.element('div').classes('p-2 w-16'):
                                                    def toggle_mcp_tool(enabled, tool_id=tool_info['tool_id']):
                                                        set_tool_enabled(tool_id, enabled, 'mcp')
                                                        ui.notify(f"MCP tool '{tool_id}' {'habilitada' if enabled else 'deshabilitada'}", color='positive')
                                                    
                                                    ui.switch(
                                                        value=is_tool_enabled(tool_info['tool_id'], 'mcp'),
                                                        on_change=lambda e, tool_id=tool_info['tool_id']: toggle_mcp_tool(e.value, tool_id)
                                                    ).props('color=secondary size=sm')
                                                
                                                with ui.element('div').classes('p-2 text-xs w-1/4'):
                                                    ui.label(tool_info['server_name'])
                                                with ui.element('div').classes('p-2 font-mono text-xs w-1/4'):
                                                    ui.label(tool_info['tool_name'])
                                                with ui.element('div').classes('p-2 text-sm w-1/3'):
                                                    ui.label(tool_info['description'])
                                else:
                                    ui.label('No hay MCP Tools disponibles. Asegúrate de que los servidores MCP estén conectados.').classes('text-sm italic text-gray-500')
                        
                        # Ejecutar la carga asíncrona
                        asyncio.create_task(load_and_display_tools())
                        
                    except Exception as e:
                        ui.label(f'Error cargando MCP tools: {str(e)}').classes('text-sm text-red-500')
        
        # Llamar la función para mostrar las MCP tools
        refresh_mcp_tools_list()
        
        # Create a container for the servers list that can be refreshed
        servers_container = ui.column().classes('w-full')
        
        def refresh_servers_list():
            """Refresh the servers list UI"""
            servers_container.clear()
            
            # Get the latest config
            current_config = app.storage.user.get('mcp-config', {})
            current_servers = current_config.get("mcpServers", {})
            
            if not current_servers:
                with servers_container:
                    with ui.card().classes('w-full mb-6'):
                        ui.label('No hay servidores configurados').classes('text-lg font-semibold text-center p-8')
                        ui.label('Haz clic en "Agregar Servidor" para comenzar').classes('text-sm text-gray-600 text-center')
                return
            
            with servers_container:
                ui.label('Servidores Configurados').classes('text-lg font-semibold mb-4')
                
                for name, config in current_servers.items():
                    # Determine server type and details
                    if 'url' in config:
                        server_type = 'HTTP'
                        details = config.get('url', '')
                        icon = 'cloud'
                        color = 'info'
                    elif 'command' in config:
                        server_type = 'Local'
                        details = f"{config.get('command', '')} {' '.join(config.get('args', []))}"
                        icon = 'computer'
                        color = 'secondary'
                    else:
                        server_type = 'Desconocido'
                        details = ''
                        icon = 'help'
                        color = 'warning'
                    
                    
                    # Server card
                    with ui.card().classes('w-full mb-4'):
                        with ui.row().classes('w-full items-center justify-between mb-3'):
                            with ui.row().classes('items-center'):
                                ui.icon(icon).classes(f'mr-2 text-{color}')
                                ui.label(name).classes('text-lg font-semibold')
                            
                            with ui.row().classes('gap-2'):
                                ui.button('', icon='edit', on_click=lambda name=name, config=config: show_edit_dialog(name, config)).props('flat round color=primary size=sm').tooltip('Editar')
                                ui.button('', icon='delete', on_click=lambda name=name: show_delete_dialog(name)).props('flat round color=negative size=sm').tooltip('Eliminar')
                        
                        ui.label(f'Tipo: {server_type}').classes('text-sm text-gray-600 mb-2')
                        ui.label(details).classes('text-sm font-mono bg-gray-100 p-2 rounded')
        
        
        # Function to delete a server
        def delete_server(server_name):
            """Delete a server from the configuration"""
            current_config = app.storage.user.get('mcp-config', {})
            if "mcpServers" in current_config and server_name in current_config["mcpServers"]:
                del current_config["mcpServers"][server_name]
                app.storage.user['mcp-config'] = current_config
                
                # Save configuration to file
                # Configuration automatically saved in user storage
                
                ui.notify(f"Server '{server_name}' deleted", color='positive')
                
                # Update the MCP client manager with the new configuration
                async def update_mcp_client():
                    try:
                        success = await mcp_client_manager.initialize(current_config)
                        if success:
                            active_servers = mcp_client_manager.get_active_servers()
                            # Use storage for safe notification from background tasks
                            app.storage.user['mcp_status'] = f"Connected to {len(active_servers)} MCP servers"
                            app.storage.user['mcp_status_color'] = 'positive'
                        else:
                            app.storage.user['mcp_status'] = "No active MCP servers"
                            app.storage.user['mcp_status_color'] = 'warning'
                    except Exception as e:
                        app.storage.user['mcp_status'] = f"Error connecting to MCP servers: {str(e)}"
                        app.storage.user['mcp_status_color'] = 'negative'
                    
                    # Only refresh the UI after the client has been initialized
                    # This prevents potential race conditions
                    refresh_servers_list()
                    refresh_mcp_tools_list()
                
                # Run the update asynchronously
                asyncio.create_task(update_mcp_client())
        
        # Dialog to confirm server deletion
        def show_delete_dialog(server_name):
            """Show confirmation dialog to delete a server"""
            with ui.dialog() as dialog, ui.card().classes('p-4'):
                ui.label(f'Delete Server: {server_name}').classes('text-h6')
                ui.label('Are you sure you want to delete this server? This action cannot be undone.')
                
                with ui.row().classes('w-full justify-end'):
                    ui.button('Cancel', on_click=dialog.close).props('flat')
                    ui.button('Delete', on_click=lambda: [delete_server(server_name), dialog.close()]).props('color=negative')
            
            # Open the dialog
            dialog.open()
        
        # Dialog to edit a server
        def show_edit_dialog(server_name, server_config):
            """Show dialog to edit a server"""
            with ui.dialog() as dialog, ui.card().classes('w-96 p-4'):
                ui.label(f'Edit Server: {server_name}').classes('text-h6')
                
                # Determine server type
                is_http = 'url' in server_config
                
                # Server type selection (disabled for editing)
                server_type = 'HTTP' if is_http else 'Local'
                ui.label(f'Server Type: {server_type}').classes('text-bold')
                
                # HTTP server fields
                if is_http:
                    url = ui.input('Server URL', value=server_config.get('url', '')).classes('w-full')
                    transport_options = ['streamable-http', 'http', 'sse']
                    transport = ui.select(
                        transport_options,
                        value=server_config.get('transport', 'streamable-http'),
                        label='Transport'
                    ).classes('w-full')
                
                # Local command fields
                else:
                    command = ui.input('Command', value=server_config.get('command', '')).classes('w-full')
                    args = ui.input(
                        'Arguments (space-separated)',
                        value=' '.join(server_config.get('args', []))
                    ).classes('w-full')
                    
                    env_text = ''
                    if 'env' in server_config and server_config['env']:
                        env_text = '\n'.join([f"{k}={v}" for k, v in server_config['env'].items()])
                    
                    env_vars = ui.input(
                        'Environment Variables (key=value, one per line)',
                        value=env_text
                    ).classes('w-full').props('type=textarea rows=3')
                
                # Buttons
                with ui.row().classes('w-full justify-end'):
                    ui.button('Cancel', on_click=dialog.close).props('flat')
                    
                    def update_server():
                        current_config = app.storage.user.get('mcp-config', {})
                        if "mcpServers" not in current_config or server_name not in current_config["mcpServers"]:
                            ui.notify(f"Server '{server_name}' not found", color='negative')
                            return
                        
                        # Preserve the disabled status
                        is_disabled = current_config["mcpServers"][server_name].get('disabled', False)
                        
                        # Create updated config
                        updated_config = {"disabled": is_disabled}
                        
                        if is_http:
                            if not url.value:
                                ui.notify('URL is required', color='negative')
                                return
                            updated_config["url"] = url.value
                            updated_config["transport"] = transport.value
                        else:
                            if not command.value:
                                ui.notify('Command is required', color='negative')
                                return
                            updated_config["command"] = command.value
                            
                            if args.value:
                                updated_config["args"] = args.value.split()
                            
                            if env_vars.value:
                                env_dict = {}
                                for line in env_vars.value.splitlines():
                                    if '=' in line:
                                        key, value = line.split('=', 1)
                                        env_dict[key.strip()] = value.strip()
                                if env_dict:
                                    updated_config["env"] = env_dict
                        
                        # Update the configuration
                        current_config["mcpServers"][server_name] = updated_config
                        app.storage.user['mcp-config'] = current_config
                        
                        # Configuration automatically saved in user storage
                        
                        # Update the MCP client manager with the new configuration
                        async def update_mcp_client():
                            try:
                                success = await mcp_client_manager.initialize(current_config)
                                if success:
                                    active_servers = mcp_client_manager.get_active_servers()
                                    # Use storage for safe notification from background tasks
                                    app.storage.user['mcp_status'] = f"Connected to {len(active_servers)} MCP servers"
                                    app.storage.user['mcp_status_color'] = 'positive'
                                else:
                                    app.storage.user['mcp_status'] = "No active MCP servers"
                                    app.storage.user['mcp_status_color'] = 'warning'
                            except Exception as e:
                                app.storage.user['mcp_status'] = f"Error connecting to MCP servers: {str(e)}"
                                app.storage.user['mcp_status_color'] = 'negative'
                            
                            # Only refresh the UI after the client has been initialized
                            # This prevents potential race conditions
                            refresh_servers_list()
                            refresh_mcp_tools_list()
                        
                        # Run the update asynchronously
                        asyncio.create_task(update_mcp_client())
                        
                        ui.notify(f"Server '{server_name}' updated", color='positive')
                        dialog.close()
                    
                    ui.button('Update', on_click=update_server).props('color=primary')
            
            # Open the dialog
            dialog.open()
        
        # Dialog to add a local server
        def show_add_local_dialog():
            """Show dialog to add a local server"""
            with ui.dialog() as dialog, ui.card().classes('w-96 p-4'):
                ui.label('Add Local MCP Server').classes('text-h6')
                
                server_name = ui.input('Server Name').classes('w-full')
                command = ui.input('Command').classes('w-full')
                args = ui.input('Arguments (space-separated)').classes('w-full')
                env_vars = ui.input('Environment Variables (key=value, one per line)').classes('w-full')
                env_vars.props('type=textarea rows=3')
                
                with ui.row().classes('w-full justify-end'):
                    ui.button('Cancel', on_click=dialog.close).props('flat')
                    
                    def add_local_server():
                        name = server_name.value.strip()
                        if not name:
                            ui.notify('Server name is required', color='negative')
                            return
                        
                        if not command.value:
                            ui.notify('Command is required', color='negative')
                            return
                        
                        current_config = app.storage.user.get('mcp-config', {})
                        if "mcpServers" not in current_config:
                            current_config["mcpServers"] = {}
                        
                        if name in current_config["mcpServers"]:
                            ui.notify(f"Server '{name}' already exists", color='negative')
                            return
                        
                        new_config = {"disabled": False, "command": command.value}
                        
                        if args.value:
                            new_config["args"] = args.value.split()
                        
                        if env_vars.value:
                            env_dict = {}
                            for line in env_vars.value.splitlines():
                                if '=' in line:
                                    key, value = line.split('=', 1)
                                    env_dict[key.strip()] = value.strip()
                            if env_dict:
                                new_config["env"] = env_dict
                        
                        current_config["mcpServers"][name] = new_config
                        app.storage.user['mcp-config'] = current_config
                        
                        async def update_mcp_client():
                            try:
                                success = await mcp_client_manager.initialize(current_config)
                                if success:
                                    active_servers = mcp_client_manager.get_active_servers()
                                    app.storage.user['mcp_status'] = f"Connected to {len(active_servers)} MCP servers"
                                    app.storage.user['mcp_status_color'] = 'positive'
                                else:
                                    app.storage.user['mcp_status'] = "No active MCP servers"
                                    app.storage.user['mcp_status_color'] = 'warning'
                            except Exception as e:
                                app.storage.user['mcp_status'] = f"Error connecting to MCP servers: {str(e)}"
                                app.storage.user['mcp_status_color'] = 'negative'
                            
                            refresh_servers_list()
                            refresh_mcp_tools_list()
                        
                        asyncio.create_task(update_mcp_client())
                        ui.notify(f"Local server '{name}' added", color='positive')
                        dialog.close()
                    
                    ui.button('Add', on_click=add_local_server).props('color=primary')
            
            dialog.open()
        
        # Dialog to add a remote server
        def show_add_remote_dialog():
            """Show dialog to add a remote server"""
            with ui.dialog() as dialog, ui.card().classes('w-96 p-4'):
                ui.label('Add Remote MCP Server').classes('text-h6')
                
                server_name = ui.input('Server Name').classes('w-full')
                url = ui.input('Server URL').classes('w-full')
                transport = ui.select(
                    ['streamable-http', 'http', 'sse'],
                    value='streamable-http',
                    label='Transport'
                ).classes('w-full')
                
                with ui.row().classes('w-full justify-end'):
                    ui.button('Cancel', on_click=dialog.close).props('flat')
                    
                    def add_remote_server():
                        name = server_name.value.strip()
                        if not name:
                            ui.notify('Server name is required', color='negative')
                            return
                        
                        if not url.value:
                            ui.notify('URL is required', color='negative')
                            return
                        
                        current_config = app.storage.user.get('mcp-config', {})
                        if "mcpServers" not in current_config:
                            current_config["mcpServers"] = {}
                        
                        if name in current_config["mcpServers"]:
                            ui.notify(f"Server '{name}' already exists", color='negative')
                            return
                        
                        new_config = {
                            "disabled": False,
                            "url": url.value,
                            "transport": transport.value
                        }
                        
                        current_config["mcpServers"][name] = new_config
                        app.storage.user['mcp-config'] = current_config
                        
                        async def update_mcp_client():
                            try:
                                success = await mcp_client_manager.initialize(current_config)
                                if success:
                                    active_servers = mcp_client_manager.get_active_servers()
                                    app.storage.user['mcp_status'] = f"Connected to {len(active_servers)} MCP servers"
                                    app.storage.user['mcp_status_color'] = 'positive'
                                else:
                                    app.storage.user['mcp_status'] = "No active MCP servers"
                                    app.storage.user['mcp_status_color'] = 'warning'
                            except Exception as e:
                                app.storage.user['mcp_status'] = f"Error connecting to MCP servers: {str(e)}"
                                app.storage.user['mcp_status_color'] = 'negative'
                            
                            refresh_servers_list()
                            refresh_mcp_tools_list()
                        
                        asyncio.create_task(update_mcp_client())
                        ui.notify(f"Remote server '{name}' added", color='positive')
                        dialog.close()
                    
                    ui.button('Add', on_click=add_remote_server).props('color=primary')
            
            dialog.open()
        
        # Function to reset configuration to default
        def reset_to_default():
            """Reset the MCP configuration to default values from files"""
            try:
                # Load initial configuration from files
                initial_configs = load_initial_config_from_files()
                default_config = initial_configs.get('mcp-config', {"mcpServers": {}})
                
                print(f"Reset to default - MCP config loaded from files: {default_config}")
                
                # Update the user storage with default configuration from files
                app.storage.user['mcp-config'] = default_config
                
                # Update the MCP client manager with the default configuration
                async def update_mcp_client():
                    try:
                        success = await mcp_client_manager.initialize(default_config)
                        if success:
                            active_servers = mcp_client_manager.get_active_servers()
                            # Use storage for safe notification from background tasks
                            app.storage.user['mcp_status'] = f"Connected to {len(active_servers)} MCP servers"
                            app.storage.user['mcp_status_color'] = 'positive'
                        else:
                            app.storage.user['mcp_status'] = "No active MCP servers"
                            app.storage.user['mcp_status_color'] = 'warning'
                    except Exception as e:
                        app.storage.user['mcp_status'] = f"Error connecting to MCP servers: {str(e)}"
                        app.storage.user['mcp_status_color'] = 'negative'
                    
                    # Refresh the UI after the client has been initialized
                    refresh_servers_list()
                    refresh_mcp_tools_list()
                
                # Run the update asynchronously
                asyncio.create_task(update_mcp_client())
                
                ui.notify('Configuration reset to default values', color='positive')
            except Exception as e:
                ui.notify(f'Error resetting configuration: {str(e)}', color='negative')
        
        # Initial load of the servers list
        refresh_servers_list()