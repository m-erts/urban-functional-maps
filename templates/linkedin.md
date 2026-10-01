# LinkedIn announcement

Rendered from `templates/linkedin.md`; the numbers come from the pipeline. Plain text, as it is pasted into LinkedIn (no markdown). Under 3,000 characters with hashtags. Image: `docs/figures/uk_trap3_three_maps.png` (the four maps answer the hook). The repository link can move to the first comment; the post reads without it. Hook alternatives are at the end.

## English

Same census. Same algorithm. Same parameters as the official Travel to Work Areas. {{uk_lma_areas_2011}} labour-market areas, or {{uk_lma_ons_areas_2011}}.
The difference is where you count {{uk_ons_added_2011/1e6:.1f}} million people who work at home or have no fixed workplace.

For FOSS4G 2026 in Hiroshima I prepared a second talk: which open mobility data can you trust for functional-area maps? I couldn't give it for health reasons, so I am publishing everything: code, paper, slides. The first draft lacked the standard algorithm, a proper null model and a third country. All three are in now.

What it found:

1️⃣ Coding. The 2021 census of England and Wales puts {{uk_home_2021/1e6:.1f}}M people who work at home on the diagonal of the commuting matrix. The share of people working in their own unit jumps from {{uk_diag_2021_clean:.3f}} to {{uk_diag_2021_naive:.3f}}. The file gives no warning; the code list does.

2️⃣ Most of the score is not the algorithm. Self-containment = scale + contiguity + placement. Scale has a closed form, d + (1 − d)·h. Contiguity comes from a recombination chain on spanning trees. Across {{dec_partitions}} maps of England and Wales, the Netherlands and Spain, placement, the part that depends on where the boundaries run, is {{dec_placement_min:.2f}} to {{dec_placement_max:.2f}}.

3️⃣ No construction wins everywhere. Coombes-Bond (R package LabourMarketAreas) places boundaries best in Spain, ties in the Netherlands and trails a simple heuristic in England and Wales.

4️⃣ Old regions can be tested. On 2023 municipal pairs, {{nl23_corop_valid_share*100:.0f}} % of the Dutch COROP regions designed in 1970 pass the TTWA validity rule.

5️⃣ Spain publishes pairs, purpose AND the hour in one open file: {{es_trips_home_work/1e6:.1f}}M trips a day from home to work or study, peaking at {{es_commute_peak_hour:02d}}:00.

The trap: comparing raw self-containment across unit systems. For British districts the random baseline alone is {{uk_district_null_share_clean*100:.0f}} % of the score.

Every number in the paper and the slides is written by the pipeline and checked by tests. Code, paper and slides: https://github.com/m-erts/urban-functional-maps

Question for people who build labour-market areas: where does your pipeline put people who work from home?

#FOSS4G2026 #FOSS4G #OSGeo #GIS #Geospatial #SpatialDataScience #OpenData #Census #Mobility #MAUP #LabourMarketAreas #Reproducibility

Hook alternatives:

- Your commuting matrix has {{uk_home_2021/1e6:.1f}} million people on its diagonal who never commute. / The 2021 census of England and Wales put them there, and the file does not say so.
- The official Travel to Work Areas of 2011: {{uk_ttwa_official_touching_ew_2011}}. The same algorithm on the open matrix: {{uk_lma_areas_2011}}. / Here is where the other areas went.

## Русский

Та же перепись. Тот же алгоритм. Те же параметры, что у официальных Travel to Work Areas. {{uk_lma_areas_2011}} ареалов рынка труда или {{uk_lma_ons_areas_2011}}.
Разница в том, где посчитать {{uk_ons_added_2011/1e6:.1f}} млн человек, которые работают из дома или без постоянного места работы.

Для FOSS4G 2026 в Хиросиме я подготовила второй доклад: каким открытым данным о мобильности можно доверять при построении функциональных ареалов. Выступить я не смогла из-за здоровья, поэтому публикую всё целиком: код, статью и слайды. В первой версии не хватало стандартного алгоритма, корректной нуль-модели и третьей страны. Теперь всё это есть.

Что получилось:

1️⃣ Кодировка. Перепись Англии и Уэльса 2021 года ставит {{uk_home_2021/1e6:.1f}} млн человек, работающих из дома, на диагональ матрицы поездок. Доля работающих в своей единице растёт с {{uk_diag_2021_clean:.3f}} до {{uk_diag_2021_naive:.3f}}. Файл об этом не предупреждает, справочник кодов предупреждает.

2️⃣ Большая часть оценки не зависит от алгоритма. Самодостаточность = масштаб + смежность + размещение. Для масштаба есть формула, d + (1 − d)·h. Смежность даёт цепь рекомбинации на остовных деревьях. На {{dec_partitions}} картах Англии и Уэльса, Нидерландов и Испании размещение, то есть часть, которая зависит от положения границ, составляет от {{dec_placement_min:.2f}} до {{dec_placement_max:.2f}}.

3️⃣ Нет конструкции, которая выигрывает везде. Алгоритм Кумбса и Бонда (R-пакет LabourMarketAreas) лучше всех размещает границы в Испании, наравне с эвристикой в Нидерландах и уступает ей в Англии и Уэльсе.

4️⃣ Старые регионы можно проверить. На парах муниципалитетов 2023 года правилу валидности TTWA отвечают {{nl23_corop_valid_share*100:.0f}} % регионов COROP, спроектированных в 1970 году.

5️⃣ Испания публикует пары, цель поездки И час в одном открытом файле: {{es_trips_home_work/1e6:.1f}} млн поездок в день из дома на работу или учёбу, пик в {{es_commute_peak_hour:02d}}:00.

Ловушка: сравнивать самодостаточность на разных сетках единиц. Для британских районов случайная нарезка сама по себе даёт {{uk_district_null_share_clean*100:.0f}} % оценки.

Каждое число в статье и на слайдах записывает конвейер, и его проверяют тесты. Код, статья и слайды: https://github.com/m-erts/urban-functional-maps

Вопрос к тем, кто строит ареалы рынков труда: куда ваш конвейер ставит людей, которые работают из дома?

#FOSS4G2026 #FOSS4G #OSGeo #GIS #Geospatial #SpatialDataScience #OpenData #Census #Mobility #MAUP #LabourMarketAreas #Reproducibility
