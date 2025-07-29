# EasySSH

Un outil CLI élégant pour gérer et se connecter facilement à vos serveurs SSH, avec une interface utilisateur similaire à Claude CLI.

## 🚀 Installation rapide

### Via pipx (recommandé)
```bash
# Installation depuis PyPI (une fois publié)
pipx install easyssh-cli

# Ou installation depuis GitHub
pipx install git+https://github.com/basile-parent/easyssh.git
```

### Via pip
```bash
# Depuis PyPI
pip install easyssh-cli

# Depuis GitHub
pip install git+https://github.com/basile-parent/easyssh.git
```

## ✨ Fonctionnalités

- 🎨 **Interface utilisateur élégante** avec ASCII art orange
- 🔍 **Autocomplétion intelligente** similaire à Google Search
- 💾 **Sauvegarde automatique** de la configuration des serveurs
- 🔑 **Support des clés SSH** privées et ports personnalisés
- ⌨️ **Raccourcis clavier** intuitifs
- 📋 **Gestion complète** des serveurs (ajouter, supprimer, lister)
- 🔄 **Suggestions en temps réel** avec navigation par flèches

## 🎯 Utilisation

### Interface utilisateur principale
```bash
easyssh
```

### Raccourcis clavier dans l'interface
- `Enter` : Se connecter au serveur sélectionné (ou autocompléter + connecter depuis la recherche)
- `Tab` : Autocompléter la suggestion sélectionnée
- `↑/↓` : Naviguer dans les suggestions
- `Ctrl+A` : Ajouter un nouveau serveur
- `Ctrl+D` : Supprimer le serveur sélectionné
- `Escape` : Effacer la recherche
- `Ctrl+C` : Quitter l'application

### Commandes CLI

```bash
# Lancer l'interface utilisateur
easyssh ui

# Se connecter directement à un serveur
easyssh connect nom_du_serveur

# Lister tous les serveurs
easyssh list

# Ajouter un serveur interactivement
easyssh add

# Supprimer un serveur
easyssh remove nom_du_serveur

# Aide
easyssh --help
```

## 📖 Guide de démarrage rapide

1. **Installation** : `pipx install easyssh-cli`
2. **Premier lancement** : `easyssh`
3. **Ajouter un serveur** : Appuyez sur `Ctrl+A` et remplissez les informations
4. **Recherche intelligente** : Tapez dans la barre de recherche, utilisez `↑/↓` et `Tab`
5. **Connexion** : Sélectionnez un serveur et appuyez sur `Enter`

## 🔧 Configuration

Les serveurs sont sauvegardés dans `~/.config/easyssh/servers.json`.

Exemple de configuration :
```json
[
  {
    "name": "serveur-prod",
    "host": "192.168.1.100",
    "user": "admin",
    "port": 22,
    "key_path": "/home/user/.ssh/id_rsa",
    "description": "Serveur de production principal"
  }
]
```

## 🛠️ Développement

### Prérequis
- Python 3.7+
- pipx (recommandé) ou pip

### Installation en mode développement
```bash
git clone https://github.com/basile-parent/easyssh.git
cd easyssh
pipx install -e .
```

### Structure du projet
```
easyssh/
├── easyssh.py          # Code principal
├── setup.py            # Configuration d'installation
├── pyproject.toml      # Configuration moderne du package
├── README.md           # Documentation
├── LICENSE            # Licence MIT
├── requirements.txt    # Dépendances
├── MANIFEST.in        # Fichiers à inclure dans le package
├── .gitignore         # Fichiers à ignorer
└── .github/
    └── workflows/
        └── test.yml    # Tests automatisés
```

## 📦 Dépendances

- **rich** (≥13.0.0) : Interface utilisateur colorée et tables
- **textual** (≥0.41.0) : Framework d'interface terminal
- **pyfiglet** (≥0.8.0) : ASCII art pour le titre
- **colorama** (≥0.4.0) : Support des couleurs cross-platform
- **paramiko** (≥3.0.0) : Client SSH Python
- **click** (≥8.0.0) : Framework CLI

## 🤝 Contribution

Les contributions sont les bienvenues ! Pour contribuer :

1. Forkez le projet
2. Créez une branche pour votre fonctionnalité (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Committez vos changements (`git commit -am 'Ajout d'une nouvelle fonctionnalité'`)
4. Poussez vers la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Ouvrez une Pull Request

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 🐛 Signaler un problème

Si vous rencontrez un problème, veuillez ouvrir une [issue](https://github.com/basile-parent/easyssh/issues) avec :
- Votre système d'exploitation
- La version de Python
- Les étapes pour reproduire le problème
- Les messages d'erreur (si applicable)

## 🎉 Remerciements

- Inspiré par l'interface de Claude CLI
- Construit avec [Textual](https://github.com/Textualize/textual)
- ASCII art généré avec [pyfiglet](https://github.com/pwaller/pyfiglet)

---

**EasySSH** - Simplifiez vos connexions SSH ! 🚀