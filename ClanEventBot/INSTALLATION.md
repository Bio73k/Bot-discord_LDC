# 🚀 Guide d'Installation - Discord Bot Clan

## Étapes Rapides

### 1. Prérequis
- Python 3.11 ou plus récent
- Un serveur Discord où vous êtes administrateur
- Un token de bot Discord

### 2. Créer le Bot Discord
1. Allez sur https://discord.com/developers/applications
2. Cliquez "New Application" → Donnez un nom
3. Onglet "Bot" → "Add Bot"
4. Copiez le **Token** (gardez-le secret!)
5. Activez ces **Intents**:
   - ✅ Presence Intent
   - ✅ Server Members Intent  
   - ✅ Message Content Intent

### 3. Inviter le Bot
1. Onglet "OAuth2" → "URL Generator"
2. Scopes: ✅ `bot` ✅ `applications.commands`
3. Permissions Bot:
   - ✅ Send Messages
   - ✅ Create Public Threads
   - ✅ Send Messages in Threads
   - ✅ Use Slash Commands
   - ✅ Manage Messages
   - ✅ Read Message History
4. Copiez l'URL générée et ouvrez-la pour inviter le bot

### 4. Configuration Serveur
1. **Rôle @Gardiens** : Créez ce rôle pour les notifications automatiques
2. **Permissions Canal** : Le bot doit pouvoir lire/écrire dans les canaux d'événements

### 5. Installation Code
```bash
# Extraire l'archive
tar -xzf discord_bot_code.tar.gz
cd discord_bot_project

# Configurer le token
export DISCORD_BOT_TOKEN="votre_token_ici"

# Lancer le bot
python main.py
```

### 6. Vérification
- Le bot apparaît en ligne sur Discord
- Les slash commands sont disponibles (`/create-event`)
- Test avec `!test-reminder` pour vérifier le fonctionnement

## 🔧 Configuration Avancée

### Variables d'Environnement
```bash
# Token obligatoire
DISCORD_BOT_TOKEN="votre_token_discord"

# Base de données (optionnel - par défaut en mémoire)
DATABASE_URL="postgresql://user:pass@localhost/dbname"
```

### Personnalisation
- **Rôle de notification** : Modifiez `1348280452305260554` dans le code
- **Timezone** : Configurée pour UTC+2 (France)
- **Types d'événements** : Modifiables dans `utils/constants.py`

## ❓ Dépannage

### Bot hors ligne
- Vérifiez le token dans les variables d'environnement
- Contrôlez les logs pour les erreurs de connexion

### Slash commands absentes
- Le bot a besoin des permissions `applications.commands`
- Réinvitez avec les bonnes permissions si nécessaire

### Rappels non envoyés  
- Vérifiez que le bot peut envoyer des messages dans les threads
- Les événements doivent avoir des participants inscrits

## 📞 Support
Consultez les logs en cas de problème - ils sont très détaillés pour faciliter le débogage.