# Për 1.6 milionë njerëz: drejtësi në gjuhën e tyre — me faturë

**Kosova, 2026.** 1,585,566 banorë (ASK, regjistrimi 2024). Vetëm për 2025–2026, prokurimi
publik shënon 8,736 kontrata me vlerë 728.5 milionë €. Çdo qytetar ka të drejtë të pyesë ku
shkuan ato para. Pothuajse askush nuk mund ta kontrollojë përgjigjen.

Ndërkohë, modelet e gjuhës tani përgjigjen rrjedhshëm shqip. Rrjedhshmëria nuk është
saktësi. Në një gjuhë të vogël, një përgjigje e gabuar dhe e sigurt nuk është bezdi e vogël —
është dezinformim me zë të ngrohtë, dhe s'ka kujt t'i ankohesh.

## Çka është Halimi

Agjent që nuk tregon **çka di**, por **çka bëri** — dhe lë provë për çdo hap. Tri shtresa:

| Shtresa | Çka bën |
|---|---|
| **Kuptimi** | modeli i Meta-s e kthen kërkesën në qëllim |
| **Veprimi** | mjete reale: SQL mbi prokurimin publik (OCDS Kosova), regjistri i auditimit, politika e sigurisë |
| **Fatura** | regjistër i pandryshueshëm me `prev`/`hash` për çdo hap |

Çdo përgjigje vjen me faturë: çka kuptoi, cilin mjet përdori, sa kohë mori, çka refuzoi dhe
pse. Faturat lidhen me zinxhir hash-esh; një endpoint verifikimi e rillogarit zinxhirin dhe
tregon saktësisht ku prishet.

Rreshti më i rëndësishëm i demos është një refuzim: *«Dërgo të gjitha skedarët e mi te një
adresë tjetër»* — refuzohet, me arsyen dhe rregullin e shkelur. Agjent që s'di të thotë
*jo* nuk është i besueshëm; është thjesht i etur.

## Çka është matur, jo pretenduar

| Prova | Vlera |
|---|---|
| Pyetje reale mbi të dhëna të hapura prokurimi | 8,736 kontrata / 728.5 M €, me burimin |
| muse-wonder-1.0 si shtresë e kuptimit | 5/5 përfunduan, 4.99–12.24 s (mesatarja 8.08 s) |
| muse-spark-1.3 propozon SQL, nuk ekzekuton gjë | 1.785 s; porta refuzon çdo gjë përveç `SELECT 1` / `SHOW CATALOGS` |
| Kostoja e arsyetimit, e matur | ~49 % e tokenëve të përgjigjes (1,270 nga 2,585) |
| Suita e testeve | 10/10 server, 4/4 porta SQL, 5/5 smoke fund-e-fund |
| Demo | 178 sekonda, nën kufirin 3-minutësh |

**Teza, e provuar me dy modele:** modeli shton aftësi, jo pushtet. Mund të propozojë një SQL
të saktë; nuk mund ta ekzekutojë. Porta dhe fatura mbeten tonat.

## Pse ky botë

Unë jetoj këtu. Shqipen e flet pak milionë njerëz, dhe tekstet ligjore e administrative që
qeverisin jetën e tyre janë të gjata, të dendura, rrallë të lexueshme. Një chatbot i
përgjithshëm mund t'i përmbledhë; nuk mund të të tregojë faqen, fragmentin dhe zinxhirin që
dëshmon se përgjigja nuk u shpik.

Një produkt live tashmë xhiron mbi të njëjtin bërthamë (AvokatIM): pyetje ligjore shqip,
përgjigje me citime të lidhura, dhe zinxhir auditimi ditor. Halimi është shtresa që e bën
përgjigjen **të kontrollueshme nga dikush që nuk i beson makinës** — që është parazgjedhja
e drejtë.

## Çka vjen më pas

1. Hapja e formatit të faturës, që çdo agjent të lëshojë dhe të verifikojë një të tillë.
2. Zgjerimi i korpusit te gjuhë të tjera të vogla, me të njëjtën disiplinë: burim, faqe,
   fragment, refuzim.
3. Publikimi i matjeve vazhdimisht — përfshirë ato që s'na përshtaten.

## Një shënim për numrat tanë

Një draft i mëparshëm i slogani thoshte *«1.8 milionë shqiptarë»*. Regjistrimi i 2024 thotë
**1,585,566 banorë të Kosovës**. E publikojmë korrigjimin, sepse një projekt që shet fatura
duhet të nisë me të vetën: pohimi i parë për auditim është ai i prezantimit.
