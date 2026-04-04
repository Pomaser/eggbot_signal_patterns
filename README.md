# Signal Generator pro EggBot

Nástroj pro generování organických a digitálních signálů pro plotr [EggBot](http://egg-bot.com/). Výstupem jsou SVG soubory 3200 × 800 px s deseti pojmenovanými vrstvami kompatibilními s Inkscape.

![Ukázka organických křivek](src/ga_eggbot/images/generations3-5.png)

## Spuštění

```bash
python app.py
```

Žádné externí závislosti — pouze Python stdlib (tkinter, math, random).

## Záložky

### Organické signály

Vlnové křivky generované kombinací sinusových funkcí s amplitudovou modulací. Každý jedinec má 8 parametrů, které určují tvar vlny (vlnová délka, amplituda, modulace). Křivky se obtáčejí přes šířku plátna a překrývají se — výsledný vzor připomíná organické textury.

### Digitální signály

Čisté digitální průběhy v pěti variantách:

| Typ | Popis |
|-----|-------|
| **square** | Obdélníkový signál s nastavitelnou střídou |
| **sawtooth** | Pilový signál (lineární nárůst) |
| **triangle** | Trojúhelníkový signál |
| **pcm** | Náhodný binární vzor (vzhled PCM dat) |
| **staircase** | Schodišťový signál s N úrovněmi |

## Ovládání

- **Nová generace** — vygeneruje novou sadu náhodných vzorů
- **Uložit SVG** — uloží vzor do složky `svg/` jako `organic_XXXX.svg` nebo `digital_XXXX.svg`
- **q + Enter** v terminálu — ukončí aplikaci

## Výstupní SVG

- Rozměry: 3200 × 800 px
- 9 pojmenovaných vrstev (`1_Layer`–`9_Layer`) kompatibilních s Inkscape a doplňkem Axidraw/EggBot
- Křivky jsou v `1_Layer`, ostatní vrstvy jsou prázdné pro ruční přidání barev pera
- Vlny začínají i končí na stejné výšce (y) — bezešvý tisk na vejci

## Struktura projektu

```
app.py                  hlavní aplikace (záložky Organické / Digitální)
individual.py           organický jedinec — algoritmus vlny
generation.py           správa organické populace
digital_individual.py   digitální jedinec — typy signálů
digital_tab.py          GUI záložka pro digitální signály
svg_renderer.py         export do SVG
src/ga_eggbot/          původní referenční implementace v Processing
```
