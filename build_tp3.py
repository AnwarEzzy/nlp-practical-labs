"""Build the completed TP3 notebook from the teacher's original notebook."""

import json
import argparse
from pathlib import Path


ROOT = Path(__file__).parent
SOURCE = ROOT / "TP3" / "sources" / "TP3_Enonce.ipynb"
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--groupe", default="GROUPE", help="Groupe à inscrire dans le notebook et son nom")
args = parser.parse_args()
group = args.groupe.strip().replace(" ", "_")
if not group or any(c in group for c in '\\/:*?"<>|'):
    parser.error("Nom de groupe vide ou invalide pour un nom de fichier Windows")
OUTPUT = ROOT / "TP3" / f"TP3_EZZIRANI_Anwar_{group}.ipynb"

notebook = json.loads(SOURCE.read_text(encoding="utf-8"))


def put(index, source):
    notebook["cells"][index]["source"] = source.strip("\n").splitlines(keepends=True)
    if notebook["cells"][index]["source"]:
        notebook["cells"][index]["source"][-1] = notebook["cells"][index]["source"][-1].rstrip("\n")
    if notebook["cells"][index]["cell_type"] == "code":
        notebook["cells"][index]["execution_count"] = None
        notebook["cells"][index]["outputs"] = []


put(2, '''
NOM = "EZZIRANI"
PRENOM = "Anwar"
GROUPE = "GROUPE"  # Remplacer par le groupe réel avant le rendu.

assert NOM and PRENOM and GROUPE, "Complétez NOM, PRENOM et GROUPE"
nom_fichier = f"TP3_{NOM}_{PRENOM}_{GROUPE}.ipynb".replace(" ", "_")
print("Enregistrez votre notebook sous le nom :", nom_fichier)
'''.replace('GROUPE = "GROUPE"  # Remplacer par le groupe réel avant le rendu.', f'GROUPE = {group!r}'))

put(10, '''
sw_nltk = set(stopwords.words("french"))
sw_spacy = set(nlp_fr.Defaults.stop_words)

communs = sw_nltk & sw_spacy
seulement_nltk = sw_nltk - sw_spacy
seulement_spacy = sw_spacy - sw_nltk

print("NLTK :", len(sw_nltk), "| spaCy :", len(sw_spacy), "| communs :", len(communs))
print("Seulement NLTK (15 premiers) :", sorted(seulement_nltk)[:15])
print("Seulement spaCy (15 premiers) :", sorted(seulement_spacy)[:15])
''')

put(16, '''
mots = [t.lower_ for doc in docs for t in doc if t.is_alpha]
freq = Counter(mots)
top10 = freq.most_common(10)

nb_vides = sum(m in sw_spacy for m in mots)
proportion = nb_vides / len(mots)

print(len(mots), "tokens,", len(freq), "mots différents")
print(top10)
print(f"Mots vides : {nb_vides} tokens, soit {proportion:.0%} du corpus")
''')

put(19, '''
def retirer_mots_vides(tokens, mots_vides):
    """Retire la ponctuation et les mots vides, sans modifier les autres tokens."""
    return [t.lower_ for t in tokens if not t.is_punct and t.lower_ not in mots_vides]

for phrase in ["Le plat est bon.", "Le plat n'est pas bon.", "Le plat n'est jamais bon."]:
    doc = nlp_fr(phrase)
    print(f"{phrase:28}", retirer_mots_vides(doc, sw_spacy))
''')

put(24, '''
NEGATION = {"ne", "n'", "pas", "plus", "jamais", "rien", "aucun", "aucune", "sans", "ni"}
INTENSITE = {"très", "trop", "peu"}
MOTS_DOMAINE = {"plat", "restaurant"}

mots_vides_tp = (sw_spacy - NEGATION - INTENSITE) | MOTS_DOMAINE

print(len(mots_vides_tp), "mots vides dans la liste adaptée")
for phrase in ["Le plat est bon.", "Le plat n'est pas bon.", "Le restaurant est très sale."]:
    print(f"{phrase:30}", retirer_mots_vides(nlp_fr(phrase), mots_vides_tp))
''')

