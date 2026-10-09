## Här skriver vi vad som gjorts under dagen.

```md
Datum - Rubrik
Medverkande:
Beskrivning:
Information: - vilken fil du jobbat i - var finns ytterligare information - ex mapp/fil
```

---

## 08/10 "setup uv, python package och install dependencies"

### Medverkande: Lisa, Rickard, Miranda, Filippa

**Beskrivning:** skapade uv med "uv init --no-package --python 3.13"

- OBS: KÖR UV SYNC
  Information: se pyproject.toml

---

## 09/10 "hämta data och börja göra eda"

### Medverkande: Lisa, Rickard, Miranda

**Beskrivning:** Vi har hämtat datan för att göra eda. Fyll gärna på (undersök mera).
För eda (svedavia) så testade vi bara med arrivals, ej departures.

**Information:**

- Se i uppdatering-kanalen i discord för .env info
- Se eda-filer under eda-mappen

## 09/10 "Hämta datan med 3 dates & alla Svedavia-flygplatser"

### Medverkande: Miranda

**Beskrivning:**
I eda_svedavia.ipynb har funktioner lagst till för att :

- Läsa in IDAG, IGÅR & I FÖRRGÅR som datum (gick inte att läsa 3 dagar bakåt..)
- Läsa in alla Svedavias flygplatser
- Hämta dem med hjälp av URL:en & API nyckel
- Få en dataFrame med arrivals
- Få en dataframe med departures

**Information:**

- Datumen är från dagen man hämtar och två dagar bakåt (inga prefixa datum)
- I DataFrame gjorde även två kolumner: "Swedavia_airport_name" & "Date_fetched" för att se datum för hämtning och Swedavia fygplats-namn
