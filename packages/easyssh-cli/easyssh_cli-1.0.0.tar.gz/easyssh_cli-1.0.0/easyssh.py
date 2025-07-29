#!/usr/bin/env python3
"""
EasySSH - Un outil CLI pour faciliter les connexions SSH
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Optional

try:
    import click
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich.prompt import Prompt
    from rich.table import Table
    from rich.align import Align
    from textual.app import App, ComposeResult
    from textual.containers import Container, Vertical, Horizontal
    from textual.widgets import Input, DataTable, Header, Footer, Static
    from textual.binding import Binding
    import pyfiglet
except ImportError as e:
    print(f"❌ Module manquant: {e}")
    print("🔧 Installez les dépendances avec:")
    print("   pip install rich textual pyfiglet colorama paramiko click")
    print("   ou")
    print("   pip3 install rich textual pyfiglet colorama paramiko click")
    sys.exit(1)

console = Console()

class SSHServer:
    """Représente un serveur SSH"""
    def __init__(self, name: str, host: str, user: str, port: int = 22, 
                 key_path: Optional[str] = None, description: str = ""):
        self.name = name
        self.host = host
        self.user = user
        self.port = port
        self.key_path = key_path
        self.description = description

    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'host': self.host,
            'user': self.user,
            'port': self.port,
            'key_path': self.key_path,
            'description': self.description
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'SSHServer':
        return cls(**data)

class SSHManager:
    """Gère la configuration et la connexion aux serveurs SSH"""
    
    def __init__(self):
        self.config_dir = Path.home() / '.config' / 'easyssh'
        self.config_file = self.config_dir / 'servers.json'
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.servers = self._load_servers()

    def _load_servers(self) -> List[SSHServer]:
        """Charge les serveurs depuis le fichier de configuration"""
        if not self.config_file.exists():
            return []
        
        try:
            with open(self.config_file, 'r') as f:
                data = json.load(f)
                return [SSHServer.from_dict(server) for server in data]
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def save_servers(self):
        """Sauvegarde les serveurs dans le fichier de configuration"""
        with open(self.config_file, 'w') as f:
            json.dump([server.to_dict() for server in self.servers], f, indent=2)

    def add_server(self, server: SSHServer):
        """Ajoute un nouveau serveur"""
        self.servers.append(server)
        self.save_servers()

    def remove_server(self, name: str) -> bool:
        """Supprime un serveur par nom"""
        for i, server in enumerate(self.servers):
            if server.name == name:
                del self.servers[i]
                self.save_servers()
                return True
        return False

    def get_server(self, name: str) -> Optional[SSHServer]:
        """Récupère un serveur par nom"""
        for server in self.servers:
            if server.name == name:
                return server
        return None

    def search_servers(self, query: str) -> List[SSHServer]:
        """Recherche des serveurs par nom, host ou description"""
        query = query.lower()
        return [
            server for server in self.servers
            if query in server.name.lower() or 
               query in server.host.lower() or 
               query in server.description.lower()
        ]

    def connect_to_server(self, server: SSHServer):
        """Se connecte à un serveur SSH"""
        cmd = ['ssh']
        
        if server.key_path:
            cmd.extend(['-i', server.key_path])
        
        if server.port != 22:
            cmd.extend(['-p', str(server.port)])
        
        cmd.append(f'{server.user}@{server.host}')
        
        try:
            subprocess.run(cmd)
        except KeyboardInterrupt:
            console.print("\n[yellow]Connexion interrompue[/yellow]")
        except Exception as e:
            console.print(f"[red]Erreur lors de la connexion: {e}[/red]")

class EasySSHApp(App):
    """Application Textual pour l'interface utilisateur"""
    
    CSS = """
    Screen {
        background: black;
    }
    
    .title {
        color: orange;
        text-align: center;
        margin: 1 0;
        height: auto;
    }
    
    .search-container {
        margin: 1 2;
        height: auto;
    }
    
    Input {
        margin: 0;
        border: solid orange;
    }
    
    .suggestions {
        margin: 0 0 1 0;
        height: auto;
        max-height: 6;
        background: #222222;
        border: solid #666666;
    }
    
    .suggestion-item {
        color: #cccccc;
        background: #222222;
        padding: 0 1;
    }
    
    .suggestion-item-selected {
        color: white;
        background: orange;
        padding: 0 1;
    }
    
    .suggestion-hidden {
        display: none;
    }
    
    DataTable {
        margin: 1 2;
        height: 1fr;
    }
    
    .help {
        color: #888888;
        text-align: center;
        margin: 1 0;
        height: 1;
        dock: bottom;
        background: #111111;
    }
    
    .content-container {
        height: 1fr;
        layout: vertical;
    }
    """

    BINDINGS = [
        Binding("ctrl+c", "quit", "Quitter"),
        Binding("ctrl+a", "add_server", "Ajouter"),
        Binding("ctrl+d", "delete_server", "Supprimer"),
        Binding("enter", "connect", "Se connecter"),
        Binding("escape", "clear_search", "Effacer recherche"),
        Binding("tab", "autocomplete", "Autocompléter"),
    ]

    def __init__(self):
        super().__init__()
        self.ssh_manager = SSHManager()
        self.filtered_servers = self.ssh_manager.servers.copy()
        self.suggestions = []
        self.selected_suggestion = 0
        self.show_suggestions = False

    def compose(self) -> ComposeResult:
        # ASCII Art pour "Easy SSH"
        ascii_art = pyfiglet.figlet_format("Easy SSH", font="slant")
        
        yield Header()
        yield Static(ascii_art, classes="title")
        yield Container(
            Container(
                Input(placeholder="Rechercher un serveur...", id="search"),
                Container(id="suggestions_container", classes="suggestion-hidden"),
                classes="search-container"
            ),
            DataTable(id="servers_table"),
            classes="content-container"
        )
        yield Static("Enter: Se connecter | Tab: Autocompléter | Ctrl+A: Ajouter | Ctrl+D: Supprimer | Ctrl+C: Quitter", classes="help")
        yield Footer()

    def on_mount(self):
        """Initialise l'application"""
        self.setup_table()
        self.populate_table()

    def setup_table(self):
        """Configure la table des serveurs"""
        table = self.query_one("#servers_table", DataTable)
        table.add_columns("Nom", "Utilisateur", "Hôte", "Port", "Description")

    def populate_table(self):
        """Remplit la table avec les serveurs"""
        table = self.query_one("#servers_table", DataTable)
        table.clear()
        
        for server in self.filtered_servers:
            table.add_row(
                server.name,
                server.user,
                server.host,
                str(server.port),
                server.description[:30] + "..." if len(server.description) > 30 else server.description
            )

    def update_suggestions(self, query: str):
        """Met à jour les suggestions basées sur la recherche"""
        if not query:
            self.hide_suggestions()
            return
        
        # Trouver les serveurs correspondants
        matching_servers = self.ssh_manager.search_servers(query)
        self.suggestions = [server.name for server in matching_servers[:5]]  # Limiter à 5 suggestions
        
        if self.suggestions:
            self.show_suggestions_list()
        else:
            self.hide_suggestions()

    def show_suggestions_list(self):
        """Affiche la liste des suggestions"""
        self.show_suggestions = True
        self.selected_suggestion = 0
        
        suggestions_container = self.query_one("#suggestions_container")
        suggestions_container.remove_class("suggestion-hidden")
        suggestions_container.add_class("suggestions")
        
        # Vider le conteneur existant
        suggestions_container.remove_children()
        
        # Ajouter les suggestions
        for i, suggestion in enumerate(self.suggestions):
            if i == self.selected_suggestion:
                suggestions_container.mount(Static(f"▶ {suggestion}", classes="suggestion-item-selected"))
            else:
                suggestions_container.mount(Static(f"  {suggestion}", classes="suggestion-item"))

    def hide_suggestions(self):
        """Cache la liste des suggestions"""
        self.show_suggestions = False
        suggestions_container = self.query_one("#suggestions_container")
        suggestions_container.add_class("suggestion-hidden")
        suggestions_container.remove_class("suggestions")
        suggestions_container.remove_children()

    def navigate_suggestions(self, direction: int):
        """Navigue dans les suggestions (direction: -1 pour haut, 1 pour bas)"""
        if not self.show_suggestions or not self.suggestions:
            return
        
        self.selected_suggestion = (self.selected_suggestion + direction) % len(self.suggestions)
        self.show_suggestions_list()

    def autocomplete_current_suggestion(self):
        """Autocomplète avec la suggestion sélectionnée"""
        if self.show_suggestions and self.suggestions:
            search_input = self.query_one("#search", Input)
            search_input.value = self.suggestions[self.selected_suggestion]
            self.hide_suggestions()
            
            # Mettre à jour les résultats
            self.filtered_servers = [self.ssh_manager.get_server(self.suggestions[self.selected_suggestion])]
            if self.filtered_servers[0]:  # Vérifier que le serveur existe
                self.filtered_servers = [self.filtered_servers[0]]
            else:
                self.filtered_servers = []
            self.populate_table()

    def on_input_changed(self, event: Input.Changed):
        """Gère les changements dans la barre de recherche"""
        if event.input.id == "search":
            query = event.value
            
            # Mettre à jour les suggestions
            self.update_suggestions(query)
            
            # Mettre à jour les résultats de recherche
            if query:
                self.filtered_servers = self.ssh_manager.search_servers(query)
            else:
                self.filtered_servers = self.ssh_manager.servers.copy()
            self.populate_table()

    def on_key(self, event):
        """Gère les événements clavier globaux"""
        search_input = self.query_one("#search", Input)
        
        # Si on est dans la barre de recherche et qu'il y a des suggestions
        if search_input.has_focus and self.show_suggestions:
            if event.key == "down":
                event.prevent_default()
                self.navigate_suggestions(1)
                return
            elif event.key == "up":
                event.prevent_default()
                self.navigate_suggestions(-1)
                return
            elif event.key == "tab":
                event.prevent_default()
                self.autocomplete_current_suggestion()
                return
            elif event.key == "enter":
                event.prevent_default()
                # Si on a des suggestions, utiliser la suggestion sélectionnée
                if self.suggestions:
                    self.autocomplete_current_suggestion()
                    # Puis se connecter au serveur
                    if self.filtered_servers:
                        server = self.filtered_servers[0]
                        self.exit()
                        self.ssh_manager.connect_to_server(server)
                return
        
        # Gérer Ctrl+A pour ajouter un serveur
        if event.key == "ctrl+a":
            event.prevent_default()
            self.action_add_server()
        
        # Gérer Ctrl+D pour supprimer un serveur
        elif event.key == "ctrl+d":
            event.prevent_default()
            self.action_delete_server()
        
        # Gérer Ctrl+C pour quitter
        elif event.key == "ctrl+c":
            event.prevent_default()
            self.action_quit()
        
        # Gérer Escape pour effacer la recherche
        elif event.key == "escape":
            event.prevent_default()
            self.action_clear_search()
        
        # Gérer Tab pour autocomplétion
        elif event.key == "tab":
            event.prevent_default()
            self.action_autocomplete()
        
        # Gérer Enter pour se connecter
        elif event.key == "enter":
            # Vérifier si le focus n'est pas sur l'input de recherche
            if not search_input.has_focus:
                event.prevent_default()
                self.action_connect()

    def action_connect(self):
        """Se connecte au serveur sélectionné"""
        table = self.query_one("#servers_table", DataTable)
        if table.cursor_row is not None and self.filtered_servers:
            server = self.filtered_servers[table.cursor_row]
            self.exit()
            self.ssh_manager.connect_to_server(server)

    def action_add_server(self):
        """Ajoute un nouveau serveur"""
        self.exit()
        add_server_interactive(self.ssh_manager)

    def action_delete_server(self):
        """Supprime le serveur sélectionné"""
        table = self.query_one("#servers_table", DataTable)
        if table.cursor_row is not None and self.filtered_servers:
            server = self.filtered_servers[table.cursor_row]
            if console.input(f"Supprimer le serveur '{server.name}' ? (y/N): ").lower() == 'y':
                self.ssh_manager.remove_server(server.name)
                self.filtered_servers = self.ssh_manager.servers.copy()
                self.populate_table()

    def action_autocomplete(self):
        """Action d'autocomplétion"""
        search_input = self.query_one("#search", Input)
        if search_input.has_focus and self.show_suggestions:
            self.autocomplete_current_suggestion()

    def action_clear_search(self):
        """Efface la recherche"""
        search_input = self.query_one("#search", Input)
        search_input.value = ""
        self.hide_suggestions()
        self.filtered_servers = self.ssh_manager.servers.copy()
        self.populate_table()

    def action_quit(self):
        """Quitte l'application"""
        self.exit()