put(29, '''
stemmer_fr = SnowballStemmer("french")

def raciner(mots):
    return [stemmer_fr.stem(m) for m in mots]

def nb_racines(mots):
    return len(set(raciner(mots)))

familles = {
    "manger":  ["mange", "mangeons", "mangeait", "mangé", "mangeur"],
    "rapide":  ["rapide", "rapides", "rapidement", "rapidité"],
    "livrer":  ["livrer", "livraison", "livreur", "livré"],
    "servir":  ["servir", "service", "serveur", "serveuse", "servi"],
    "aller":   ["aller", "allons", "va", "irai"],
}
for nom, mots_famille in familles.items():
    print(f"{nom:8} {nb_racines(mots_famille)} racine(s) :", raciner(mots_famille))
''')

put(32, '''
def lemmatiser(texte):
    doc = nlp_fr(texte)
    return [t.lemma_.lower() for t in doc if not t.is_punct]

print(lemmatiser("Les serveurs étaient aimables et nous avons mangé des tajines délicieux."))
print(lemmatiser("Nous irons, tu vas, ils allaient."))
''')

put(35, '''
avis = "Les serveurs étaient souriants mais les livraisons arrivaient froides."
lignes = []
for t in nlp_fr(avis):
    if not t.is_punct:
        lignes.append({"mot": t.lower_, "racine": stemmer_fr.stem(t.lower_),
                       "lemme": t.lemma_.lower(), "catégorie": t.pos_})

tableau = pd.DataFrame(lignes)
tableau
''')

put(39, '''
porter = PorterStemmer()
snow_en = SnowballStemmer("english")

lignes_en = []
deja_vus = set()
for texte, _ in ENGLISH:
    for t in nlp_en(texte):
        mot = t.lower_
        if t.is_alpha and mot not in deja_vus:
            deja_vus.add(mot)
            lignes_en.append({"mot": mot, "Porter": porter.stem(mot),
                              "Snowball": snow_en.stem(mot),
                              "lemme spaCy": t.lemma_.lower()})

tableau_en = pd.DataFrame(lignes_en)
tableau_en[(tableau_en["Porter"] != tableau_en["mot"]) |
           (tableau_en["lemme spaCy"] != tableau_en["mot"])]
''')

put(43, '''
racine_vers_lemmes = {}
for doc in docs:
    for t in doc:
        if t.is_alpha and t.lower_ not in mots_vides_tp:
            r = stemmer_fr.stem(t.lower_)
            racine_vers_lemmes.setdefault(r, set()).add(t.lemma_.lower())

suspects = {r: lemmes for r, lemmes in racine_vers_lemmes.items() if len(lemmes) >= 2}
for r, lemmes in sorted(suspects.items()):
    print(f"{r:10} <- {sorted(lemmes)}")
''')

put(47, '''
def normaliser_arabe(t):
    t = re.sub("[\\u064B-\\u0652]", "", t)  # 1. voyelles brèves
    t = t.replace("\\u0640", "")           # 2. tatweel
    t = t.translate(str.maketrans({"\\u0623": "\\u0627", "\\u0625": "\\u0627", "\\u0622": "\\u0627"}))
    t = t.replace("\\u0649", "\\u064A")   # 4. alef maqsura -> ya
    t = t.replace("\\u0629", "\\u0647")   # 5. ta marbuta -> ha
    t = t.translate(str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789"))  # 6. chiffres
    return t

for mot in ["أحمد", "إلى", "مدرسة", "شُكْرًا", "المطعـــم", "٢٠٢٤"]:
    print("avant :", mot, "| après :", normaliser_arabe(mot))
''')

