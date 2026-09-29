# Критический разбор деки v1 (Cowork, до выступления)

> Написан по v1 (17 слайдов) до доклада 3 сентября. Факты проверены по первоисточникам (ссылки внизу и в `docs/02_DATA_SOURCES.md`).
> Задачи из разбора разложены в `docs/06_BACKLOG.md`. Номера слайдов — по v1.

**Вердикт.** Каркас сильный и редкий по жанру: «честность как метод», три ловушки, каждая из которых убила собственный результат. Но в деке три фактические мины (одна — про Японию при японской аудитории), структурная дыра размером с Испанию, и главный визуальный долг: слайд про «континуум вместо кластеров» не показывает континуум.

## 1. Три фактические мины (P0)

### 1.1 MLIT people-flow — не NTT docomo и, строго говоря, не MNO
«(NTT docomo)» и «aggregated anonymised MNO» — на слайдах 2, 4, 12, 15 и в notes. Проверка:
- G空間情報センター (mlit-1km-fromto): исходник — данные **株式会社Agoop** (SoftBank group) с коэффициентами расширения Agoop.
- Urban Data Challenge: «提供元：国土交通省、株式会社Agoop».
- MLIT пресс-страница: «携帯電話端末等の位置情報データ» — позиционные данные устройств, не сетевые данные оператора.
- Продукт Agoop «流動人口データ» — GPS-логи смартфонных приложений (панель), расширенные до населения; не モバイル空間統計 docomo (базовые станции). См. e-Stat bigdata №130 vs №126.
Почему важно: японская аудитория; ошибка атрибуции — ровно тот тип ошибки, против которого доклад; app-GPS панель и MNO имеют разные смещения.
Фикс: сверить с データ定義書; «MLIT people-flow (app-GPS, Agoop/SoftBank, expanded to population)»; добавить измерение «кто в выборке». Формулировка для сл. 12: «Japan's flagship open people-flow is not MNO at all — it is a smartphone-app GPS panel, expanded to population. The clock is real; the sample is not "everyone with a SIM".»

### 1.2 «A standard without data» / «only Japan publishes the clock» — опровергается Испанией
MITMA/MITMS «Estudio de movilidad con Big Data»: v1 14.02.2020–09.05.2021, v2 с 01.01.2022 по сей день; почасовая детализация; district/municipality/GAU; свободно; R-пакет spanishoddata; Kotov et al. 2026 (EPB B). Плюс INE EM-1…EM-4.
Фиксы: сл. 2 карточка 1 — «Multi-MNO: standard shipped, EU-wide data not yet. National products exist — Spain publishes hourly MNO OD weekly (MITMA); Japan ships the open people-flow panel I use here.» Футер сл. 4 — «Spain and Japan publish the clock — nobody publishes all three». Сл. 15 строка 2 — «MNO/app-derived products (ES MITMA hourly OD today · JP MLIT 2019–21 · Eurostat Multi-MNO next)».
Новый панчлайн: **«Europe wrote the standard, Spain shipped the data, Japan shipped the clock I could join to a census — and none of the three is what its label says.»**
Подарки FOSS4G-аудитории: референс-пайплайн Eurostat — open source (github.com/eurostat/multimno), проект Multi-MNO завершён в 06/2025, преемник MNO-MINDS. Бэкап-слайд Madrid day/night из MITMA восстановил бы европейскую ногу.