def add_server_interactive(ssh_manager: SSHManager):
    """Interface interactive pour ajouter un serveur"""
    console.print("\n[bold orange]Ajouter un nouveau serveur SSH[/bold orange]")
    
    name = Prompt.ask("Nom du serveur")
    host = Prompt.ask("Adresse IP ou nom d'hôte")
    user = Prompt.ask("Nom d'utilisateur")
    port = Prompt.ask("Port", default="22")
    key_path = Prompt.ask("Chemin vers la clé privée (optionnel)", default="")
    description = Prompt.ask("Description (optionnel)", default="")
    
    try:
        port = int(port)
    except ValueError:
        port = 22
    
    server = SSHServer(
        name=name,
        host=host,
        user=user,
        port=port,
        key_path=key_path if key_path else None,
        description=description
    )
    
    ssh_manager.add_server(server)
    console.print(f"[green]Serveur '{name}' ajouté avec succès ![/green]")

@click.group()
def cli():
    """EasySSH - Outil de gestion des connexions SSH"""
    pass

@cli.command()
def ui():
    """Lance l'interface utilisateur interactive"""
    app = EasySSHApp()
    app.run()

@cli.command()
@click.argument('server_name')
def connect(server_name):
    """Se connecte directement à un serveur par nom"""
    ssh_manager = SSHManager()
    server = ssh_manager.get_server(server_name)
    
    if not server:
        console.print(f"[red]Serveur '{server_name}' non trouvé[/red]")
        return
    
    ssh_manager.connect_to_server(server)

