# MCD2 Item Forge

Éditeur de sauvegarde **externe** pour **Minecraft Dungeons II** sur PC (version Game Pass / Xbox app).
Charge ton personnage hors ligne, choisis des objets (armes, armures, artéfacts), leur rareté, leur
puissance et leurs enchantements, puis enregistre : le jeu les trouvera dans ton inventaire au
prochain lancement.

![Aperçu de l'application](docs/apercu.png)

> **Version 0.2.** L'ancien mode « injection mémoire » a été retiré : le jeu se fermait peu après
> chaque connexion d'un outil externe à sa mémoire. L'application ne touche plus du tout au jeu en
> cours d'exécution : elle modifie seulement le fichier de sauvegarde, **jeu fermé**. L'ancienne
> version reste disponible dans `archive/`.

## Sommaire

- [Ce que fait l'application](#ce-que-fait-lapplication-et-ce-quelle-ne-fait-pas)
- [Les règles à respecter](#les-règles-à-respecter)
- [Arborescence](#arborescence)
- [Installation et lancement](#installation-et-lancement)
- [Utilisation](#utilisation)
- [Profil : niveau, émeraudes, livres enchantés](#profil--niveau-émeraudes-livres-enchantés)
- [Icônes des objets](#icônes-des-objets)
- [Tester sans risque](#tester-sans-risque)
- [Tags vérifiés, tags supposés et enchantements](#tags-vérifiés-tags-supposés-et-enchantements)
- [Comment l'enregistrement fonctionne](#comment-lenregistrement-fonctionne)
- [Restaurer une sauvegarde](#restaurer-une-sauvegarde)
- [Dépannage](#dépannage)
- [Tests automatisés](#tests-automatisés)
- [Limites connues](#limites-connues)

## Ce que fait l'application (et ce qu'elle ne fait pas)

- **Elle lit tes sauvegardes locales** dans
  `%LOCALAPPDATA%\Packages\Microsoft.MinecraftDungeons2_8wekyb3d8bbwe\SystemAppData\wgs`. Chaque
  personnage hors ligne y est un fichier JSON lisible (format `FCharacterSaveV1`).
- **Elle ajoute des objets** à l'inventaire du personnage, ou en fait des copies exactes. Elle ne
  modifie ni ne supprime jamais les objets existants.
- **Elle modifie le profil** : niveau, expérience, émeraudes, points d'enchantement et autres
  attributs déjà présents dans la sauvegarde.
- **Elle enregistre comme le fait le jeu**, avec une nouvelle version du conteneur de sauvegarde Xbox.
  Elle fait d'abord une copie de sécurité, puis relit tout pour vérifier.
- **Elle ne touche pas au jeu** : aucun fichier du jeu, aucune mémoire, aucune injection.
- **Elle refuse les personnages en ligne.** Leurs données font foi sur les serveurs du jeu. Seuls les
  personnages hors ligne, stockés sur ton PC, sont modifiables.
- **Elle remplit les tags toute seule** à partir de tags réellement vus en jeu, et n'invente pas de
  format : les enchantements proposés sont ceux déjà vus dans tes sauvegardes.

## Les règles à respecter

1. **Jeu fermé.** L'application refuse d'enregistrer tant que `Dungeons-WinGDK-Shipping.exe` ou son
   lanceur `Dungeons.exe` tourne. Sinon, le jeu écraserait ta modification.
2. **Synchronisation cloud Xbox.** Pour qu'elle garde ta version :
   1. ferme le jeu et l'application Xbox ;
   2. coupe Internet ;
   3. enregistre dans MCD2 Item Forge ;
   4. lance le jeu hors connexion et charge le personnage, puis quitte ;
   5. reconnecte-toi. Si l'Xbox app signale un conflit, choisis la copie de cet appareil.
3. **Un tag supposé à la fois.** Un tag que le jeu ne connaît pas peut empêcher le personnage de se
   charger. Teste-les un par un ; la copie de sécurité permet de revenir en arrière.
4. **Garde tes copies de sécurité.** Chaque enregistrement copie tout le dossier `wgs` dans
   `userdata\backups`.

## Arborescence

```
Mod menu Dungeon 2/
├── main.py                    Point d'entrée
├── lancer.bat                 Lancement par double-clic (sans console)
├── installer.bat              Crée .venv et installe les dépendances
├── creer_raccourci.bat        Crée le raccourci bureau avec l'icône de l'app
├── tools/creer_raccourci.py   Script appelé par creer_raccourci.bat
├── requirements.txt           Dépendances d'exécution (PySide6, psutil, pydantic)
├── requirements-dev.txt       Dépendances + pytest
├── pyproject.toml             Configuration de pytest
├── README.md
├── app/
│   ├── __init__.py            Nom et version
│   ├── paths.py               Emplacements des fichiers (mode portable)
│   ├── logging_setup.py       Journal : fichier tournant + console
│   ├── core/                  Logique, indépendante de l'interface
│   │   ├── wgs.py             Format de sauvegarde Xbox : lecture, nouvelle génération, retour arrière
│   │   ├── character_save.py  JSON du personnage : lecture, ajout d'objets
│   │   ├── editor.py          Session d'édition : ouvrir, ajouter, enregistrer avec vérifications
│   │   ├── knowledge.py       Registre des tags et enchantements vus dans les sauvegardes
│   │   ├── attributes.py      Attributs du profil : libellés, groupes, bornes
│   │   ├── catalog.py         Items, raretés, noms d'enchantements, recherche
│   │   ├── request.py         Demande d'ajout et ses règles
│   │   ├── game_process.py    Détection du jeu (l'enregistrement est bloqué s'il tourne)
│   │   ├── backup.py          Copie de sécurité du dossier wgs
│   │   ├── fsutil.py          Chemins longs Windows (au-delà de 260 caractères)
│   │   ├── settings.py        Réglages de l'utilisateur
│   │   ├── jsonio.py          Lecture/écriture JSON avec erreurs lisibles
│   │   └── errors.py          Erreurs prévues, messages en français
│   └── ui/                    Interface PySide6 (Qt 6)
│       ├── main_window.py     Fenêtre principale et orchestration
│       ├── item_panel.py      Liste des items, recherche, filtres
│       ├── enchant_panel.py   Enchantements observés et niveaux
│       ├── summary_panel.py   Résumé, tag du jeu, options, vérifications, boutons
│       ├── inventory_panel.py Onglet « Inventaire du personnage » (dont « Dupliquer… »)
│       ├── profile_panel.py   Onglet « Profil du personnage »
│       ├── log_panel.py       Onglet « Journal »
│       ├── dialogs.py         Confirmation d'enregistrement, Réglages
│       ├── tutorial.py        Tutoriel du premier lancement (Aide › Revoir le tutoriel)
│       ├── workers.py         Surveillance du jeu en arrière-plan
│       ├── widgets.py         Composants (pastille d'état, listes)
│       ├── icons.py           Icônes : images de data/icons/, vignettes à initiales
│       └── theme.py           Thème sombre, icône et export .ico
├── data/
│   ├── items.json             160 items : tags vérifiés, supposés ou absents
│   ├── enchantments.json      Noms français des enchantements (base MCD1)
│   ├── app.ico                Icône du raccourci (créée par creer_raccourci.bat)
│   └── icons/                 Tes images d'objets (voir « Icônes des objets »)
├── docs/apercu.png            Capture d'écran
├── archive/                   Ancienne version 0.1 (mode mémoire), en .zip
├── tests/                     66 tests automatisés (pytest)
└── userdata/                  Créé au lancement : settings.json, knowledge.json, logs/, backups/
```

## Installation et lancement

Prérequis : Windows 10 ou 11, 64 bits, et Python 3.12 64 bits. Sur ton PC, tout est déjà installé
dans `.venv`.

- Installation : double-clic sur **`installer.bat`**, ou
  `python -m venv .venv` puis `.venv\Scripts\python.exe -m pip install -r requirements.txt`.
- Lancement : double-clic sur **`lancer.bat`**, ou `.venv\Scripts\python.exe main.py`.
- **Raccourci bureau** : double-clic sur **`creer_raccourci.bat`**. Il écrit l'icône de l'application
  dans `datapp.ico` et crée « MCD2 Item Forge » sur le bureau (lancement sans console). Ajoute
  `--menu-demarrer` pour l'ajouter aussi au menu Démarrer :
  `.venv\Scripts\python.exe tools\creer_raccourci.py --menu-demarrer`. Relance-le si tu déplaces le
  dossier du projet : l'ancien raccourci est remplacé.

Au **premier lancement**, un tutoriel en six étapes explique le fonctionnement, notamment le fait que
tout se passe hors ligne. Tu peux le revoir avec **Aide › Revoir le tutoriel** (`F1`).

La barre de menu contient :

- **Fichier** : Recharger les sauvegardes (`F5`), Exporter un aperçu du personnage, Réglages
  (`Ctrl+,`), Quitter (`Ctrl+Q`) ;
- **Aide** : Revoir le tutoriel (`F1`), ouvrir le dossier des copies de sécurité ou des journaux,
  À propos.

Le journal complet est enregistré dans `userdata\logs\app.log`.

## Utilisation

1. **Quitte le jeu** (la pastille en haut à droite doit afficher « Jeu fermé »).
2. **Choisis le personnage** dans la liste « Personnage ». L'application trouve seule les sauvegardes
   Game Pass ; sinon, indique le dossier dans **Réglages**.
3. **Choisis un item** à gauche. La recherche fonctionne en français, en anglais ou par tag. Coche
   « Seulement les items avec un tag vérifié » pour ne voir que les objets sans risque.
4. **Ajoute des enchantements** au centre, s'il y en a de connus (voir plus bas).
5. **Règle l'objet** à droite : tag du jeu (modifiable), rareté, puissance. Les vérifications
   indiquent ce qui est sûr et ce qui est supposé.
6. **« Ajouter au personnage »** : l'objet apparaît en doré dans l'onglet « Inventaire du
   personnage ». Rien n'est encore écrit, et tu peux le retirer.
7. **« Enregistrer (N) »** : une confirmation résume les ajouts. Coche les cases, puis confirme.
8. **Suis la routine hors ligne** décrite dans les règles, lance le jeu et regarde ton inventaire.

`Ctrl+F` place le curseur dans la recherche d'items.

## Profil : niveau, émeraudes, livres enchantés

L'onglet **« Profil du personnage »**, en bas de la fenêtre, affiche les attributs de la sauvegarde
(liste `Ability.Attributes`). Change les valeurs voulues, clique sur **« Appliquer au personnage »**,
puis sur **« Enregistrer »**.

| Groupe | Attributs (nom dans la sauvegarde) | Bornes |
|---|---|---|
| Personnage | Niveau (`Level`), Expérience (`XP`), Points d'enchantement (`EnchantmentPoints`) | niveau 1 à 1000 |
| Monnaies | Émeraudes (`Emeralds`), `SpringStone` | 0 à 2 147 483 647 (entier 32 bits) |
| Avancé | Renouvellements et niveaux des marchands | à modifier avec prudence |

- **Le niveau** est écrit à ses deux emplacements : l'attribut `Level` et `MetaData.Level`, affiché
  dans la liste des personnages.
- **Points d'enchantement :** d'après ta sauvegarde, il y en a 1 par niveau gagné (niveau 2 : 1 point),
  comme dans MCD1. Monter le niveau ici ne les donne pas : ajoute-les toi-même si tu veux.
- **L'expérience** n'est pas recalculée. Si le jeu recalculait le niveau à partir de l'expérience, le
  niveau pourrait revenir en arrière au lancement : dans ce cas, augmente aussi l'expérience.
- **Seules les cases modifiées** sont écrites : une expérience décimale (ex. 1492,25), affichée
  arrondie, n'est pas touchée si tu ne la changes pas.
- Les modifications du profil sont conservées même si le jeu réécrit la sauvegarde avant
  l'enregistrement : les valeurs choisies sont réappliquées à la version la plus récente.

**Livres enchantés.** Le jeu les range dans quatre collections (`CollectedEnchantmentBooksOffensive`,
`…Defensive`, `…Utility`, `…Uncategorised`). Elles étaient vides dans ta sauvegarde, et aucun livre
n'était dans l'inventaire : leur format n'est donc pas encore connu, et l'éditeur n'en invente pas,
pour ne pas corrompre le profil. Dès qu'un livre apparaît (ramasse-le en jeu, quitte, puis
**Recharger**) :
- il s'affiche dans le cadre « Livres enchantés » du profil, où tu peux en faire jusqu'à 20 copies
  exactes, enchantement compris ;
- son tag devient « vérifié », et il apparaît dans la liste des items (catégorie « Livre enchanté »).

Le bouton **« Dupliquer… »** de l'onglet Inventaire fait la même chose pour n'importe quel objet, par
exemple une arme enchantée. Une copie exacte garde le format du jeu : c'est la façon la plus sûre de
multiplier un objet.

## Icônes des objets

L'application affiche une icône à côté de chaque objet : dans la liste, dans le résumé (en grand) et
dans l'inventaire. Elle utilise les images que tu déposes dans **`data\icons\`**. Sans image, elle
affiche une vignette avec les initiales de l'objet, teintée selon sa rareté.

**Noms reconnus sans renommage** (sous-dossiers acceptés ; formats PNG, WEBP, JPG, TGA) :

| Style | Exemple |
|---|---|
| Nom exporté du jeu | `T_UI_Icon_MysticChest.png`, `T_Artifact_Satchel_Fire_Icon.png` |
| Tag exact | `SW.Item.Greatsword.png`, `SW.Effect.Sharpness.png` (enchantement) |
| Nom anglais ou clé | `Mystic Chest.png`, `greatsword.png` |

Pour comparer, l'application retire les mots génériques (`T`, `UI`, `Icon`, `Item`, `Artifact`…) :
`T_UI_Icon_MysticChest` et `SW.Item.MysticChest` deviennent tous deux « mysticchest ». Après avoir
ajouté des images, clique sur **Recharger** : le journal indique combien d'objets ont leur icône.
**Réglages → « Écrire la liste des noms attendus »** crée `data\icons\_noms_attendus.txt`, avec le
nom conseillé pour chaque objet encore sans image.

### Obtenir les vraies images du jeu

**Option A : extraire les textures avec FModel.** FModel est un visualiseur libre des fichiers
Unreal Engine ([fmodel.app](https://fmodel.app)). Il lit les archives du jeu sans les modifier. Les
libellés exacts peuvent varier selon sa version.
1. Installe FModel et lance-le.
2. Dans le sélecteur de jeu, ajoute un jeu non détecté :
   - dossier : `D:\Xbox games\Minecraft Dungeons II\Content\Dungeons\Content\Paks` (celui qui contient
     `Dungeons-WinGDK.utoc` et `.ucas`) ;
   - version : la plus récente d'Unreal Engine 5 proposée.
3. Charge l'archive `Dungeons-WinGDK.utoc` dans l'onglet des archives.
4. Cherche les textures d'icônes, par exemple avec la recherche « Icon » ou le nom anglais d'un objet
   (« Greatsword »). Ce sont des fichiers de type `Texture2D`.
5. Clic droit sur le dossier trouvé → export des textures en PNG. Les fichiers vont dans le dossier de
   sortie de FModel (défini dans ses réglages).
6. Copie ces PNG dans `data\icons\` (sous-dossiers compris), puis clique sur **Recharger**.

Si FModel demande une **clé AES**, les archives sont chiffrées : l'extraction n'est alors pas possible
simplement, et l'éditeur ne fournit pas de clé. Passe à l'option B.

**Option B : enregistrer les images depuis un wiki.** Les pages d'objets de Minecraft Dungeons II sur
le [Minecraft Wiki](https://minecraft.wiki/w/Minecraft_Dungeons_II) montrent leur icône. Clic droit →
« Enregistrer l'image sous… » dans `data\icons\`, en la nommant d'après le nom anglais de l'objet
(`Mystic Chest.png`).

**Option C : capture d'écran.** Recadre l'icône depuis l'inventaire du jeu, et enregistre-la sous le
nom anglais de l'objet.

## Tester sans risque

- **Avant d'enregistrer :** « Exporter un aperçu JSON… » (onglet Inventaire) écrit le personnage
  modifié dans un fichier lisible, sans toucher aux sauvegardes.
- **Sur une copie :** copie ton dossier `wgs` ailleurs, puis choisis cette copie dans **Réglages →
  Dossier des sauvegardes**. L'application lit et écrit alors uniquement cette copie.
- **Tests automatisés :** voir [plus bas](#tests-automatisés).

## Tags vérifiés, tags supposés et enchantements

Dans la sauvegarde, un objet est identifié par un **tag** : son identifiant interne dans le jeu,
par exemple `SW.Item.Greatsword` pour la grande épée ou `SW.Rarity.Rare` pour la rareté. C'est ce
texte que l'application écrit dans ton personnage. Un tag que le jeu ne connaît pas peut empêcher le
personnage de se charger.

**Tu n'as pas à saisir de tag.** Quand tu choisis un objet, son tag se remplit tout seul. Le champ
« Tag du jeu » est aussi une liste déroulante de tous les tags connus, si tu veux en choisir un autre.

**D'où viennent les tags.** Il n'existe pas de liste officielle publique : les sites de données
(dungeons.tools, metabot.gg) donnent les noms affichés en jeu, mais pas les identifiants internes.
L'application s'appuie donc sur des tags **réellement vus dans des sauvegardes** :
- **28 tags intégrés**, relevés dans une vraie sauvegarde du 01/10/2026 (jeu 1.1.1.0) :
  - armes : épée, hache, grande épée, rapière, pelle, arc, grand arc, arc puissant, arbalète à dispersion ;
  - 10 pièces d'armure : Miel, Mystique, Usé par le temps, Champignon, Fantôme, Intrépide, Realmreacher ;
  - 8 artéfacts et 1 talisman ;
  - les raretés Commun, Rare et Spécial.
- **Le registre** `userdata\knowledge.json` : à chaque chargement, l'application note les tags présents
  dans ta sauvegarde (inventaire, butin découvert, collections). Un objet trouvé en jeu devient
  utilisable au prochain « Recharger ». S'il porte un nom du catalogue, il en prend le tag
  (ex. « Power Bow » ↔ `SW.Item.Powerbow`) ; sinon il s'ajoute à la liste.

| État | Signification |
|---|---|
| **tag vérifié** | Vu dans une vraie sauvegarde : sans risque |
| **tag supposé** | Construit par analogie, jamais vu en jeu : l'application demande confirmation |
| **sans tag** | Nom repris de Minecraft Dungeons 1, absent de MCD2 (ex. « Armure du champion » : l'armure y est découpée en pièces) |

La case **« Seulement les objets reconnus dans MCD2 »**, cochée par défaut, masque les noms de MCD1.
Les noms français des objets de MCD2 sont proposés par l'application : les noms officiels en jeu
peuvent différer.

**Enchantements.** Dans MCD2, un enchantement est un objet « Rerollable » qui contient l'effet
(`SW.Effect.Sharpness`…), son intensité et son modèle (`SW.EffectTemplate.Sharpness.I`). L'application
propose les enchantements vus dans tes sauvegardes et les recopie **tels quels**, niveau compris. Leur
niveau n'est pas encore modifiable, car son codage (intensité, modèle .I/.II/.III) n'est pas confirmé.

## Comment l'enregistrement fonctionne

Une sauvegarde Game Pass est un dossier « wgs » (Xbox Connected Storage) :

```
wgs\<compte>\
  containers.index             index de tous les conteneurs
  <GUID du conteneur>\
    container.<N>              manifeste : nom des données → GUID du fichier
    <GUID des données>         pour un personnage : le JSON
```

Pour enregistrer, l'application reproduit ce que fait le jeu :
1. Elle vérifie que le jeu est fermé. Si le personnage a changé sur le disque depuis son
   chargement, elle **rejoue tes ajouts** sur sa version la plus récente, et ta progression est
   conservée. C'est le cas si tu as ajouté des objets jeu lancé : il réécrit la sauvegarde en
   quittant. Un simple changement de numéro par l'Xbox app, contenu identique, n'est pas un conflit.
2. Elle copie tout le dossier `wgs` dans `userdata\backups\saves-AAAAMMJJ-HHMMSS`.
3. Elle écrit le JSON dans un **nouveau** fichier au GUID inédit, puis le manifeste `container.<N+1>`.
4. Elle met à jour l'index : numéro de version, taille, horodatages, état « modifié ». Elle efface
   aussi le drapeau « téléversé », pour que l'Xbox app sache qu'il faut envoyer la version locale.
   Tout le reste de l'index est recopié à l'octet près.
   Chaque fichier est d'abord écrit en `.tmp`, puis mis en place avec `os.replace`. Si l'Xbox app
   tient un fichier ouvert, l'opération est réessayée plusieurs fois. Si elle modifie l'index
   pendant l'écriture, l'application annule et recommence depuis l'étape 1, jusqu'à 3 fois.
5. Elle relit tout depuis le disque. En cas d'écart, elle remet l'ancien index et supprime les
   nouveaux fichiers : la sauvegarde reste dans son état d'avant.
6. Elle retire l'ancienne version du conteneur, comme le fait le jeu.

Le JSON est réécrit avec la même mise en forme que le jeu, y compris l'écriture exacte de chaque
nombre décimal (le jeu en écrit certains sur 17 chiffres) : sans modification, il est identique à
l'octet près, et seuls les champs modifiés changent. Ce format a été vérifié sur une vraie sauvegarde du 30/09/2026 et correspond à celui
documenté par la bibliothèque [GamePassStorage](https://github.com/ChristopherVR/GamePassStorage).

## Restaurer une sauvegarde

1. Quitte le jeu et l'application Xbox.
2. Ouvre `userdata\backups` (bouton « Ouvrir le dossier des copies » dans les Réglages) et choisis la
   copie `saves-AAAAMMJJ-HHMMSS` voulue.
3. Remplace le contenu du dossier `wgs` des sauvegardes par celui de la copie.
4. Suis la routine hors ligne (règle 2) pour que le cloud reprenne cette version.

## Dépannage

| Message | Cause probable | Que faire |
|---|---|---|
| Aucun personnage trouvé | Pas encore de personnage hors ligne, ou sauvegardes ailleurs | Crée un personnage hors ligne en jeu, ou indique le dossier dans Réglages |
| Personnage en ligne : non modifiable | Tes données sont sur les serveurs du jeu | Utilise un personnage hors ligne |
| Le jeu est encore lancé | Le jeu ou son lanceur tourne | Quitte complètement le jeu |
| L'application Xbox modifie les sauvegardes en ce moment | Synchronisation cloud en cours | Attends quelques secondes ou coupe Internet, puis réessaie |
| Ce conteneur contient maintenant un autre personnage | Personnage supprimé puis recréé entre-temps | Clique sur Recharger, puis refais tes ajouts |
| Format de personnage inconnu / version d'index inattendue | Mise à jour du jeu | L'éditeur refuse d'écrire ; il faudra l'adapter au nouveau format |
| Le personnage ne se charge plus | Tag inconnu du jeu | Restaure la dernière copie de sécurité |
| L'objet n'apparaît pas | La synchronisation cloud a remis l'ancienne version | Restaure si besoin, et suis la routine hors ligne |

## Tests automatisés

```powershell
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.venv\Scripts\python.exe -m pytest
```

Les 62 tests couvrent :
- le format wgs : nouvelle génération, conteneurs voisins intacts, retour arrière, fichiers verrouillés, index modifié pendant l'écriture, chemins longs ;
- le JSON du personnage : aller-retour exact et ajout d'objets ;
- la session d'édition : jeu lancé, sauvegarde réécrite par le jeu (ajouts rejoués), personnage en ligne ;
- l'édition du profil (niveau, émeraudes, bornes, rejeu) et la duplication de livres ;
- le registre des tags ;
- les icônes (noms reconnus, images illisibles, affichage) ;
- l'interface complète, hors écran.

Ils tournent sur de **fausses** sauvegardes créées dans un dossier temporaire, jamais sur les tiennes.

## Limites connues

- Le catalogue reprend les noms de Minecraft Dungeons 1 : beaucoup d'items de MCD2 manquent encore
  (armures en pièces séparées, talismans…). Ils s'ajoutent quand tu les trouves en jeu, ou à la main
  dans `data/items.json`.
- Les enchantements et les livres enchantés ne sont disponibles qu'une fois vus dans une sauvegarde.
- Seuls les personnages hors ligne de la version Game Pass sont pris en charge. La version Steam
  stocke peut-être ses sauvegardes autrement : ce n'est pas vérifié.
- La synchronisation cloud Xbox peut remettre l'ancienne version : suis la routine hors ligne.
- Windows uniquement.
