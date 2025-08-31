# 📱 Guide d'Utilisation pour Smartphone

Ce guide vous explique comment utiliser et gérer votre système de prédiction de matchs de football directement depuis votre smartphone, sans avoir besoin d'un ordinateur.

## 1. Accéder à l'Interface Web

L'interface web est le moyen le plus simple de consulter les prédictions quotidiennes. Elle est accessible depuis n'importe quel navigateur mobile.

**URL de l'interface :** [https://main--football-elo-predictor.manus.space](https://main--football-elo-predictor.manus.space)

**Comment l'utiliser :**
1.  Ouvrez le lien ci-dessus dans le navigateur de votre smartphone (Chrome, Safari, etc.).
2.  L'interface affichera automatiquement les matchs du jour avec leurs prédictions ELO et les probabilités de paris.
3.  Vous pouvez faire défiler la liste pour voir tous les matchs disponibles.
4.  L'interface est responsive et s'adaptera à la taille de votre écran.

## 2. Comprendre le Fonctionnement Automatique

Le système est conçu pour fonctionner de manière autonome grâce aux **GitHub Actions**. Vous n'avez aucune commande à exécuter manuellement.

- **Mise à jour des prédictions :** Tous les matins à **6h00 UTC**, un processus automatique récupère les matchs du jour, calcule les prédictions et met à jour l'interface.
- **Mise à jour des ELO :** Tous les soirs à **22h00 UTC**, un autre processus récupère les résultats des matchs terminés et met à jour les classements ELO des équipes.

## 3. Gérer le Projet depuis GitHub

Votre dépôt GitHub est le centre de contrôle de votre projet. Vous pouvez y gérer le code, suivre les mises à jour automatiques et même apporter des modifications si nécessaire.

**URL du dépôt GitHub :** [https://github.com/Matttgic/football-elo-predictor](https://github.com/Matttgic/football-elo-predictor)

### Suivre les Mises à Jour Automatiques

Vous pouvez vérifier que les mises à jour quotidiennes se déroulent correctement en consultant l'onglet **Actions** de votre dépôt GitHub.

1.  Ouvrez l'URL de votre dépôt GitHub sur votre smartphone.
2.  Allez dans l'onglet **Actions**.
3.  Vous verrez la liste des workflows qui se sont exécutés. Une icône verte (✅) indique que la mise à jour s'est bien déroulée.

### Déclencher une Mise à Jour Manuellement

Si vous souhaitez forcer une mise à jour des prédictions sans attendre le lendemain, vous pouvez le faire depuis l'interface GitHub.

1.  Allez dans l'onglet **Actions** de votre dépôt.
2.  Dans le menu de gauche, cliquez sur le workflow **Daily ELO and Prediction Update**.
3.  Cliquez sur le bouton **Run workflow** (Exécuter le workflow) à droite.
4.  Cela déclenchera immédiatement le processus de mise à jour.

## 4. Personnalisation (Avancé)

Si vous souhaitez modifier le code ou l'apparence de votre application, vous pouvez le faire directement depuis l'interface de GitHub.

1.  Ouvrez l'URL de votre dépôt GitHub.
2.  Naviguez jusqu'au fichier que vous souhaitez modifier (par exemple, `frontend/src/App.jsx` pour l'interface).
3.  Cliquez sur l'icône en forme de crayon (✏️) pour modifier le fichier.
4.  Une fois vos modifications terminées, enregistrez-les (commit). Cela déclenchera automatiquement un redéploiement de votre application avec les nouvelles modifications.

## 5. En Cas de Problème

Si l'interface n'affiche pas les matchs ou si vous rencontrez un problème, voici quelques points à vérifier :

- **Statut des GitHub Actions :** Vérifiez dans l'onglet **Actions** de votre dépôt si les derniers workflows se sont bien exécutés.
- **Secrets GitHub :** Assurez-vous que les secrets `RAPIDAPI_KEY` et `API_BASE_URL` sont correctement configurés dans les paramètres de votre dépôt.
- **Statut de l'API Backend :** Vous pouvez vérifier l'état de votre API backend en accédant à son URL de santé : [https://60h5imcle9pq.manus.space/api/health](https://60h5imcle9pq.manus.space/api/health)

Ce guide devrait vous permettre de profiter pleinement de votre système de prédiction de football directement depuis votre smartphone. N'hésitez pas si vous avez d'autres questions !