put(52, '''
def nb_tokens(listes):
    return sum(len(liste) for liste in listes)

def taille_vocabulaire(listes):
    return len({mot for liste in listes for mot in liste})

exemple = [["le", "plat", "est", "bon"], ["le", "plat", "est", "froid"]]
print(nb_tokens(exemple), taille_vocabulaire(exemple))
''')

put(55, '''
def garde(t):
    return not t.is_punct and not t.is_space and t.lower_ not in mots_vides_tp

etapes = {
    "0. tokens bruts":        [[t.text for t in d] for d in docs],
    "1. minuscules":          [[t.lower_ for t in d] for d in docs],
    "2. sans ponctuation":    [[t.lower_ for t in d if not t.is_punct and not t.is_space] for d in docs],
    "3. sans accents":        [[sans_accents(t.lower_) for t in d if not t.is_punct and not t.is_space] for d in docs],
    "4. sans mots vides":     [[sans_accents(t.lower_) for t in d if garde(t)] for d in docs],
    "5a. racines (Snowball)": [[stemmer_fr.stem(sans_accents(t.lower_)) for t in d if garde(t)] for d in docs],
    "5b. lemmes (spaCy)":     [[sans_accents(t.lemma_.lower()) for t in d if garde(t)] for d in docs],
}

v0 = taille_vocabulaire(etapes["0. tokens bruts"])
resultats = pd.DataFrame([
    {"étape": nom, "tokens": nb_tokens(l), "vocabulaire": taille_vocabulaire(l),
     "réduction du vocabulaire": f"{1 - taille_vocabulaire(l) / v0:.0%}"}
    for nom, l in etapes.items()])
resultats
''')

put(58, '''
plt.figure(figsize=(8, 3.5))
plt.barh(resultats["étape"], resultats["vocabulaire"], color="#2869a6")
plt.gca().invert_yaxis()
plt.xlabel("Taille du vocabulaire (formes distinctes)")
plt.title("Effet du prétraitement sur le vocabulaire français")
plt.tight_layout()
plt.show()
''')

put(60, '''
def normaliser_tp3(texte, methode="lemmes"):
    doc = nlp_fr(preprocess(texte))
    if methode == "lemmes":
        return [t.lemma_.lower() for t in doc if garde(t)]
    elif methode == "racines":
        return [stemmer_fr.stem(t.lower_) for t in doc if garde(t)]
    raise ValueError("methode doit être 'lemmes' ou 'racines'")

for texte, etiquette in AVIS[:3] + AVIS[-2:]:
    print(etiquette, normaliser_tp3(texte))
''')

put(65, '''
def corriger(mot, max_dist=2):
    mot = mot.lower()
    if mot in connus:
        return mot
    candidats = [(edit_distance(mot, connu), -frequence, connu)
                 for connu, frequence in connus.items()]
    if not candidats:
        return mot
    distance, _, meilleur = min(candidats)
    return meilleur if distance <= max_dist else mot

for m in ["restaurent", "magnifque", "servise", "tajine", "excellentes"]:
    print(f"{m:12} -> {corriger(m)}")
''')

put(68, '''
etape4_nltk = [[sans_accents(t.lower_) for t in d
               if not t.is_punct and not t.is_space and t.lower_ not in sw_nltk]
              for d in docs]
voc_nltk = {mot for liste in etape4_nltk for mot in liste}
print("Vocabulaire avec la liste NLTK :", len(voc_nltk), "| avec la liste adaptée :",
      taille_vocabulaire(etapes["4. sans mots vides"]))
print("n' gardé :", "n'" in voc_nltk, "| pas gardé :", "pas" in voc_nltk)
''')

