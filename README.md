# NLP Practical Labs

Travaux pratiques de traitement automatique du langage naturel (5e année, groupe G4), organisés par séance. **Le notebook exécuté constitue le compte rendu à remettre.** Les ressources de l'enseignant sont conservées dans `sources/`.

## TP disponibles

| TP | Sujet | Livrables |
|---|---|---|
| [TP3](TP3/) | Normalisation, mots vides, racinisation, lemmatisation et darija | [Notebook à remettre](TP3/TP3_EZZIRANI_Anwar_G4.ipynb) |

Le dossier local d'origine s'appelait `TP4`, mais les trois documents fournis indiquent **TP3**. Le dossier du dépôt suit le numéro de l'énoncé ; les prochains TP pourront être ajoutés à côté.

## Exécuter le notebook

Python 3.11 ou plus récent :

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m spacy download fr_core_news_sm
python -m spacy download en_core_web_sm
```

Ouvrir ensuite le notebook dans Jupyter ou VS Code, puis **redémarrer le noyau et exécuter toutes les cellules**. Le téléchargement NLTK des mots vides est géré par le notebook si la ressource manque.

La même exécution peut être enregistrée depuis PowerShell avec `python execute_tp3.py TP3/TP3_EZZIRANI_Anwar_G4.ipynb` une fois les deux modèles installés. Le script n'écrit le fichier que si toutes les cellules réussissent.

Le notebook peut être régénéré à partir de l'énoncé avec `python build_tp3.py --groupe G4`. Cette commande efface ses sorties : il faut ensuite l'exécuter à nouveau.

`publish.ps1` crée et pousse deux commits séparés (sources et outils, puis notebook exécuté) avec l'adresse GitHub publique de l'étudiant. Si GitHub a créé un premier commit lors de la création du dépôt, le script conserve cet historique.

## Vérification locale

Les 38 cellules de code ont été exécutées avec succès. Les 13 tests de l'énoncé affichent ✅. Environnement vérifié : spaCy 3.8.16, `fr_core_news_sm` 3.8.0, `en_core_web_sm` 3.8.0 et NLTK 3.9.4. Le notebook enregistré contient les sorties des cellules, les tableaux et le graphique.
