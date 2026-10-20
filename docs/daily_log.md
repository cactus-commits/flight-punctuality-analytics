## Här skriver vi vad som gjorts under dagen.

```md
## Datum - Rubrik

### Medverkande:

**Beskrivning:**
**Information:** - vilken fil du jobbat i - var finns ytterligare information - ex mapp/fil
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

---

## 11/10 "EDA flight status (arrivals)"

### Medverkande: Rickard

**Beskrivning:** Undersökte kolumnen `remarksEnglish` för arrivals (flight status). Varje flyg har 0, 1 eller 2 meddelanden: ett om flygets status och ett om bagage. Varje meddelande har en tag, NEUTRAL eller NEGATIVE. NEGATIVE är 11 inställda flyg + 9 flyg med ny tid (Arrives/Estimated), troligen försenade men inte verifierat. Inget "Delayed"-meddelande finns för arrivals.

**Information:**

- Fil: `eda/eda_svedavia.ipynb`, se avsnittet "Summary: flight status (arrivals)"
- Kvar att göra: jämföra de 9 flygen med planerad tid, och göra samma undersökning för departures

---

## 11/10 "Hur vi räknar försening"

### Medverkande: Alexandra

**Beskrivning:** Eftersom arrivals inte har något "Delayed"-meddelande räknar vi försening från tiderna i stället.

- Försening = faktisk tid (eller beräknad tid om flyget inte landat/startat än) minus planerad tid
- Försenat = 15 min sent eller mer (kan ändras i `DELAY_THRESHOLD_MIN`)
- Inställda och borttagna flyg får ingen försening, de har egna kolumner
- Funktionen `add_delay` lägger till kolumnerna: `delay_minutes`, `is_cancelled`, `is_deleted`, `has_time`, `is_delayed` och `flight_date`
- `flight_date` = planerad tid i svensk tid. Vi använder den i stället för `Date_fetched`, som bara är datumet vi frågade API:t om
- Dubbletter (samma flyg på två datum, runt midnatt) är borttagna
- Kollade mot Swedavias egna varningar (NEGATIVE): de stämmer med vår definition, men de hittar bara 12 av 141 försenade arrivals. Därför är tiderna bättre

**Information:**

- Fil: `eda/eda_swedavia.ipynb`, se avsnittet "Delay definition"

---

## 12/10 "DBdiagram från swedavia filen"

### Medverkande: Filippa

**Beskrivning** Granskade igenom swedavia filen och småbörjade lite med DBdiagram

- Gått igenom EDA filen från eda_swedavia.ipynb.
- Undersökt kolumner och datatyper med hjälp av df.info() och df.dtypes
- Identifierat vilka kolumner som kan användas för faktatabellen och dimensionstabellerna t.ex. flygplatser, flygbolag och datum

## 13/ 10 - DM MODEL | SETUP SNOWFLAKE ACCESS CONTROL | DATA LOAD EXTRACT (WIKI-DATA & SWEDAVIA DATA)

### Medverkande: Miranda, Lisa, Filippa, Rickard

**Beskrivning:**

1. Skapat dbml i db-diagram med fact och dim-tables.
2. fixade setup dbt/dlt roles, database och warehouse
3. Skapade data_load_extract filer för wikipedia data & swedavia data
4. Satte upp profiles.yml
5. Satte upp .dlt/secrets.toml i orchestration-mappen

**Information:**

**github project issue 34:**

- profiles.yml
- secrets.toml [ligger i .dlt/]

**dm_model:**

- png bild på modellen samt dbml-fil för koden.

**Worksheets mappen:**

- Skapat roller i DLT/DBT
- skapat user developer
- Grantat roll
- Skapat en Database
- Skapat en warehouse
- Allt fixat inom worksheet_snowflake foldern

**data_load_extract:**

- Skapat script med dlt resources för wikipedia data airports
- Skapat script med dlt resources för wikipedia data airlines
- Skapat script med dlt resources för swedavia data arrivals
- Skapat script med dlt resources för swedavia data departures
- Skapat script för run_pipeline där resources laddas in i pipelinen och in till snowflake

---

## 14 Okt - sources.yml, scr arrivals & departures

### Medverkande: Miranda & Rickard

**Beskrivning:**

- dimensional model har nu ändrats lite för att stämma överrens med dbt-steget för models (src/dim/fct)
- sources.yml
  - sources för wikipedia - data och Swedaviadata har skapats. Dessa ska användas i modellerna för att enkelt kunna hämta sources.
- Arrivals
  - i src_arrivals har kod för sourcen arrivals skrivits utifrån dimensional modellen NOTERA att flight_number är swedavias egna flight_id.
- Departures
  - i src_departures har kod för sourcen departures skrivits utifrån dimensional modellen NOTERA att flight_number är swedavias egna flight_id.
- Worksheets_snowflake
  - små korrigeringar i setup_db och setup_roles, borttagning av överflödig text
- Säkerhet
  - secrets.toml borttagen ur repot, Snowflake-lösenordet bytt
  - lösenord i setup_users.sql ersatt med <CHANGE_ME>
  - profilnamn rättat till dbt_flight, dbt debug grönt
  - src_departures skriven och testad med dbt show
- Backlog
  - #82 generate_schema_name flyttad före #37

**Information:**
**Mapp:**

- data_transformation -> dbt_flights -> models -> src -> sources.yml / src_arrivals
- data_transformation -> dbt_flights -> models -> src -> src_departures

---

## 14 Okt - src airline & airport och exempelfiler för secrets

### Medverkande: Alexandra

**Beskrivning:**

- src_airline
  - skriven utifrån Wikipedia-källan airlines och dimensional modellen (airline_iata, airline_icao, airline_name, country)
  - tar bort mellanslag, gör om tom text till null och behåller bara flygbolag med minst en kod
  - OBS: IATA-koder är inte unika i Wikipedia-listan (t.ex. SK finns två gånger), dubbletter måste hanteras i dim_airline
- src_airport
  - skriven utifrån Wikipedia-källan airports (airport_iata, airport_icao, airport_name, city)
  - samma rensning som src_airline

- Skapade `.env.example` med nycklarna `BASE_URL` och `FLIGHT_KEY` (utan riktiga värden)
- Skapade `orchestration/.dlt/secrets.toml.example` med Snowflake-uppgifterna för dlt (utan lösenord)
- Ändrade `.gitignore` så att example-filen i `.dlt/` kommer med i git, medan `secrets.toml` fortfarande ignoreras

## 15/10 Dim and fct tables

### Medverkande: Miranda, Rickard, Filippa, Alexandra

**Beskrivning:**

- fct_arrivals / fct_departures
  - added surrogate keys
  - calculations for delayed
  - is cancelled
- dim_airport
  - surrogate key from airport_iata
  - filtered out airports without IATA (143 rows: heliports, hospitals, closed airbases)- macros
- Macros 
  - generate schema name
- dbt utils
  - packages.yml
- some changes in the dimensional model
  - example:
    arrival_airport_id
    departure_airport_id
    båda dessa kopplas till airport_id i dim_airport

**Information:**

- in folder dbt_flights `uv run dbt deps`

--- 
### 16/10 "dim-modeller och marts samt tester i schema.yml"
Medverkande: Miranda, Lisa och Rickard
Beskrivning: Sett över och fixat i samtliga modeller (src, dom, fct) samt skapat två marts - en för arrivals och en för departures.
Stötte på en del problem iom dbt testing där vissa hade dubletter på id - därav vissa ändringar. Kört 'dbt build' och nu funkar det.
Sen korrigering:
- mart_arrivals_info: la till Deleted-filtret som redan fanns i mart_departures_info
- fct_arrivals: qualify väljer nu raden som inte är Deleted först, så att flygningar inte försvinner när två versioner finns
- dim_airline: rättat coalesce/max så att 18 flygbolag inte längre får ICAO "Missing"
Information:
- uppdaterat och ändrat lite i dimensional model 
- schema.yml - dbt testing
- models (kolla igenom alla)
- snowflake under warehouse

---

## 18/10 "Kontroll av dbt-to-dos och 'Unknown' i marts"

### Medverkande: Alexandra

**Beskrivning:**

- Gått igenom to do-listan från 15/10 och tagit bort den, eftersom allt på den är gjort:
  - IATA-dubletter i dim_airline och dim_airport är borta (en rad per IATA-kod)
  - dim_date finns och alla rader i fct matchar ett datum
  - marts joinar fct med dim_date, dim_airline och dim_airport
  - departure_airport_name / arrival_airport_name finns i båda marts
  - inga NULL i dim_airline (saknade värden är texten 'Missing')
- Tog bort kommentarer i src_airport som beskrev rensning som modellen inte gör (rensningen sker i dim-modellerna)
- Ändrade mart_arrivals_info och mart_departures_info: airline_name, airline_country, departure_airport_name och arrival_airport_name är nu 'Unknown' i stället för NULL när flyget inte matchar någon rad i dim-tabellerna. Då visas inga tomma grupper i dashboarden
- `dbt test` (10 tester) och `dbt run` på båda marts är gröna

**Information:**

- Ca 3-8 % av flygen har ett flygbolag eller en flygplats som inte finns i Wikipedia-listorna, så de visas som 'Unknown'. Flygbolag: Swedavia saknar ofta IATA-kod och anger bara ICAO (t.ex. JON, FRO). Flygplatser: små flygplatser och platshållare (t.ex. RNB, KRN, ZZZ). Detta ska nämnas i README och på presentationen

---

```md
### 18/10 - "Setup Dagster Project, create dlt assets and update sources.yml"
### Medverkande: Lisa 
**Beskrivning:**
- Initierade dagster project med 'uvx create-dagster@latest project my-project' utan uv i mappen
(källa: https://dagster.io/docs/guides/build/projects/creating-projects)
- uppdatera pyprojekt.toml för att dagster ska kunna hitta load-filerna utan sys
- uv add dagster-dg-cli
- uv sync
- Lägg till @dlt.source i hämtningen av wikipedia-datan - för dagster assets
- kolla att kopplingen fungerar: uv run python -c "from orchestration.defs.assets.dlt_assets import swedavia_dlt_assets, wikipedia_dlt_assets; print('ok')"
- skapa orchstreation/src/orchestration/defs/resources.py för att skapa resurserna
- testa i dagster ui: uv run dagster dev -m orchestration.definitions
- hämta namnen "aliasen" från dagster till sources.yml tex. dlt_flights_source_arrivals
- uppdatera sources.yml med aliasen för dagster 

**Information:** 
- data_load_extract/get_wikipedia_data.py 
- data_transformation/dbt_flights/models/src/sources.yml
- orchestration/src/orchestration/defs/assets/dlt_assets.py
```
--- 

## 18/10 "Streamlit-dashboard"

## 18/10 "Saknade flygplatser i dim_airport"

### Medverkande: Alexandra

**Beskrivning:**

Första versionen av dashboarden är klar. Den läser från `mart_arrivals_info` och `mart_departures_info` i Snowflake.

- Sammanfattning överst: en ruta för arrivals och en för departures. Antal förseningar står först (t.ex. 118 delays), under det andel försenade, antal flyg och antal inställda
- Delays by date: ett diagram per riktning. Staplarna visar försenade (orange, underst) och i tid (grå). Procenten ovanför varje stapel är andelen försenade den dagen
  - Dagar som inte är klara (mer än 5 % av de icke-inställda flygen saknar faktisk tid) är bleka och märkta "(partial)". Just nu gäller det 16/10, som är dagen vi hämtade datan
  - Båda diagrammen har samma y-axel så att de går att jämföra
- Delays by airline and airport: rankning per flygplats (först) och flygbolag. Standard är andel försenade, eftersom antal bara visar vilka som flyger mest (SAS och Norwegian hamnar alltid högst)
  - Streckad linje = genomsnittlig andel försenade för alla flyg i filtret. Staplar till höger om linjen är sämre än normalt
  - Flygplatser och flygbolag med färre än 5 mätta flyg per riktning visas inte i andelsrankningen


**Information:**

- Fil: `streamlit_app/app.py`, kör `uv run streamlit run streamlit_app/app.py` från repots rot
- Lösenord: kopiera `.streamlit/secrets.toml.example` till `.streamlit/secrets.toml` och fyll i (ignoreras av git)
- Datan täcker bara tre dagar, så datumdiagrammet har få staplar. 13/10 har få flyg eftersom hämtningen började mitt på dagen, men räknas inte som partial eftersom nästan alla flyg har faktisk tid

I dashboarden dök flygplatserna Ronneby och Kiruna upp som "Unknown". Vi har nu lagt till dem.

- Vad som var fel: flygplatsnamnen kommer från Wikipedia-listan (`src_airport`). Ronneby (RNB) och Kiruna (KRN) finns inte i den listan, varken på kod eller namn. Flyg till och från dem hittade därför ingen rad i `dim_airport` och fick 'Unknown' i marts (45 flyg, 33 för RNB och 12 för KRN)
- Varför det spelar roll: det är Swedavias egna flygplatser och flygplatsdiagrammet är det viktigaste för den som äger dem. Två "Unknown" där ser ut som ett fel
- Vad vi gjorde: la till en seed, `seeds/missing_airports.csv`, med RNB och KRN (kod, namn, stad) och la in raderna i `dim_airport`. En seed-rad används bara om koden inte redan finns i Wikipedia-listan, så vi får inga dubletter om Wikipedia rättas senare
- Varför en seed: det är bara två rader, och det syns tydligt i repot vad vi har lagt till för hand. Alternativet var att hämta namnen från Swedavia-datan, men det kräver mer arbete och är inte nödvändigt för en PoC
- Seeden hamnar i schemat `warehouse` (inställt i `dbt_project.yml`), bredvid dim-tabellerna, där dbt-rollen redan har rättigheter
- Kört `dbt seed` och `dbt build -s dim_airport+`, alla tester gröna. Efteråt finns inga 'Unknown' kvar på den svenska sidan av flyget i marts

**Information:**

- Filer: data_transformation -> dbt_flights -> seeds/missing_airports.csv, models/dim/dim_airport.sql, dbt_project.yml
- Utländska flygplatser som saknas (t.ex. AGH, SFT, ZZZ) ligger inte i seeden. De visas fortfarande som 'Unknown' på andra sidan av flyget i marts, men inte i dashboardens flygplatsdiagram, som bara visar den svenska sidan
- Kör `uv run dbt seed` i dbt_flights innan `dbt build` om du har en tom databas

---

## 19/10 "Färdigställt Dagster och satt upp Docker"

### Medverkande: Filippa, Lisa, Rickard, Miranda

**Beskrivning**

- Vi har skapat jobs, assets, sensor, schedule i orchestration/src/ochestration och testat att det funkar i dagster UI
- Vi har satt upp docker med två dockerfiles (dwh och dashboard) och testat att det funkar med docker-compose up --build
- 

**Information:**
- Vi ändrade i app.py för att kunna koppla docker via .env
- Uppdatera .env filen - se pinnat meddelande i discord
- Flytta ut .dlt mappen till root

**Todo**
- Sätta upp Azure

---

## 20/10 "Deploy till Azure och städning av README"

### Medverkande: Rickard, Filippa, Miranda, Lisa

**Beskrivning:**

- Uppdaterat `README.md` så att den stämmer med koden: projektstruktur, Snowflake-roller, Dagster-kommandot, beskrivning av src/fct/mart och Azure-stegen. Lagt till kända begränsningar (Unknown-flyg och UTC-datum)
- Tagit bort den gamla `secrets.toml`-instruktionen, eftersom appen nu läser `.env`
- Undersökt datumet i `fct_arrivals`: `date_id` tas från UTC-tiden, så 135 ankomster mellan 00:00 och 02:00 svensk tid hamnar på dagen innan. Inte fixat, dokumenterat under Known limitations i README
- Forkat repot till eget konto för egen deploy. Gruppens repo ligger som `upstream` med push avstängd (`no_push`), så att inget hamnar där av misstag
- Lagt till `image: ${ACR_LOGIN_SERVER}/...` för `dwh_pipeline` och `dashboard` i `docker-compose.yml`, så att alla kan pusha till sitt eget ACR med samma fil
- Skapat ett Azure Container Registr med Admin user påslaget, byggt båda images och pushat dem dit
- Skapat en Container App för Dagster (2 CPU, 4 Gi, ingress på port 3000) med miljövariablerna från `.env`. Testat i Azure: `job_dlt` kördes manuellt och `dlt_success_sensor` startade `job_dbt` automatiskt, båda Success
- Skapat en Web App för Streamlit (Basic B1) med `WEBSITES_PORT=8501`, Streamlit-portarna och Snowflake-variablerna. Dashboarden visar data från Snowflake

**Information:**

- `.env` måste ha två understreck i alla namn: `DESTINATION__SNOWFLAKE__CREDENTIALS__...`. `profiles.yml` och `app.py` läser nu också dessa
- `app.py` läser schemat från `DASHBOARD_SCHEMA` (värde `mart`), som måste finnas i `.env` och i Web App
- Dagster-UI:t uppdateras inte alltid av sig självt. Ser en körning ut att hänga, ladda om sidan

**Todo:**

- Byta `DESTINATIONSNOWFLAKESCHEMA=` mot `DASHBOARD_SCHEMA=` i `.env.example`
- Bestämma om `date_id` ska fixas med `convert_timezone` eller stå kvar som begränsning
- Stoppa Container App när den inte används, för att spara kredit
- Presentation (#60) och individuell video (#61)