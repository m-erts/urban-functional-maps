# LinkedIn announcement

Rendered from `templates/linkedin.md`; the numbers come from the pipeline. Two versions: English, and Russian for a Russian-speaking audience. Attach `docs/figures/uk_decomposition.png` as the image.

## English

On 3 September I gave a talk at FOSS4G 2026 in Hiroshima on open mobility data for functional-area maps. The code, the paper and the corrected slides are now public.

The question: when you draw labour-market areas from open data, how much of the map is the data, how much the zoning, and how much the algorithm?

Four results, all reproducible from the repository.

1. One category of a code list. The 2021 census of England and Wales codes {{uk_home_2021/1e6:.1f}} million people who work at home with workplace = residence. Leave them in the matrix and local working rises from {{uk_diag_2021_clean:.3f}} to {{uk_diag_2021_naive:.3f}}. The file format gives no warning.

2. Why a plain overlay misleads. Self-containment, the usual score of a functional area, grows with the size of the areas. Under random relabelling of units its expected value is d + (1 − d)·h, where d is the share of flows that never leave their unit and h is the concentration of area sizes. At district level this null gives {{uk_district_null_share_clean*100:.0f}} % of the score. At neighbourhood level, {{uk_null_share_msoa_2021*100:.0f}} %.

3. Contiguity does most of the rest. Of the {{uk_own_sc_2021:.3f}} scored by {{uk_areas_flows_only_2021}} areas on {{uk_msoa_n:,}} units, {{uk_own_from_scale_2021:.2f}} is scale, {{uk_own_from_contiguity_2021:.2f}} is what any contiguous zoning of those sizes holds, and {{uk_own_from_placement_2021:.2f}} is the position of the boundaries. For the official Travel to Work Areas the last part is {{uk_official_from_placement_2021:.2f}}. Algorithms should be compared on that part.

4. A similar count of areas is not a similar map. {{uk_areas_flows_only_2011}} delimited areas against {{uk_ttwa_official_touching_ew_2011}} official ones agree at an adjusted Rand index of {{uk_ari_contiguous_2011:.2f}}. Enforcing the published validity rule lowers it to {{uk_ari_ttwa_greedy_2011:.2f}}. Agreement is measured with an error matrix counted in employed residents, with intersection over union per official area.

The same audit covers Serbian census bands, Dutch register pairs, the Japanese people-flow panel and OpenStreetMap GPS traces. In the slides of the talk it found {{deck_corrected}} of {{deck_numbers}} numbers to correct; the list is in the repository.

What the pipeline does: reads each source with its code list, reconciles with published totals, delimits, repairs contiguity, runs both nulls, builds the error matrix, and writes every number that the paper and the slides then print.

Repository: https://github.com/m-erts/urban-functional-maps
Paper: https://github.com/m-erts/urban-functional-maps/blob/main/docs/paper/paper.md

Code MIT, text and figures CC BY 4.0. Data: ONS, SORS, CBS, MLIT, JRC, © OpenStreetMap contributors, Overture Maps Foundation.

#FOSS4G #GIS #OpenData #UrbanAnalytics #MAUP #Reproducibility

## Русский

3 сентября я выступала на FOSS4G 2026 в Хиросиме с докладом об открытых данных о мобильности для карт функциональных ареалов. Код, статья и исправленные слайды теперь в открытом доступе.

Вопрос: когда мы рисуем ареалы рынков труда по открытым данным, какая часть карты получена из данных, какая из нарезки территории, какая из алгоритма?

Четыре результата. Все воспроизводятся из репозитория.

1. Одна строка в справочнике кодов. В переписи Англии и Уэльса 2021 года {{uk_home_2021/1e6:.1f}} млн человек, работающих из дома, записаны с местом работы, равным месту жительства. Если оставить их в матрице, доля работающих в своей единице растёт с {{uk_diag_2021_clean:.3f}} до {{uk_diag_2021_naive:.3f}}. Формат файла об этом не предупреждает.

2. Почему простое наложение вводит в заблуждение. Самодостаточность, обычная оценка функционального ареала, растёт с размером ареалов. При случайной перестановке меток её ожидание равно d + (1 − d)·h, где d это доля потоков, не покидающих свою единицу, а h это концентрация размеров ареалов. На уровне районов эта нуль-модель даёт {{uk_district_null_share_clean*100:.0f}} % оценки. На уровне кварталов {{uk_null_share_msoa_2021*100:.0f}} %.

3. Большую часть остального даёт смежность. Из {{uk_own_sc_2021:.3f}}, которые набирают {{uk_areas_flows_only_2021}} ареалов на {{uk_msoa_n:,}} единицах, {{uk_own_from_scale_2021:.2f}} приходится на масштаб, {{uk_own_from_contiguity_2021:.2f}} на любую связную нарезку тех же размеров и {{uk_own_from_placement_2021:.2f}} на положение границ. У официальных Travel to Work Areas последняя часть равна {{uk_official_from_placement_2021:.2f}}. Сравнивать алгоритмы нужно по ней.

4. Близкое число ареалов не означает близкую карту. {{uk_areas_flows_only_2011}} построенных ареалов и {{uk_ttwa_official_touching_ew_2011}} официальных согласуются на уровне скорректированного индекса Рэнда {{uk_ari_contiguous_2011:.2f}}. После применения опубликованного правила валидности он падает до {{uk_ari_ttwa_greedy_2011:.2f}}. Согласие измеряется матрицей ошибок в занятых жителях и пересечением по объединению (IoU) для каждого официального ареала.

Та же проверка сделана для сербской переписи, нидерландского регистра, японской панели присутствия и GPS-треков OpenStreetMap. В слайдах доклада она нашла {{deck_corrected}} чисел из {{deck_numbers}}, которые нужно исправить. Список лежит в репозитории.

Репозиторий: https://github.com/m-erts/urban-functional-maps
Статья: https://github.com/m-erts/urban-functional-maps/blob/main/docs/paper/paper.md

Код MIT, текст и рисунки CC BY 4.0.