put(71, '''
docs_en = list(nlp_en.pipe([t for t, _ in ENGLISH]))
sw_en = nlp_en.Defaults.stop_words - {"not", "no", "n't", "never", "very"}

def garde_en(t):
    return not t.is_punct and not t.is_space and t.lower_ not in sw_en

etapes_en = {
    "0. tokens bruts":        [[t.text for t in d] for d in docs_en],
    "1. minuscules":          [[t.lower_ for t in d] for d in docs_en],
    "2. sans ponctuation":    [[t.lower_ for t in d if not t.is_punct and not t.is_space] for d in docs_en],
    "3. sans accents":        [[sans_accents(t.lower_) for t in d if not t.is_punct and not t.is_space] for d in docs_en],
    "4. sans mots vides":     [[sans_accents(t.lower_) for t in d if garde_en(t)] for d in docs_en],
    "5a. racines (Porter)":   [[porter.stem(sans_accents(t.lower_)) for t in d if garde_en(t)] for d in docs_en],
    "5b. lemmes (spaCy)":     [[sans_accents(t.lemma_.lower()) for t in d if garde_en(t)] for d in docs_en],
}
v0_en = taille_vocabulaire(etapes_en["0. tokens bruts"])
resultats_en = pd.DataFrame([
    {"étape": nom, "tokens": nb_tokens(l), "vocabulaire": taille_vocabulaire(l),
     "réduction du vocabulaire": f"{1 - taille_vocabulaire(l) / v0_en:.0%}"}
    for nom, l in etapes_en.items()])
resultats_en
''')

put(14, '''
✍️ **Réponse 1.1.** spaCy contient 507 mots vides, contre 157 pour NLTK (85 sont communs).
NLTK contient `n` mais pas `n'` : son inventaire ne correspond pas au découpage de spaCy, qui produit `n'`.
Parmi les formes de négation proposées, `ne` et `pas` figurent dans les deux listes ; `n'` et `plus` ne sont que dans spaCy.
''')

put(21, '''
✍️ **Réponse 1.3.** Avec la liste spaCy brute, « Le plat est bon » et « Le plat n'est pas bon » deviennent tous deux `['plat', 'bon']`.
Un classifieur de sentiment perd alors le signal qui inverse la polarité de la seconde phrase.
« jamais » reste car il n'appartient pas à la liste française de mots vides de spaCy utilisée ici.
''')

put(26, '''
✍️ **Réponse 1.4.** J'ajoute `plat` (présent dans 3 avis) et `restaurant` (2 avis), deux termes qui décrivent le domaine plutôt que la polarité.
Le choix se fonde sur la fréquence documentaire `df` : ces mots reviennent dans plusieurs avis, positifs et négatifs ; `plats` reste distinct de `plat` à ce stade.
`service` (4 avis) peut porter une information d'aspect (« service lent/rapide ») et `bon` (6 avis) porte directement la polarité ; je les conserve.
La faible taille du corpus rend ce choix de mots du domaine expérimental.
''')

put(27, '''
### 2.1 À la main d'abord
Prédictions faites avant l'exécution, puis comparées à Snowball :

| Mot | Prédiction | Snowball |
|---|---|---|
| mangeons | mang | mangeon |
| rapidement | rapid | rapid |
| livraison | livr | livraison |
| livreur | livr | livreur |
| serveuse | serveus | serveux |

Les écarts montrent qu'un raciniseur ne réduit pas systématiquement tous les membres d'une famille à la même forme.
''')

put(37, '''
✍️ **Réponse 2.3.** `souriants` donne une racine tronquée (`souri`) qui n'est pas un mot français autonome, alors que le lemme `souriant` reste lisible.
Le lemme `être` pour `étaient` est aussi plus utile que sa racine : il regroupe les formes fléchies d'un verbe sous sa forme de dictionnaire.
La racinisation est simple, rapide et ne dépend pas d'un modèle grammatical ; elle peut cependant confondre ou séparer à tort des formes.
''')

put(41, '''
✍️ **Réponse 2.4.** `were` est ramené à `be` par le modèle spaCy, alors que Porter garde `were`.
Porter transforme `generously` en `gener`, forme peu lisible.
Pour `friendly`, Porter produit `friendli` et Snowball `friend` : les deux règles de suffixe ne donnent pas la même racine.
''')

