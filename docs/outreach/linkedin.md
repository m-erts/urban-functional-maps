# LinkedIn announcement

Rendered from `templates/linkedin.md`; the numbers come from the pipeline. Plain text, as it is pasted into LinkedIn (no markdown). Under 3,000 characters with hashtags. Image: `docs/figures/uk_trap3_three_maps.png` (the four maps answer the hook). The repository link can move to the first comment; the post reads without it. Hook alternatives are at the end.

## English

Same census. Same algorithm. Same parameters as the official Travel to Work Areas. 59 labour-market areas, or 95.
The difference is where you count 5.0 million people who work at home or have no fixed workplace.

For FOSS4G 2026 in Hiroshima I prepared a second talk: which open mobility data can you trust for functional-area maps? The session was cancelled, so I am publishing everything: code, paper, slides. The first draft lacked the standard algorithm, a proper null model and a third country. All three are in now.

What it found:

1️⃣ Coding. The 2021 census of England and Wales puts 12.6M people who work at home on the diagonal of the commuting matrix. The share of people working in their own unit jumps from 0.093 to 0.506. The file gives no warning; the code list does.

2️⃣ Most of the score is not the algorithm. Self-containment = scale + contiguity + placement. Scale has a closed form, d + (1 − d)·h. Contiguity comes from a recombination chain on spanning trees. Across 11 maps of England and Wales, the Netherlands and Spain, placement, the part that depends on where the boundaries run, is 0.06 to 0.22.

3️⃣ No construction wins everywhere. Coombes-Bond (R package LabourMarketAreas) places boundaries best in Spain, ties in the Netherlands and trails a simple heuristic in England and Wales.

4️⃣ Old regions can be tested. On 2023 municipal pairs, 45 % of the Dutch COROP regions designed in 1970 pass the TTWA validity rule.

5️⃣ Spain publishes pairs, purpose AND the hour in one open file: 11.3M trips a day from home to work or study, peaking at 07:00.

The trap: comparing raw self-containment across unit systems. For British districts the random baseline alone is 69 % of the score.

Every number in the paper and the slides is written by the pipeline and checked by tests. Code, paper and slides: https://github.com/m-erts/urban-functional-maps

Question for people who build labour-market areas: where does your pipeline put people who work from home?

#FOSS4G2026 #FOSS4G #OSGeo #GIS #Geospatial #SpatialDataScience #OpenData #Census #Mobility #MAUP #LabourMarketAreas #Reproducibility

Hook alternatives:

- Your commuting matrix has 12.6 million people on its diagonal who never commute. / The 2021 census of England and Wales put them there, and the file does not say so.
- The official Travel to Work Areas of 2011: 173. The same algorithm on the open matrix: 59. / Here is where the other areas went.

## Русский

Та же перепись. Тот же алгоритм. Те же параметры, что у официальных Travel to Work Areas. 59 ареалов рынка труда или 95.
Разница в том, где посчитать 5.0 млн человек, которые работают из дома или без постоянного места работы.

Для FOSS4G 2026 в Хиросиме я подготовила второй доклад: каким открытым данным о мобильности можно доверять при построении функциональных ареалов. Сессию отменили, поэтому публикую всё целиком: код, статью и слайды. В первой версии не хватало стандартного алгоритма, корректной нуль-модели и третьей страны. Теперь всё это есть.

Что получилось:

1️⃣ Кодировка. Перепись Англии и Уэльса 2021 года ставит 12.6 млн человек, работающих из дома, на диагональ матрицы поездок. Доля работающих в своей единице растёт с 0.093 до 0.506. Файл об этом не предупреждает, справочник кодов предупреждает.

2️⃣ Большая часть оценки не зависит от алгоритма. Самодостаточность = масштаб + смежность + размещение. Для масштаба есть формула, d + (1 − d)·h. Смежность даёт цепь рекомбинации на остовных деревьях. На 11 картах Англии и Уэльса, Нидерландов и Испании размещение, то есть часть, которая зависит от положения границ, составляет от 0.06 до 0.22.

3️⃣ Нет конструкции, которая выигрывает везде. Алгоритм Кумбса и Бонда (R-пакет LabourMarketAreas) лучше всех размещает границы в Испании, наравне с эвристикой в Нидерландах и уступает ей в Англии и Уэльсе.

4️⃣ Старые регионы можно проверить. На парах муниципалитетов 2023 года правилу валидности TTWA отвечают 45 % регионов COROP, спроектированных в 1970 году.

5️⃣ Испания публикует пары, цель поездки И час в одном открытом файле: 11.3 млн поездок в день из дома на работу или учёбу, пик в 07:00.

Ловушка: сравнивать самодостаточность на разных сетках единиц. Для британских районов случайная нарезка сама по себе даёт 69 % оценки.

Каждое число в статье и на слайдах записывает конвейер, и его проверяют тесты. Код, статья и слайды: https://github.com/m-erts/urban-functional-maps

Вопрос к тем, кто строит ареалы рынков труда: куда ваш конвейер ставит людей, которые работают из дома?

#FOSS4G2026 #FOSS4G #OSGeo #GIS #Geospatial #SpatialDataScience #OpenData #Census #Mobility #MAUP #LabourMarketAreas #Reproducibility
