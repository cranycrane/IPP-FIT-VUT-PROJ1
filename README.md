Hodnocení: 6.7/7 bodů


Implementační dokumentace k 1. úloze do IPP 2023/2024\
Jméno a příjmení: Jakub Jeřábek\
Login: xjerab28

## Struktura repozitáře
- exceptions.py
- scanner.py
- xmlgenerator.py
- **parse.py**

## exceptions.py
Obsahuje definované různe typy výjimek, které v rámci programu používám a následně odchytávám v hlavním programu a ukončuji se specifikovaným návratovým kódem. 

## scanner.py - rozšíření NVP
Obsahuje třídu *Scanner* implementující lexikalní analyzátor. Třída implementuje návrhový vzor **Iterátor**, umožňuje tedy iterovaně získávat jednotlivé tokeny pomocí vestavěné metody *next*.\
Tento návrhový vzor jsem použil, protože mi v daném kontextu dává smysl - parser potřebuje postupně zpracovávat jednotlivé tokeny jeden po druhém. Využil jsem tedy vestavěné Python metody *__iter__*, která z této instance třídy udělá iterovatelný objekt.\
*Scanner* získává jednotlivé tokeny pomocí regulárních výrazů, kdy nejdříve odstraní ze zdrojového kódu všechny komentáře a následně postupně aplikuje tyto regulární výrazy.\
Jelikož je IPP23Code kontextově závislá, je potřeba tento kontext třídě předat (skrze metodu *setContext*), abychom dostali token, který očekáváme, nebo dostali výjimku, která značí chybu 22 nebo 23, podle toho, co očekáváme.\
Součástí souboru je i třída *Token*, která funguje pouze jako datová struktura pro přenos typu tokenu a hodnoty.

## xmlgenerator.py
Obsahuje třídu *XmlGenerator* a její primárním úkolem je umožnit rozhraní pro *Parse* pro jednoduché přidávání elementů do XML stromu a následné generování na standardní výstup.

## parse.py 
Obsahuje třídu *Parse* a vytvoření její instance v hlavním tělem programu. *Parse* s hlavní metodou *parse* zajišťuje syntaktickou kontrolu vstupního zdrojového kódu. Metoda *execute* zachycuje jednotlivé výjimky a ukončuje program dle jejich typů. Dle typu *OPCODE* obdrženého ze scanneru postupně získává další tokeny (argumenty) skrze pomocné metody jako například *checkSymb* nebo *checkLabel*. Tyto metody zajišťují nastavení kontextu lexikálního analyzátoru a odchycují případné výjimky, které mohou nastat, pokud analyzátor nenašel token, který jsme očekávali.\
*Parse* také využívá instance třídy *XmlGenerator*, do které přidává jednotlivé prvky XML stromu jako například operační kód se svými argumenty.\
Součástí hlavního těla je také kontrola počtu vstupních parametrů a vypsání nápovědy a základních informací o programu s parametrem *--help*

