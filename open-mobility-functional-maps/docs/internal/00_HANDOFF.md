# HANDOFF: перенос проекта из Cowork в Claude Code

Составлено 2026-09-29 из контекста чата Cowork (критический разбор деки FOSS4G talk 2).
Для Маши и для Claude Code. Публичные документы репозитория — на английском, этот — внутренний.

---

## 1. Что есть и откуда

| Артефакт | Где сейчас | Статус |
|---|---|---|
| Дека v1 `1787944295594_FOSS4G_talk2_EurostatOSMCensus.pptx` (17 слайдов, speaker notes) | у Маши локально (загружалась в чат); облачная копия удалена вместе с контейнером | **положить в `talk/FOSS4G2026_talk2_v1.pptx`** |
| Полный текст слайдов + notes | `talk/deck_text_and_notes.md` (восстановлен дословно) | ✅ |
| Критический разбор (RU) | `docs/internal/05_REVIEW_FINDINGS.md` (+ файл `FOSS4G2026_critical_review.md`, отправленный в чат) | ✅ |
| Рендер слайдов, картинки из деки | не сохранились → `python scripts/extract_deck.py talk/FOSS4G2026_talk2_v1.pptx` | ⏳ после п.1 |
| **Исходный код анализа** | писался в прошлой Cowork-сессии; пути в деке: `/sessions/practical-upbeat-brown/mnt/outputs/deck2_assets/{osm_overture,uk_areas,rs_selfcont,jp_daynight,jp_signatures}.png` | ❓ **скорее всего утерян** (scratch-папка Cowork эфемерна) — см. §2 |
| Параметры методов | `config/params.yaml` (все, что названо на слайдах) | ✅ |
| Все числа со сцены | `docs/04_RESULTS_REGISTER.md`, `tests/golden_values.yaml` | ✅ |
| Источники данных + лицензии | `docs/02_DATA_SOURCES.md`, `data/manifest.yaml` | ✅ (URL-ы уточнить при fetch) |
| Литература | `docs/07_LITERATURE.md`, `docs/references.bib` | ✅ |
| Бэклог | `docs/06_BACKLOG.md` + `scripts/create_github_issues.sh` | ✅ |

## 2. Первый шаг: найти оригинальный код (15 минут, экономит дни)

Поищи на Mac всё, что осталось от прошлой сессии:
```bash
mdfind -name deck2_assets; mdfind -name osm_overture.png; mdfind -name jp_signatures
mdfind "kMDItemFSName == '*.py' && kMDItemFSContentChangeDate >= \$time.iso(2026-08-01)" | grep -iv library
find ~ -name "*.py" -newermt 2026-08-01 -not -path "*/Library/*" 2>/dev/null | head -50
find ~ \( -name "*ODWP*" -o -name "*WU01EW*" -o -name "*81252*" -o -name "*mesh1km*" -o -name "*popis*" \) 2>/dev/null
```
Также проверь: папку Downloads, папки, которые были подключены к Cowork в августе, и
историю Cowork-сессии «practical-upbeat-brown» в приложении (если там код приходил файлами —
скачай). Если найдётся — положи в `legacy/` без правок, первым коммитом («import legacy code as-is»),
потом рефакторинг в `src/omfm/`. Если нет — строим заново по `docs/03_METHODOLOGY.md`;
golden values покажут, воспроизвелось ли.

Имя `deck2_assets` / файл `talk2` → был и talk 1. Если его пайплайн пересекается — решить, один
репозиторий или два (см. §4).

## 3. Контекст доклада (для README и proceedings)

- **FOSS4G 2026 Hiroshima**, 30.08–05.09.2026; доклад 3.09, 14:00–14:30 (07:00–07:30 Europe/Belgrade), Room 2, без микрофона.
- Уровень: 2 — intermediate. Лицензия вклада: **CC BY 4.0** (абстракт, текст для proceedings, слайды, видео).
- Автор: **Marija Ercegovac** — Senior Geospatial Analyst, Rockup; URBAN_MASH (2,200+).
  ⚠️ В старых комментариях был пункт «сменить фамилию на Канагина» — противоречит pretalx и заявке. Решить Маше; в репо пока Ercegovac.
- Полный абстракт и био: `docs/01_TALK.md`.
- Обещано в абстракте vs. сделано к v1: см. `docs/01_TALK.md` §«Promise ledger». Незакрытое: Urban Atlas, DEGURBA-классификация на Urban Atlas, intraday-профили (данные только day/night), UMAP (сознательно убран), OSRM, QGIS-ready layers, Docker/conda.
- **Для Маши заполнить** (Claude спросит): что спрашивали в Q&A 3 сентября; какие P0-правки из разбора успела внести до выступления; есть ли запись/видео; опубликованы ли слайды на pretalx.

## 4. Стратегия GitHub: «не только финальное отображение, а все репозитории»

Рекомендация — **монорепо** `open-mobility-functional-maps` (этот каркас), в нём всё:
код по источникам, анализ, фигуры, дека, разбор, бэклог, тесты. Причины: одна среда, один
DOI (Zenodo), golden values проверяют весь путь данные→слайд.

Опционально позже:
- `omfm-talk-foss4g2026` — только слайды/видео/proceedings (или GitHub Pages из `talk/`);
- если talk 1 — отдельный проект, отдельный репо, общие утилиты вынести в пакет.

Публиковать ли `docs/internal/` (разбор на русском, заметки)? По умолчанию — да, в ветке
`main` это честный «making-of», в духе доклада. Если нет — перенести в приватный репо/ветку
до первого push.

## 5. Порядок работ (детально — `docs/06_BACKLOG.md`)

0. Положить pptx, запустить `scripts/extract_deck.py`, найти legacy-код (§2).
1. `make env` + Dockerfile, CI (GitHub Actions: lint + unit tests без данных).
2. UK: fetch ODWP01EW/WU01EW + MSOA → self-containment, null model, delimitation, TTWA rule → слайды 5–8.
3. Serbia: SORS daily migrations + GHSL → слайды 9–10.
4. NL: CBS 81252NED (+ 83628NED/85481NED) → слайд 11.
5. Japan: MLIT 人流 (Hiroshima) → слайды 12–14; континуум-скаттер, Hopkins.
6. OSM traces + Overture (Belgrade, Hiroshima) → слайд 3; тест ρ(traces, MLIT) vs ρ(traces, Overture).
7. **Новое:** Spain MITMA (Madrid day/night) — европейская нога MNO.
8. Обещанное в абстракте: Urban Atlas + DEGURBA, OSRM, QGIS-проект, PostGIS-экспорт.
9. Дека v2 с правками P0/P1, README, Zenodo DOI, релиз v1.0.

## 6. Как стартовать в Claude Code
```bash
cd ~/Projects && unzip open-mobility-functional-maps.zip && cd open-mobility-functional-maps
cp ~/Downloads/1787944295594_FOSS4G_talk2_EurostatOSMCensus.pptx talk/FOSS4G2026_talk2_v1.pptx
git init && git add -A && git commit -m "Scaffold from Cowork handoff"
gh repo create open-mobility-functional-maps --public --source=. --push   # или --private до релиза
claude
```
Первое сообщение — содержимое `KICKOFF_PROMPT.md`.