@cli.command()
def list():
    """Liste tous les serveurs configurés"""
    ssh_manager = SSHManager()
    
    if not ssh_manager.servers:
        console.print("[yellow]Aucun serveur configuré[/yellow]")
        return
    
    table = Table(title="Serveurs SSH configurés", title_style="bold orange")
    table.add_column("Nom", style="cyan")
    table.add_column("Utilisateur", style="green")
    table.add_column("Hôte", style="yellow")
    table.add_column("Port", style="magenta")
    table.add_column("Description", style="white")
    
    for server in ssh_manager.servers:
        table.add_row(
            server.name,
            server.user,
            server.host,
            str(server.port),
            server.description
        )
    
    console.print(table)

@cli.command()
def add():
    """Ajoute un nouveau serveur de manière interactive"""
    ssh_manager = SSHManager()
    add_server_interactive(ssh_manager)

@cli.command()
@click.argument('server_name')
def remove(server_name):
    """Supprime un serveur par nom"""
    ssh_manager = SSHManager()
    
    if ssh_manager.remove_server(server_name):
        console.print(f"[green]Serveur '{server_name}' supprimé[/green]")
    else:
        console.print(f"[red]Serveur '{server_name}' non trouvé[/red]")

if __name__ == '__main__':
    # Par défaut, lance l'interface utilisateur
    if len(sys.argv) == 1:
        ui()
    else:
        cli()