put(45, '''
✍️ **Réponse 2.5.** `sal` regroupe `sale` et `salé`, deux adjectifs de sens distinct : c'est une vraie sur-racinisation, dangereuse pour le sentiment.
`command` regroupe `commande` (nom) et `commander` (verbe) : les lemmes diffèrent, mais ils appartiennent à la même famille sémantique ; ce n'est pas une collision de sens manifeste.
`froid` associe `froid` à `froider` : le modèle spaCy a interprété `froides` comme un verbe ; c'est une erreur de lemmatisation dans ce contexte.
Une racine associée à plusieurs lemmes n'est donc qu'un signal à examiner manuellement, pas une preuve de sur-racinisation.
''')

put(62, '''
### ✍️ Conclusion (livrable)

1. Sur 26 avis français, on passe de 279 tokens et 142 formes distinctes à 139 tokens et 87 lemmes distincts.
2. Le retrait des mots vides adaptés réduit le plus le vocabulaire d'une étape à la suivante : 124 → 92 formes (−32).
3. Le plus gros retrait de tokens vient aussi de cette étape : 230 → 139 (−91) ; la ponctuation en enlève 49.
4. Snowball donne 86 racines distinctes contre 87 lemmes : les racines réduisent ici légèrement plus le vocabulaire.
5. Cette différence vient des suffixes coupés sans analyse grammaticale ; `sale` et `salé` fusionnent sous `sal`.
6. Les minuscules effacent la casse (`TRÈS`), et la suppression des accents rapproche des graphies comme `très` et `tres`.
7. La ponctuation et les mots vides effacent des indices de forme et de syntaxe ; les mots du domaine `plat` et `restaurant` disparaissent.
8. Pour le sentiment, je choisis `preprocess` → spaCy → mots vides adaptés → lemmes, en gardant `n'`, `pas`, `très` et `trop`.
9. Ainsi « Le plat est bon » donne `['bon']`, tandis que « Le plat n'est pas bon » donne `["n'", 'pas', 'bon']`.
''')

put(66, '''
✍️ **Réponse A.** `magnifque` n'est pas corrigé, car `magnifique` n'apparaît qu'une fois dans ce corpus et ne figure donc pas dans `connus` (seuil : deux occurrences).
Un lexique français externe, un corpus plus grand ou un modèle de correction contextuelle permettrait de proposer `magnifique`.
La distance d'édition seule peut produire des corrections plausibles en forme mais fausses en contexte.
''')

put(69, '''
✍️ **Réponse B.** Avec NLTK, le vocabulaire de l'étape 4 contient 98 formes, contre 92 avec la liste adaptée.
`n'` est gardé parce que NLTK ne contient que `n`, forme qui ne correspond pas au token spaCy ; `pas` est supprimé parce qu'il figure dans NLTK.
Cette combinaison est incohérente pour le sentiment : les deux parties de la négation ne sont pas traitées ensemble.
''')

put(72, '''
✍️ **Réponse C.** Sur 6 avis anglais, le vocabulaire passe de 43 formes brutes à 31 après retrait des mots vides, soit une baisse de 28 % ; le nombre de tokens passe de 61 à 31.
Porter et spaCy laissent tous deux 31 formes distinctes dans ce petit corpus : les formes retenues ne contiennent pas ici de doublons morphologiques supplémentaires à fusionner.
En français, la chaîne comparable passe de 142 formes brutes à 86 racines ou 87 lemmes (environ 39 % de réduction).
Les réductions ne sont donc pas du même ordre : le corpus anglais est beaucoup plus petit et ses mots vides, flexions et fréquences diffèrent du corpus français.
''')

setup = "".join(notebook["cells"][4]["source"])
setup = setup.replace(
    'nltk.download("stopwords", quiet=True)',
    'try:\n    nltk.data.find("corpora/stopwords")\nexcept LookupError:\n    nltk.download("stopwords", quiet=True)',
)
put(4, setup)

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text(json.dumps(notebook, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print(OUTPUT)
