# LinkedIn announcement

Rendered from `templates/linkedin.md`; the numbers come from the pipeline. Two versions: English, and Russian for a Russian-speaking audience. Attach `docs/figures/uk_decomposition.png` as the image.

## English

For FOSS4G 2026 in Hiroshima I prepared a talk on open mobility data for functional-area maps. The session was cancelled, so I am publishing the material in full: code, paper and slides.

The question: when you draw labour-market areas from open data, how much of the map is the data, how much the zoning, and how much the algorithm?

Four results, all reproducible from the repository.

1. One category of a code list. The 2021 census of England and Wales codes 12.6 million people who work at home with workplace = residence. Leave them in the matrix and local working rises from 0.093 to 0.506. The file format gives no warning.

2. Why a plain overlay misleads. Self-containment, the usual score of a functional area, grows with the size of the areas. Under random relabelling of units its expected value is d + (1 − d)·h, where d is the share of flows that never leave their unit and h is the concentration of area sizes. At district level this null gives 69 % of the score. At neighbourhood level, 19 %.

3. Contiguity does most of the rest. Of the 0.696 scored by 235 areas on 7,264 units, 0.13 is scale, 0.43 is what any contiguous zoning of those sizes holds, and 0.13 is the position of the boundaries. For the official Travel to Work Areas the last part is 0.19. Algorithms should be compared on that part.

4. A similar count of areas is not a similar map. 197 delimited areas against 173 official ones agree at an adjusted Rand index of 0.54. Enforcing the published validity rule lowers it to 0.46. Agreement is measured with an error matrix counted in employed residents, with intersection over union per official area.

The same audit covers Serbian census bands, Dutch register pairs, the Japanese people-flow panel and OpenStreetMap GPS traces. In the first version of the slides it found 10 of 56 numbers to correct; the list is in the repository.

What the pipeline does: reads each source with its code list, reconciles with published totals, delimits, repairs contiguity, runs both nulls, builds the error matrix, and writes every number that the paper and the slides then print.

Repository: https://github.com/m-erts/urban-functional-maps
Paper: https://github.com/m-erts/urban-functional-maps/blob/main/docs/paper/paper.md

Code MIT, text and figures CC BY 4.0. Data: ONS, SORS, CBS, MLIT, JRC, © OpenStreetMap contributors, Overture Maps Foundation.

#FOSS4G #GIS #OpenData #UrbanAnalytics #MAUP #Reproducibility

## Русский

Для FOSS4G 2026 в Хиросиме я подготовила доклад об открытых данных о мобильности для карт функциональных ареалов. Сессию отменили, поэтому публикую материал целиком: код, статью и слайды.

Вопрос: когда мы рисуем ареалы рынков труда по открытым данным, какая часть карты получена из данных, какая из нарезки территории, какая из алгоритма?

Четыре результата. Все воспроизводятся из репозитория.

1. Одна строка в справочнике кодов. В переписи Англии и Уэльса 2021 года 12.6 млн человек, работающих из дома, записаны с местом работы, равным месту жительства. Если оставить их в матрице, доля работающих в своей единице растёт с 0.093 до 0.506. Формат файла об этом не предупреждает.

2. Почему простое наложение вводит в заблуждение. Самодостаточность, обычная оценка функционального ареала, растёт с размером ареалов. При случайной перестановке меток её ожидание равно d + (1 − d)·h, где d это доля потоков, не покидающих свою единицу, а h это концентрация размеров ареалов. На уровне районов эта нуль-модель даёт 69 % оценки. На уровне кварталов 19 %.

3. Большую часть остального даёт смежность. Из 0.696, которые набирают 235 ареалов на 7,264 единицах, 0.13 приходится на масштаб, 0.43 на любую связную нарезку тех же размеров и 0.13 на положение границ. У официальных Travel to Work Areas последняя часть равна 0.19. Сравнивать алгоритмы нужно по ней.

4. Близкое число ареалов не означает близкую карту. 197 построенных ареалов и 173 официальных согласуются на уровне скорректированного индекса Рэнда 0.54. После применения опубликованного правила валидности он падает до 0.46. Согласие измеряется матрицей ошибок в занятых жителях и пересечением по объединению (IoU) для каждого официального ареала.

Та же проверка сделана для сербской переписи, нидерландского регистра, японской панели присутствия и GPS-треков OpenStreetMap. В первой версии слайдов она нашла 10 чисел из 56, которые нужно исправить. Список лежит в репозитории.

Репозиторий: https://github.com/m-erts/urban-functional-maps
Статья: https://github.com/m-erts/urban-functional-maps/blob/main/docs/paper/paper.md

Код MIT, текст и рисунки CC BY 4.0.
