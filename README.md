# Agentic Travel Planner

Système agentique de planification de voyage propulsé par **DeepAgents / LangGraph**, **FastAPI**, **Gemini**, et le **Model Context Protocol (MCP)**.

## Fonctionnalités Principales

*   **Orchestration Multi-Agents :** Utilisation de DeepAgents pour coordonner un flux de travail impliquant la recherche de destination, l'évaluation du budget et la vérification des conditions météorologiques.
*   **Graphes d'État Cycliques & Auto-Correction :** Implémentation d'un nœud d'évaluation (Critic Agent) capable de rejeter un itinéraire ne respectant pas les contraintes de l'utilisateur (budget, logistique) et de déclencher une boucle de révision.
*   **Intégration MCP (Model Context Protocol) :** Découplage complet des outils. Les agents exécutent des outils via un serveur MCP distant et standardisé (Recherche web, API Météo).
*   **Endpoints Asynchrones & Persistance :** API exposée via FastAPI avec une sauvegarde persistante de l'état des agents (Checkpointer LangGraph via SQLite).

## Architecture

Le projet est divisé en deux microservices conteneurisés :
1.  **Backend (`/backend`) :** Le "Cerveau". Exécute FastAPI, gère le StateGraph (LangGraph), et maintient la mémoire (SQLite).
2.  **MCP Server (`/mcp_server`) :** Les "Mains". Un serveur léger exposant les outils au standard MCP pour une exécution sécurisée.

## Stack Technique
*   **Langage :** Python 3.11
*   **Gestionnaire de paquets :** `uv`
*   **Framework LLM :** DeepAgents, LangGraph, LangChain (Google GenAI / Gemini)
*   **API / Serveur :** FastAPI, Uvicorn
*   **Infrastructure :** Docker, Docker Compose

## ⚙️ Installation & Démarrage (Local)

1. **Cloner le dépôt :**
   ```bash
   git clone [https://github.com/FlorianeJN/ai-travel-planner.git](https://github.com/FlorianeJN/ai-travel-planner.git)
   cd ai-travel-planner