### 1.3 Японская перепись публикует полные пары
e-Stat, таблица 6-1 «従業・通学市区町村，男女別通勤者・通学者数» (常住地×従業地); на этих потоках — 都市雇用圏 (Kanemoto & Tokuoka). «Bands only» верно для файла MLIT From-To, но не для переписи.
Фикс: «(Serbia; Japan's MLIT product — its census does publish pairs)»; вслух: «your census gives pairs, your people-flow gives the clock; Japan is the one country in my sample that has both dimensions».

## 2. Логика и содержание

**2.1 Сл. 6 (Trap 1): нет слова «lockdown».** День переписи 21.03.2021, до 5,6 млн на furlough; ONS: «a mixture of pandemic and pre-pandemic travel behaviours», рекомендует продолжать использовать TTWA-2011. «The workforce split instead» — структурное утверждение на снапшоте локдауна; 15,1 млн fixed-workplace — не случайная подвыборка (key workers). Механика диагонали подтверждена дословно ONS user guide: «The usual residents who do not have a fixed place to work or work at or from home have been counted at their usual residence as place of work» (в 2011 — отдельные коды OD0000001/3). Фиксы: подпись «census day = 21 March 2021, mid-lockdown»; «what exploded is who has a fixed workplace on census day»; выровнять «category 1» (notes) vs «1 и 3» (слайд).

**2.2 Сл. 8 (Trap 3): «the algorithm is the moat» — преувеличение.** Coombes–Bond описан открыто (Newcastle/ONS отчёт), EU-адаптация реализована в R-пакете LabourMarketAreas (Istat, EU-TTWA). Честный тезис: опубликованное описание ≠ запускаемый код; production-реализация ONS (порядок слияний, tie-breaking) не опубликована. Формулировка: «The criterion is open; the production code is not. A published description is not a runnable artefact.» + строка про LMA как next step; идеально — прогнать LMA и показать три карты. Для «several parameter sets hit ≈230 with different maps» — триптих миниатюр.

**2.3 Сл. 3 (OSM vs Overture): корреляция не доказывает вывод.** ρ показывает совместную концентрацию, люди тоже ходят там, где POI. Решающий тест: ρ(traces, MLIT daytime) vs ρ(traces, Overture) в Хиросиме. Ещё: «200k pts» = потолок пагинации (5000 × 40) — сказать; путь `api.openstreetmap.org/api/0.6/trackpoints` (пропущен /api); «Three city windows» vs две карты, «2.4–10k unique minutes» не сходится с 2 395 и 5 695; «two campaigns (2019, 2026)» расшифровать; атрибуция © OpenStreetMap contributors (ODbL) и Overture.

**2.4 Сл. 11 (NL): «discontinued after 2014» неверно.** 81252NED закрыт, но есть 83628NED (2014–2020) и действующий 85481NED — всё ещё региональные. Формулировка: «the table closed in 2014; its successors run to today — in the same 40-region cage». «2 functional areas» подать как артефакт разрешения (Trap 2 в чистом виде), как нули на сл. 10.

**2.5 Сл. 4: «a sixth kind».** В ISO 19157 есть элемент usability / fitness for use. Инверсия: «Five ISO 19157 elements are computable and pass. The sixth — usability, fitness for a stated purpose — is the one nobody computes. My whole talk is element six.» «4 distance bands» → «nested administrative rings». ODiN — «открытая поставка», не микроданные.

**2.6 Сл. 10: +0.08 vs 0.65−0.53=0.12.** Подписать «median of per-municipality gaps». «RBSC» на колорбаре сл. 9 не расшифрован.

**2.7 Сл. 14:** «IDENTICAL» vs «±0.3 %» → «identical to within ±0.3 %»; население Японии −~0.7 % за 2019–21 — нормализация доказана. Добавить третий кавеат: **панель** (кто вне app-GPS панели, 拡大係数 Agoop).

**2.8 Сл. 2/15: Европа полна муниципальных OD.** FR MOBPRO (commune→commune, 2022), DE BA Pendlerstatistik, JP census, AT регистровая матрица. «EU Census Hub at NUTS-2» для делимитации бесполезен. Фикс строки 1: «census/register OD pairs (UK, FR MOBPRO, DE BA, JP census; EU Hub only at NUTS-2 — too coarse to delimit)».

**2.9 Несоответствие абстракту.** Urban Atlas (нет, вместо GHS-SMOD), DEGURBA, intraday (только day/night), UMAP (убран), OSRM, QGIS. Добавить на сл. 2 строку «Also renegotiated since spring: Urban Atlas→GHS-SMOD, intraday→day/night, HDBSCAN→thresholds, UMAP→dropped». OSRM — вернуть или убрать из заявленных.

## 3. Научная база
Lenormand et al. 2014 (cross-checking mobility sources); Ratti et al. 2010 (redrawing GB map); Reades et al. 2007; Toole et al. 2012; Ahas et al.; Ricciato et al. (Eurostat); Openshaw 1984, Fotheringham & Wong 1991 (MAUP); Adolfsson et al. 2019 + Hopkins; Chari & Pachter 2023 (против UMAP); Neis & Zipf 2012; Zielstra & Hochmair; Nielsen 90-9-1; Pendler Mobil (AStA); SORS «Дневне миграције» 07/2024.
Редакционно: «Kosovo excluded» / «a 587 km² Kosovo polygon wearing Belgrade data» → «Census 2022 does not cover Kosovo*» (UNSCR 1244) и «an unmatched polygon silently inherited another unit's values».

## 4. Визуализация по слайдам
- 1: поднять контраст нижних строк.
- 2: полупустые карточки; жирнить вердикты.
- 3: нет легенды пурпурной шкалы; мелкие подписи; нет атрибуции; ρ крупно на картах.
- 4: панчлайн-футер поднять в полноразмерную строку; красным подсветить «жертву» в каждой строке.
- 5: шрифты matplotlib ≠ дека; аннотацию про Бристоль в текст; «my own 2-rule delimitation, not the TTWA algorithm».
- 7: нет error bars по 60 прогонам; добавить district-пару (0.961/0.798); подпись оси; метафора «bigger boxes catch more balls by chance».
- 8: визуал для «≈230 with different maps».
- 9: расшифровать RBSC; красно-зелёная шкала → blue–orange/purple–green; 8 артефактов — контуром; Kosovo*.
- 10: **overflow текста в карточке 2**; +0.08 vs 0.12.
- 12: карты разного размера/масштаба; ключ крупно; назвать Naka-ku, реки/вокзал; «come from outside by day».
- 13: **главная дыра — добавить скаттер log₂(day/night) × log₂(holiday/weekday) с порогами 1.5× и словесными квадрантами**; легенду с карты наружу; Hopkins; перебор min_cluster_size.
- 14: пустая нижняя половина → третий кавеат «panel».
- 15: правки строк 1–2 (фотографируемый слайд).
- 16: подтянуть текст к заголовкам; код под MIT, не CC BY; репо **до** доклада + QR.
- 17: QR на репо/слайды.
Сквозное: низкоконтрастные серые футеры; проверить дейтеранопию (сл. 9, 13).

## 5. Нарратив и тайминг
- OSM-нить обрывается после сл. 3 — эхо в финале («the bright line was one logger»).
- «Urban Function Maps» vs 8/17 слайдов про labour-market delimitation — связка «functional areas are the where of urban function; temporal signatures are the when».
- Бюджет ≈21:45 на 17 слайдов — перебор. Сжать сл. 5 до 30 с, сл. 11 — flex, сл. 14 — 40 с. Чек-пойнты: сл. 6 к 8:00, сл. 12 к 14:00, сл. 15 к 18:00.

## 6. Вопросы из зала (заготовки)
Испания/MITMA · Agoop vs docomo · JP census pairs · lockdown census · Coombes–Bond опубликован / LMA · «HDBSCAN не настроили» (sweep, Hopkins, Adolfsson) · почему не Strava/Google/Meta (закрыты/прекращены; критерий «anyone can re-run tonight») · кто в панели Agoop · NL после 2014 · Kosovo* (нейтральная формула).

## 7. Про старые комментарии
Нумерация в них по другой версии деки. Уже исправлено: Trap 1 отделён от карты; матрица цветокодирована. В силе: перегруз, log₂, метафора null-модели. Пункт «фамилия → Канагина» противоречит pretalx/заявке — решать Маше, начиная с профиля программы. Панчлайн «добро пожаловать в Японию» фактически неверен — заменён (1.2).
