# Website EAC De Sperwers

De nieuwe, statische website van EAC De Sperwers (eacdesperwers.nl), als vervanging van WordPress + Divi.
Snel, mobielvriendelijk en zonder plugins of updates.

- **Agenda en nieuws** bijwerken via een webformulier op `/admin/`, zonder code.
- Verlopen activiteiten verdwijnen vanzelf uit de agenda en de carrousel op de homepage.
- Gehost op **Cloudflare Pages**: gratis, en na elke wijziging staat de site binnen een minuut opnieuw online.

## Hoe het werkt

| Map | Wat staat erin |
| --- | --- |
| `content/agenda/` | Eén bestand per activiteit (datum, tijd, locatie, foto, links) |
| `content/nieuws/` | Eén bestand per nieuwsbericht |
| `content/pages/` | De vaste pagina's (trainingstijden, contributie, enz.) |
| `data/` | Menu, sponsors en algemene gegevens |
| `templates/` | De opmaak van de pagina's |
| `src/assets/` | Stylesheet, script, foto's en PDF's |
| `build.py` | Maakt van dit alles de website in `public/` |

In de pagina's staan een paar speciale regels die je moet laten staan:
`[[formulier:proefles]]` (en `lid-worden`, `opzeggen`, `contact`) plaatst een formulier,
`[[subpaginas]]` een overzicht van onderliggende pagina's en `[[pdf]]` een PDF-viewer.

Lokaal bouwen (optioneel): `pip install -r requirements.txt && python build.py`, daarna `public/` openen.

## Eenmalige installatie

### 1. Site koppelen aan Cloudflare Pages

1. Maak een gratis account aan op [dash.cloudflare.com](https://dash.cloudflare.com).
2. Ga naar **Workers & Pages → Create → Pages → Connect to Git** en kies de repository `btrip2017/eacdesperwers`.
3. Vul bij de build-instellingen in:
   - **Framework preset:** None
   - **Build command:** `pip install -r requirements.txt && python build.py`
   - **Build output directory:** `public`
4. Klik op **Save and Deploy**. De site staat daarna op een adres als `eacdesperwers.pages.dev`. Controleer hem daar eerst.

### 2. Domeinnaam overzetten (als alles klopt)

In het Pages-project: **Custom domains → Set up a custom domain** → `eacdesperwers.nl` (en `www.eacdesperwers.nl`).
Cloudflare legt uit welke DNS-instellingen je bij de huidige domeinbeheerder moet aanpassen.
De oude WordPress-adressen worden via `src/_redirects` automatisch doorgestuurd naar de nieuwe pagina's.

### 3. Beheeromgeving (`/admin/`) aanzetten

De beheeromgeving (Sveltia CMS) slaat wijzigingen op in GitHub. Daarvoor is een kleine inlog-helper nodig:

1. Ga naar [github.com/sveltia/sveltia-cms-auth](https://github.com/sveltia/sveltia-cms-auth) en klik op **Deploy to Cloudflare Workers**.
   Noteer het adres van de worker, bijvoorbeeld `https://sveltia-cms-auth.<naam>.workers.dev`.
2. Maak op GitHub een OAuth-app aan via **Settings → Developer settings → OAuth Apps → New OAuth App**:
   - **Homepage URL:** `https://eacdesperwers.nl`
   - **Authorization callback URL:** `<adres van de worker>/callback`
   - Klik op **Generate a new client secret** en bewaar Client ID en Client Secret.
3. Zet bij de worker in Cloudflare (**Settings → Variables**):
   - `GITHUB_CLIENT_ID` = de Client ID
   - `GITHUB_CLIENT_SECRET` = het Client Secret (als *Encrypt* opslaan)
   - `ALLOWED_DOMAINS` = `eacdesperwers.nl, eacdesperwers.pages.dev`
4. Vul het worker-adres in bij `base_url` in `src/admin/config.yml`.

**Wie mag bewerken?** Iedereen met een (gratis) GitHub-account die je als *collaborator* toevoegt aan de repository
(**Settings → Collaborators → Add people**). Die persoon logt in op `eacdesperwers.nl/admin/` met **Inloggen met GitHub**.

### 4. Formulieren (Web3Forms)

1. Ga naar [web3forms.com](https://web3forms.com), vul `info@eacdesperwers.nl` in en klik op **Create Access Key**. De sleutel komt per mail binnen.
2. Doe hetzelfde voor `ledenadministratie@eacdesperwers.nl`.
3. Zet beide sleutels in `data/site.yml` onder `web3forms` (of via **/admin → Instellingen → Algemene gegevens**).

Proefles en contact gaan naar info@, lid worden en opzeggen naar ledenadministratie@. Zonder sleutel openen de formulieren een e-mail.
Gratis: 250 berichten per maand; Web3Forms bewaart berichten 30 dagen.

## Agenda en nieuws bijwerken

1. Ga naar `eacdesperwers.nl/admin/` en log in met GitHub.
2. Kies **Agenda** of **Nieuws** → **Nieuw**, vul de velden in en klik op **Opslaan**.
3. Na ongeveer een minuut staat de wijziging op de site.

Activiteiten met **Tonen in de carrousel** aan verschijnen op de homepage zolang de datum nog niet voorbij is.
