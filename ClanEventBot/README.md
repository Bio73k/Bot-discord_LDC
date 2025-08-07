# Discord Bot - Gestion d'Événements de Clan

## 📋 Description

Bot Discord complet pour la gestion d'événements de clan avec support multi-jeux. Conçu pour les communautés gaming françaises avec interface entièrement localisée.

## ✨ Fonctionnalités

### 🎮 Gestion d'Événements
- **Types d'événements** : Bingo, Tournois JcJ, Événements généraux
- **Création interactive** : Interface à 2 étapes avec sélection du type puis formulaire détaillé
- **Participation** : Boutons Discord intuitifs ("🎮 Participer", "🚪 Ne plus participer")
- **Threads automatiques** : Création automatique avec ping @Gardiens
- **Format français** : Dates DD/MM/YYYY HH:MM avec timezone française (UTC+2)

### ⏰ Système de Rappels
- **Notifications automatiques** : Rappels avant l'événement
- **Ping des participants** : Notification de tous les inscrits
- **Gestion timezone** : Conversion automatique UTC ↔ heure française

### 👥 Gestion d'Équipes
- **Randomisation** : Attribution aléatoire des équipes
- **Tailles configurables** : 1 à 6 joueurs par équipe
- **Validation** : Vérification des tailles d'équipe selon l'activité

### 📊 Système de Pointage
- **Check-in** : Système d'émargement pour les événements
- **Rapports** : Statistiques de présence détaillées
- **Contrôle** : Activation/désactivation par créateur ou admin

## 🚀 Installation

### Prérequis
- Python 3.11+
- Token Discord Bot
- Serveur Discord avec permissions appropriées

### Configuration
1. **Variables d'environnement** :
   ```
   DISCORD_BOT_TOKEN=votre_token_ici
   ```

2. **Permissions Discord** :
   - Lire/Envoyer des messages
   - Créer des threads
   - Utiliser les slash commands
   - Gérer les messages (pour les boutons)

### Lancement
```bash
python main.py
```

## 📱 Commandes

### Slash Commands
- `/create-event` : Création d'événement interactive
- `/activer-pointage [event_id]` : Activer le check-in
- `/desactiver-pointage [event_id]` : Désactiver le check-in
- `/pointer [event_id]` : Se signaler présent
- `/rapport-presence [event_id]` : Rapport de présence

### Commandes Texte
- `!clear-events` : Supprimer tous les événements
- `!list-events` : Lister tous les événements
- `!test-reminder` : Test du système de rappel
- `!create-teams [event_id]` : Créer les équipes

## 🏗️ Architecture

### Structure du Projet
```
├── bot/                    # Core Discord bot
│   ├── commands/          # Commandes organisées par catégorie
│   └── destiny_bot.py     # Bot principal
├── models/                # Modèles de données
├── services/              # Logique métier
├── utils/                 # Utilitaires et helpers
└── main.py               # Point d'entrée
```

### Modules Principaux
- **EventService** : Gestion complète des événements
- **ReminderService** : Système de notifications
- **TeamService** : Attribution des équipes
- **TimezoneUtils** : Gestion timezone française

## 🌐 Internationalisation

Interface entièrement en français :
- Commandes slash traduites
- Messages d'interface
- Format de dates français
- Timezone française (UTC+2)

## 🔧 Personnalisation

### Types d'Événements
Modifiez `utils/constants.py` pour ajouter de nouveaux types :
```python
EVENT_TYPE_INFO = {
    EventType.NOUVEAU_TYPE: {
        "description": "Description du nouveau type",
        "suggested_team_sizes": [2, 4],
        "max_participants": 50
    }
}
```

### Rôles et Permissions
Configurez le rôle @Gardiens dans votre serveur Discord pour les notifications automatiques.

## 📝 Utilisation

### Créer un Événement
1. Utilisez `/create-event`
2. Sélectionnez le type d'événement
3. Remplissez le formulaire (nom, date, heure, taille d'équipe)
4. L'événement est créé avec thread automatique

### Participation
- Cliquez sur "🎮 Participer" pour rejoindre
- Cliquez sur "🚪 Ne plus participer" pour quitter

### Gestion du Check-in
1. Activez avec `/activer-pointage`
2. Les participants utilisent `/pointer`
3. Consultez le rapport avec `/rapport-presence`

## 🛠️ Support Technique

Le bot utilise un système de stockage en mémoire (reset au redémarrage). Conçu pour une migration facile vers base de données persistante.

### Logs
Le système de logging détaillé facilite le débogage :
- Événements créés/supprimés
- Rappels envoyés
- Erreurs système

## 📄 Licence

Projet développé pour communautés gaming françaises.