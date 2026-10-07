# Git Workflow (Branching & Pull Requests)

För att säkerställa ett strukturerat arbete i projektet använder vi **feature branches** från `main`.
All ny funktionalitet utvecklas i en egen branch och mergas till `main` via Pull Requests.
Vi använder Git för versionshantering och GitHub för repository, Pull Requests och kodgranskning.

---

## Snabbåtkomst

> Det du oftast behöver, samlat högst upp. Resten av dokumentet finns i [innehållsförteckningen](#innehåll).

### Co-authors (pair och mob programming)

Kontrollera din egen e-post med `git config user.email`. Lägg **inte** till dig själv som co-author, bara de andra du jobbat med.

| Namn | E-post |
|---|---|
| Miranda Lyng | lyngmiranda@gmail.com |
| Lisa Yllander | lisaylander92@gmail.com |
| Alexandra Kaktus | aurabyte.dev@gmail.com |
| Rickard Garnau | rickardgarnau@gmail.com |
| Filippa Jansson | filippa762@gmail.com |

Kopiera de rader du behöver:

```text
Co-authored-by: Miranda Lyng <lyngmiranda@gmail.com>
Co-authored-by: Lisa Yllander <lisaylander92@gmail.com>
Co-authored-by: Alexandra Kaktus <aurabyte.dev@gmail.com>
Co-authored-by: Rickard Garnau <rickardgarnau@gmail.com>
Co-authored-by: Filippa <filippa762@gmail.com>
```

Färdigt kommando (kort):

```bash
git commit -m "feat: add track ingest" -m "Co-authored-by: Miranda Lyng <lyngmiranda@gmail.com>"
```

Färdigt kommando (med beskrivning och flera co-authors):

```bash
git commit -m "feat: add login with email and password

Short description of what and why.

Co-authored-by: Lisa Yllander <lisaylander92@gmail.com>
Co-authored-by: Alexandra Kaktus <aurabyte.dev@gmail.com>"
```

Mer om formatet: [Pair och mob programming](#pair-och-mob-programming).

### Commit-prefix

| Prefix | Användning |
|---|---|
| `chore` | Set up / konfiguration |
| `feat` | Ny funktionalitet |
| `fix` | Buggfix |
| `docs` | Dokumentation |
| `refactor` | Kodomstrukturering |
| `test` | Tester |

Exempel: `feat: add weather data filtering`, `fix: resolve csv parsing error`, `docs: update README installation guide`.
Fler regler: [Commit guidelines](#commit-guidelines).

### Vanligaste kommandon

```bash
git status                                   # vilken branch, vilka filer?
git switch <branch>                          # byt branch
git checkout -b feat/<namn>                  # skapa ny branch
git add .                                    # stage:a alla ändringar
git commit -m "feat: beskrivning"            # commit
git push origin <branch>                     # pusha
git push --set-upstream origin <branch>      # första pushen av en ny branch
git pull origin main                         # hämta senaste main
```

---

## Innehåll

1. [Snabbåtkomst](#snabbåtkomst)
2. [Grundregler](#grundregler)
3. [Pair och mob programming](#pair-och-mob-programming)
4. [Standard Workflow](#standard-workflow)
   1. [Skapa en feature branch](#1-skapa-en-feature-branch)
   2. [Arbeta i din branch](#2-arbeta-i-din-branch)
   3. [Push din branch](#3-push-din-branch)
   4. [Fortsätta arbeta nästa dag](#4-fortsätta-arbeta-nästa-dag)
   5. [Uppdatera din branch](#5-uppdatera-din-branch-om-main-har-ändrats)
   6. [Skapa Pull Request](#6-skapa-pull-request)
   7. [Code Review](#7-code-review)
   8. [Merge till main](#8-merge-till-main)
   9. [Ångra senaste commit](#9-ångra-senaste-commit)
   10. [Tracking on a branch](#10-tracking-on-a-branch)
5. [Commit regler](#commit-regler)
6. [Commit guidelines](#commit-guidelines)
7. [Innan du loggar ut](#innan-du-loggar-ut)
8. [Säkerhetsregel](#säkerhetsregel)

---

## Grundregler

- Arbeta **aldrig** direkt i `main`
- All kod ska gå via Pull Requests
- Commit:a regelbundet
- Push:a innan du avslutar
- Kontrollera alltid vilken branch du är i
- Koden ska granskas av minst en person innan merge

[↑ Till toppen](#git-workflow-branching--pull-requests)

---

## Pair och mob programming

Om man jobbar tillsammans med någon/några är det viktigt att man lägger till **co-author** i slutet av commit message. Det är viktigt att det är **rätt e-postadress**. För att se vilken e-post du själv har:

```bash
git config user.email
```

**Regler för formatet:**

1. Rubrikrad först.
2. Tom rad.
3. En `Co-authored-by:`-rad per person, på formen `Co-authored-by: Namn <email@exempel.se>`.

**Exempel 1:** kort commit med `-m` två gånger

```bash
git commit -m "feat: add track ingest" -m "Co-authored-by: Miranda Lyng <lyngmiranda@gmail.com>"
```

**Exempel 2:** flera co-authors

```bash
git commit -m "Add authentication middleware

Co-authored-by: Rickard Garnau <rickardgarnau@gmail.com>
Co-authored-by: Lisa Yllander <lisaylander92@gmail.com>
Co-authored-by: Miranda Lyng <lyngmiranda@gmail.com>
Co-authored-by: Alexandra Kaktus <aurabyte.dev@gmail.com>"
```

**Exempel 3:** med prefix och egen beskrivning

```bash
git commit -m "feat: add login with email and password

{text for commit here}

Co-authored-by: Lisa Yllander <lisaylander92@gmail.com>
Co-authored-by: Alexandra Kaktus <aurabyte.dev@gmail.com>"
```

Kontrollera resultatet med `git log -1`.

[↑ Till toppen](#git-workflow-branching--pull-requests)

---

## Standard Workflow

### 1. Skapa en feature branch

När du börjar arbeta på en ny uppgift ska du skapa en branch från `main`.

```bash
git checkout main
git pull origin main
```

Skapa en ny branch:

```bash
git checkout -b feat/weather-analysis
```

Byta branch:

```bash
git switch <ditt_branch>
```

Första pushen av en branch:

```bash
git push --set-upstream origin <ditt-branch>
```

Exempel på branch-namn:

- `feat/created-ai-agent`
- `fix/csv-import-bug`

### 2. Arbeta i din branch

Om du inte står i rätt branch:

```bash
git fetch
```

Visa alla remote branches:

```bash
git branch -r
```

Byta branch:

```bash
git switch <branch-name>
git pull
```

Byta till en feature-branch (du måste ha gjort `pull` på branchen innan):

```bash
git switch feat/<branch-name>
```

All utveckling sker i din branch. Kolla att du är i rätt branch och commit:a:

```bash
git status
git add .
git commit -m "feat: add weather data import"
```

Commit:a gärna ofta när du gör framsteg.

### 3. Push din branch

När du har gjort commits ska du pusha branchen till GitHub.

```bash
git push origin feat/weather-analysis
```

Det gör att:

- arbetet sparas online
- andra kan se ditt arbete
- inget går förlorat

### 4. Fortsätta arbeta nästa dag

Om du fortsätter på samma branch behöver du inte byta till `main`. Kontrollera bara vilken branch du är i:

```bash
git status
```

Om du är i rätt branch kan du fortsätta arbeta direkt.

### 5. Uppdatera din branch (om main har ändrats)

Om andra i gruppen har mergat kod till `main` kan du uppdatera din branch:

```bash
git pull origin main
```

eller

```bash
git fetch origin
git merge origin/main
```

Detta minskar risken för merge-konflikter senare.

### 6. Skapa Pull Request

När din feature är klar:

1. Push:a branchen.
2. Skapa en Pull Request i GitHub.
3. Merge: din branch → `main`.

Pull Requesten ska innehålla:

- kort beskrivning av ändringen
- referens till user story eller task

### 7. Code Review

När en Pull Request skapas ska resten av teamet:

- läsa igenom koden
- kontrollera kodstandard
- ge feedback
- godkänna Pull Requesten

**Minst en person måste godkänna innan merge.**

### 8. Merge till main

När Pull Requesten är godkänd mergas branchen till `main`.
Efter merge ska alla i teamet uppdatera sin `main` innan de skapar nya branches.

```bash
git checkout main
git pull origin main
```

### 9. Ångra senaste commit

```bash
git reset --soft HEAD~1   # ångrar committen men behåller ändringarna
git reset --hard HEAD~1   # ångrar committen OCH kastar ändringarna
```

> Var försiktig med `--hard`. Ändringarna går inte att få tillbaka. Har du redan pushat committen, prata med teamet innan du ändrar historiken.

### 10. Tracking on a branch

Tracking betyder att en lokal branch är kopplad till en remote branch.

Kolla tracking på branchen:

```bash
git branch -vv
```

Koppla en lokal branch till en remote branch:

```bash
git branch -u origin/feature/branch_name
```

[↑ Till toppen](#git-workflow-branching--pull-requests)

---

## Commit regler

Vi använder följande commit-prefix:

| Prefix | Användning |
|---|---|
| `chore` | Set up / konfiguration |
| `feat` | Ny funktionalitet |
| `fix` | Buggfix |
| `docs` | Dokumentation |
| `refactor` | Kodomstrukturering |
| `test` | Tester |

## Commit guidelines

Commit-meddelanden ska följa dessa regler:

- Imperative mood (`add` istället för `added`)
- Max 50 tecken
- Ingen punkt i slutet
- Fokusera på varför ändringen görs

Exempel:

```text
feat: add weather data filtering
fix: resolve csv parsing error
docs: update README installation guide
```

[↑ Till toppen](#git-workflow-branching--pull-requests)

---

## Innan du loggar ut

Se till att ditt arbete är sparat:

```bash
git add .
git commit -m "feat: update weather analysis"
git push origin din-branch
```

## Säkerhetsregel

Om du är osäker innan commit eller push:

```bash
git status
```

Det visar:

- vilken branch du är i
- vilka filer som ändrats

[↑ Till toppen](#git-workflow-branching--pull-requests)