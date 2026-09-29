Привет! Это перенос проекта из Cowork. Прочитай по порядку: CLAUDE.md, docs/internal/00_HANDOFF.md,
docs/01_TALK.md, docs/03_METHODOLOGY.md, docs/06_BACKLOG.md, talk/deck_text_and_notes.md,
docs/internal/05_REVIEW_FINDINGS.md. Общаемся по-русски, всё в репозитории — по-английски.

Цель: довести до полноценного публичного репозитория всё, что обещано в абстракте доклада
(конвейер от сырых данных до каждой фигуры и каждого числа со слайдов), исправив фактические ошибки v1.

План на эту сессию:
1. Проверь окружение: `pip install -e ".[dev]" && pytest -q` (юнит-тесты ядра должны пройти, golden — skip).
2. Если в `talk/` есть pptx — запусти `make deck` и сверь слайды с talk/deck_text_and_notes.md.
3. Помоги мне найти legacy-код с прошлой Cowork-сессии (HANDOFF §2) — дай команды, я выполню или разреши тебе.
4. Задай мне вопросы из HANDOFF §3 («для Маши заполнить») и из пунктов [DECIDE] в методологии — одним списком.
5. Инициализируй git, создай репо на GitHub (сначала private), заведи issues через `scripts/create_github_issues.sh --dry-run`, покажи мне, потом без --dry-run.
6. Начни M1 (UK): fetch ODWP01EW/WU01EW + MSOA, clean, и воспроизведи 0.103 / 0.506 / 0.093.
После каждого воспроизведённого числа обнови outputs/tables/golden_actual.yaml и статус в tests/golden_values.yaml.
Если число не сходится — не подгоняй параметры, покажи мне расхождение.
