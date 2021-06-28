# observer

[![forthebadge](https://forthebadge.com/images/badges/powered-by-black-magic.svg)](https://forthebadge.com) 

## Что это?

Это программа и набор вспомогательных скриптов на языке Python для анализа датасетов

## Зачем это было сделано?

### Какая стояла задача

Стояла задача поиска и анализа различных датасетов для распознавания объектов на изображении. В ходе анализа требовалось вычислить различные метрики, касающиеся каждого из датасетов.

### Что сложного в задаче

- Данные (т.е. объекты и аннотации к ним) в датасетах могут быть организованы очень по-разному. Поэтому нельзя просто взять и написать один универсальный скрипт и скармливать ему любой датасет
- Датасеты могут лежать на диске как в формате изображений (.jpg, .png и т.п.), так и в формате видео (.mp4, .avi и т.п.). Было бы хорошо, если бы можно было не задумываться об этом
- В ходе анализа и экспериментов, вероятно, придется добавлять новые метрики и изменять старые, и хотелось бы, чтобы это выглядело как, например, просто написание функции, принимающей на вход изображение и возвращающей результат
- Датасеты, как правило, содержат десятки и сотни тысяч изображений, поэтому следует использовать возможности распараллеливания вычислений, а также как можно меньше обращаться к диску (это,  вообще, узкое место в таких задачах)
- Было бы удобно иметь возможность выводить вычисленные метрики (особенно графики) в jupyter notebook для визуального анализа
- Также очень полезно иметь возможность просмотреть примеры изображений, относящихся к той или иной части графика (гистограммы)

## Как это было сделано

Итак, задача -- подсчет значений метрик по заданному датасету.

Вот как в результате выглядит решение с точки зрения пользователя (пример для датасета FER-2013):

```shell
python parse_dataset.py --input /path/to/dataset/fer2013 --api fer2013
python get_metrics.py --dataset fer2013 --api fer2013 --threads 16
python on_flow.py --dataset fer2013 --api fer2013 --threads 16
```

А теперь обо всем по порядку.

### parse_dataset.py

Этот скрипт находит в заданной папке объекты и аннотации к ним, связывает их и записывает результат в формате JSON файлов в папку pairs_*имя датасета* (по умолчанию). Имя датасета по умолчанию -- имя заданной папки.

Т.е. предполагается, что **датасет лежит выделенной специально под него папке**. Соответственно первое, что делает скрипт -- это получает список файлов в этой папке. Для этого используется **функция `getFiles`  из файла files.py**. 

Далее, необходимо выделить из этих файлов объекты, т.е. сущности, к которым в дальнейшем будут привязываться аннотации. На данный момент observer поддерживает два типа объектов:

- изображения (например, файлы с расширением .jpg)
- кадры (например, 121-ый кадр в файле с расширением .avi)

Для этого используется **класс `Objects` из файла objects.py**. Список расширений интересующих файлов специфичен для каждого отдельного датасета, поэтому вынесен в отдельный файл -- **API датасета, который хранится в папке dataset_specific_apis**.

Когда известны объекты, скрипт связывает их с аннотациями. Этот процесс состоит из следующих этапов:

1. Получение данных, необходимых для поиска аннотаций. Для этого используется **функция `getAnnotationsData`, описанная в API датасета**
2. Получение аннотации для каждого отдельного объекта. Для этого используется **функция `getAnnotations`, описанная в API датасета**. Помимо самого объекта этой функции передается результат работы функции `getAnnotationsData`, т.е. данные, необходимые для поиска аннотаций
3. Если `getAnnotations` вернула хотя бы одну аннотацию (непустой список), данные об объекте записываются в JSON файл с именем, соответствующим порядковому номеру объекта

#### `getFiles`, описание файла

Функция `getFiles` описана в файле files.py. Функция принимает путь к папке и возвращает список описаний файлов, находящихся в этой папке. Пример описания файла:

```python
{
    'name': 'PrivateTest_88305'
    'extension': 'jpg',
    'dir': '..\\fer2013\\test\\angry
}
```

#### `Objects`

Конструктор класса `Objects` принимает 2 аргумента:

- Список описаний файлов (см. главу "`getFiles`, описание файла")
- Список расширений интересующих файлов

В рамках конструктора список описаний файлов фильтруется так, чтобы остались только файлы интересующих расширений. Затем к каждому из оставшихся файлов применяется метод `getObjects` класса `Objects`. Эта функция, в зависимости от расширения файла, возвращает либо описание объекта-изображения, либо итератор по описаниям объектов-кадров. Результаты работы `getObjects` соединяются в единый итератор, который фактически и используется при итерации по объекту класса `Objects`.

Пример описания объекта-изображения:

```python
{
    "type": "image",
    "name": "PrivateTest_10131363",
    "extension": "jpg",
    "dir": "..\\fer2013\\test\\angry"
}
```

Пример описания объекта-кадра:

```python
{
    "type": "frame",
 	"number": 12,
    "name": "1-30-1280x720",
    "extension": "mp4",
    "dir": "..\\aff-wild2\\expr\\videos\\train_set"
}
```



#### `Frames`

**Класс `Frames` описан в файле objects.py**. Конструктор этого класса принимает один аргумент -- путь к видеофайлу. При итерации по объекту класса Frames последовательно возвращаются описания объектов-кадров из заданного в конструкторе видеофайла.

#### dataset_specific_apis

Папка dataset_specific_apis содержит API к датасетам. API к датасету -- это скрипт на языке Python, содержащий определения следующих функций:

- `getClasses`. Принимает описание пары объект-аннотация и возвращает список классов, к которым принадлежит объект.
- `getAnnotationsData`. Принимает список описаний файлов. Возвращаемое значение будет подано в функцию `getAnnotations`
- `getAnnotations`. Принимает описание объекта, а также (в рамках parse_dataset.py) результат работы функции `getAnnotationsData`. Возвращает список аннотаций к объекту

Пример аннотации:

```python
{
	"emotion": "Happiness"
}
```

Фактически, аннотация может содержать любые поля с любыми значениями, единственное условие -- сериализируемость значений в формат JSON. Т.е., например, функция не может быть полем, потому что ее нельзя (встроенными средствами) сериализовать в формат JSON.

Для работы с API датасетов можно использовать функции из файла dataset_specific_api.py:

- `getDatasetSpecificApi`. Принимает один обязательный аргумент -- имя файла с API. Возвращает объект-модуль API. Например, если имя этого объекта `api`, то соответствующая функция для получения аннотаций к объекту -- `api.getAnnotations`. У `getDatasetSpecificApi` есть также один необязательный аргумент -- `splited_by_frames`. Его соответствие `False` (по умолчанию) или `True` указывает, выполняется ли работа с изначальным датасетом, или с конвертированным с разбиением видео на кадры с помощью videos_expander.py
- `getAnnotationsSplitedDecorator`. Используется для конвертации функции getAnnotations в вариант, учитывающий, что датасет был конвертирован с разбиением видео на кадры

#### videos_expander.py

Скрипт videos_expander.py предназначен для конвертации датасетов с разбиением видео на кадры. Под датасетом здесь подразумевается заданная входная директория (`--input_dir`). Скрипт создает заданную выходную директорию (`--output_dir`), содержимое которой идентично содержимому входной за исключением видеофайлов: вместо них папки с соответствующими именами, содержащие файлы-кадры (изображения), с именами \_\_frame\_\__номер кадра_. Скрипт поддерживает многопоточную обработку файлов, которая как правило сильно ускоряет конвертацию (`--threads`).

### get_metrics.py

Этот скрипт подсчитывает метрики для объектов, JSON-описания которых находятся в заданной папке и записывает обновленные (содержащие значения метрик) JSON-описания в папку pairs\_*имя датасета*\_new (по умолчанию).

Для работы с JSON-описаниями объектов (итерации по ним, фильтрации) используется **класс `Pairs` из файла pairs.py**. `Pairs` -- потому что JSON-описания состоят из указателя на объект и списка аннотаций, т.е. это *пары* объект-аннотации.

Метрики задаются **в словаре `metrics` в файле default_metrics.py**. Ключ -- имя метрики, значение -- функция, принимающая на вход изображение (numpy-массив) и возвращающая значение метрики. **Метрики можно указать в любом другом файле**, главное поместить его в директорию observer-а и указать его имя (без расширения) в ключе `--metrics_file` команды `python get_metrics.py`

Для вычисления метрик используется **функция `calculateMetricsForImages` из файла filters.py**. Ее обязательные аргументы:

- объект класса `Pairs`, по которому она будет итерироваться
- словарь с метриками (см. предыдущий абзац)
- путь к папке, в которую надо записывать обновленные JSON-описания

#### `Pairs`

Класс `Pairs` описан в файле pairs.py. Он используется для итерации по JSON-описаниям объектов, а также содержит методы для их фильтрации.

Пример JSON-описания объекта (пара):

```python
{
    "object": {
        "type": "frame",
        "number": 12,
        "name": "1-30-1280x720",
        "extension": "mp4",
        "dir": "..\\aff-wild2\\expr\\videos\\train_set"
    },
    "annotations": [
        {
            "emotion": "Happiness"
        }
    ]
}
```



Его конструктор принимает следующие аргументы:

- путь к директории, в которой находятся JSON-описания объектов
- ограничение на кол-во JSON-описаний (например, 10 означает что после 10-ой итерации итерирование прервется (raise StopIteration))
- функция для получения списка классов, к которым относится заданный объект (должна быть определена в API датасета как `getClasses`)

Класс `Pairs` поддерживает итерацию и доступ по индексу ([]).

Для фильтрации необходимо вначале создать индексы фильтров с помощью метода `dumpFiltersIndexes`. Метод принимает 2 аргумента:

- список обобщенных фильтров (см. главу "Обобщенные фильтры, компиляция обобщенных фильтров в обычные")
- флаг (`True`/`False`) `overwrite` (по умолчанию `True`), указывающий, следует ли перезаписать файл с индексами

Затем можно выполнить фильтрацию с помощью метода `filterBy`, принимающего в качестве аргумента фильтр (см. главу "Фильтры"). Метод загрузит индекс, соответствующий объектам, которые проходят указанный фильтр, после чего при итерации по этому объекту класса Pairs будут возвращаться только объекты, прошедшие фильтр. Т.е. непосредственно фильтрация происходит в методе `dumpFiltersIndexes`, в методе `filterBy` происходит только подгрузка результатов.

#### filters.py

Файл filters.py содержит функции, с помощью которых выполняется подсчет метрик по объектам. Основной функцией является `calculateMetricsForImages`. Ее аргументы:

- объект класса pairs, по которому будет выполняться итерирование
- список метрик
- путь к директории, в которую будут записываться обновленные JSON-описания объектов
- `threads` -- количество потоков (по умолчанию `1`)
- `overwrite` -- флаг, указывающий, нужно ли перезаписывать результаты вычисления метрик (соответствующие поля аннотации) (по умолчанию `False`)

Функция выполняет вычисление метрик и записывает обновленные JSON-описания объектов  на диск.

Функция `calculateMetricsForImages` использует функцию `calculateMetricsForImage`, описанную в том же файле. Она принимает следующие аргументы:

- пара, состоящая из номера объекта (имени файла JSON-описания) и JSON-описания объекта
- список метрик
- путь к директории, в которую будет записано обновленное JSON-описание объекта
- флаг, указывающий, нужно ли перезаписывать результаты вычисления метрик (соответствующие поля аннотации)

### on_flow.py

#### `onFlowMetric`

В предыдущей главе описано, как устроено получение метрик, касающихся каждого отдельного объекта. Такими метриками могут быть, например, констрастость изображения или HOG. Однако таких метрик недостаточно, т.к. они не описывают датасет в целом. Что, если мне нужна не контрастность каждого отдельного изображения, а ее среднее значение или гистограмма? Для этого был создан другой, более высокоуровневый вид метрик -- поточные метрики. Они **описываются классом `OnFlowMetric` из файла on_flow_metrics.py**.

Почему поточные? Дело в том, что иногда нет возможности держать в памяти все данные, необходимые для подсчета метрики. Реальный пример -- распределение попарных косинусных расстояний между HOG-векторами. Т.е. каждому изображению соответствует вектор, и нужно построить гистограмму попарных расстояний между такими векторами. Эти расстояния можно считать по разному -- по одному, порциями, возможно, как-то еще.  Проблема в том, что для реальных датасетов, состоящих из сотен тысяч изображений, невозможно держать в памяти все эти расстояния сразу. Выход -- генерировать и подавать на обработку не сразу все данные (расстояния). Действительно, чтобы посчитать распределение некоторой величины, не обязательно знать сразу все ее значения, можно получать их порциями и обновлять результат.

Итак, класс `OnFlowMetric` описывает как раз такую метрику, вычисление которой не требует сразу всех данных -- их можно подавать порциями, и значение метрики будет обновляться с каждой порцией. Любая такая метрика может быть описана тремя сущностями:

1. Начальное значение
2. Обновляющая функция, т.е. функция, которая получает на вход новые данные, имеет доступ к текущему значению и возвращает новое текущее значение
3. Возвращающая функция, т.е. функция, которая имеет доступ к текущему значению (1) и возвращает значение, соответствующее смыслу метрики (2). Пример разницы между (1) и (2): для метрики, соответствующей среднему, (1) содержит сумму поступивших чисел и кол-во поступивших чисел, а (2) является частным этой суммы и этого кол-ва

Именно эти сущности (и еще имя метрики), являются аргументами конструктора класса OnFlowMetric.

#### Задачи (`tasks`)

Однако, вернемся к нашему примеру -- распределению попарных косинусных расстояний между HOG-векторами. Очевидно, что поточных метрик недостаточно для описания этой задачи. Ведь надо еще указать, что нам интересны именно HOG-векторы, что для подсчета попарных расстояний между ними надо использовать такую-то функцию, и подавать данные в нее такими-то порциями (иначе результат ее работы не поместится в памяти). Только уже результат работы этой функции можно подавать в потоковую метрику. В итоге описание этой задачи будет выглядеть так:

```python
{
	'name': 'HOG cosine distances mean and distribution',
	'initial_metric': 'hog',
	'batcher': unziped_batches,
	'batch_size': 30000,
	'preprocessing': [getCosineDistanceMatrix],
	'on_flow_metrics': [mean_on_flow(None), ndim_unnormed_distribution_on_flow(0.1)],
}
```

Под ключом 'name', разумеется, хранится имя задачи. Под ключом `'initial_metric'` -- имя метрики, которую нужно взять из JSON-описаний объектов для начала вычислений. `'batcher'` -- итератор, который будет использоваться для подачи данных (значений метрики `'hog'` в данном случае) порциями. Данные будут последовательно обрабатываться функциями из списка `'preprocessing'`, результаты обработки будут подаваться на каждую из поточных метрик из списка `on_flow_metrics` в отдельности.

Итератор `unziped_batches` работает следующим образом (пример):

- Входной объект: `[(1, 10), (2, 20), (3, 30)]`. Размер порции: 2
- Результат первой итерации: `([1, 2], [10, 20])`
- Результат второй итерации: `([3], [30])`

Такой хитрый итератор нужен для удобного проброса идентификаторов объектов. Проброс нужен для записи примеров объектов, соответствующих тому или иному столбцу гистограммы.

Для предобработки в этой задаче используется функция `getCosineDistanceMatrix`. Она принимает на вход массив векторов одинаковой размерности и возвращает матрицу косинусных расстояний между ними.

Касательно использованных в этой задаче поточных метрик:

- `mean_on_flow(None)` -- считает среднее значение. None, если коротко, означает, что мы считаем среднее число, а не вектор (чтобы посчитать средний вектор, надо написать 0 вместо None)
- `ndim_unnormed_distribution_on_flow(0.1)` -- считает распределение с шагом 0.1. Может работать как данными любых ненулевых размерностей (в данном случае матрица размерности 2)

По умолчанию такие задачи хранятся **в списке `tasks` в файле default_tasks.py**. **Задачи можно указать в любом другом файле**, главное поместить его в директорию observer-а и указать его имя (без расширения) в ключе `--tasks_file` команды `python on_flow.py`.

#### Фильтры

Однако, даже такого высокоуровневого понятия, как задача, недостаточно. Действительно, ведь мы нигде не указываем, применительно к каким данным мы выполняем все эти вычисления. Короче -- из каких объектов мы достаем значения метрик 'hog'. А ведь хотелось бы выполнить эту задачу для каждого класса по отдельности, например. Для этой цели используется понятие фильтра.

Сразу пример: фильтр, пропускающий только объекты классов 'happy' и 'neutral' с контрастностью в пределах от 0.01 до 0.05 или от 0.10 до 0.15 выглядит так:

```python
{
	'__class__': ['happy', 'neutral'],
	'contrast': [{'from': 0.01, 'to': 0.05}, {'from': 0.10, 'to': 0.15}]
}
```

Т.е. можно указать множество классов, к одному из которых должен принадлежать объект и множество значений каких-либо других полей, находящихся в аннотации к нему, при этом множество значений задается как множество отрезков. Чтобы указать точку, можно написать просто значение, т.е. если нам еще интересны объекты с контрастностью 0.07, то фильтр будет такой:

```python
{
	'__class__': ['happy', 'neutral'],
	'contrast': [{'from': 0.01, 'to': 0.05}, {'from': 0.10, 'to': 0.15}, 0.07]
}
```

#### Обобщенные фильтры, компиляция обобщенных фильтров в обычные

И вот, казалось бы, есть все инструменты для удобного анализа: и задачи, и фильтры. Но забавная ситуация может возникнуть, если в датасете штук 40 классов, и мы хотим выполнить задачи для каждого из 10 интервалов контрастностей для каждого из классов. Получается, нам надо написать 40 * 10 = 400 фильтров! Чтобы не заниматься такой ерундой, был сделан механизм компиляции фильтров, позволяющий легко описать такой "букет". Нескомпилированные фильтры будем называть обобщенными.

Принцип работы комбинаторный: пишем множество значений каждого из полей, после компиляции получаем множество фильтров-комбинаций этих значений. Простой пример:

Обобщенный фильтр:

```python
{
	'__class__': [
		['happy', 'neutral'],
		['sad', 'neutral']
	],
	'contrast': [
		[{'from': 0.01, 'to': 0.05}, {'from': 0.10, 'to': 0.15}],
		[{'from': 0.03, 'to': 0.08}, {'from': 0.13, 'to': 0.18}]
	]
}
```

Результат компиляции (список фильтров):

```python
[
	{
		'__class__': ['happy', 'neutral'],
		'contrast': [{'from': 0.01, 'to': 0.05}, {'from': 0.10, 'to': 0.15}]
	},
	{
		'__class__': ['sad', 'neutral'],
		'contrast': [{'from': 0.03, 'to': 0.08}, {'from': 0.13, 'to': 0.18}]
	},
	{
		'__class__': ['happy', 'neutral'],
		'contrast': [{'from': 0.03, 'to': 0.08}, {'from': 0.13, 'to': 0.18}]
	},
	{
		'__class__': ['sad', 'neutral'],
		'contrast': [{'from': 0.01, 'to': 0.05}, {'from': 0.10, 'to': 0.15}]
	}
]
```

По умолчанию список таких обобщенных фильтров возвращает **функция `filters`, определенная в файле default_filters.py**. **Обобщенные фильтры можно указать в любом другом файле**, главное поместить его в директорию observer-а и указать его имя (без расширения) в ключе `--filters_file` команды `python on_flow.py`.

#### `calculateOnFlowForFilters`

Функция, которая вычисляет и сохраняет результаты выполнения задач для фильтров -- **`calculateOnFlowForFilters` из файла on_flow.py**. Ее аргументы:

- объект класса `Pairs`, по которому будет выполняться итерирование
- список обобщенных фильтров
- список задач
- имя файла, в который будут записываться результаты
- количество потоков
- максимальное количество примеров объектов для столбца гистограммы
- уровень логирования: 0 -- без логирования, 1 -- логирование прогресса выполнения задач, 2 -- самое подробное логирование, включая прогресс подгрузки новых начальных метрик и обновление распределений

#### `"values_to_load"`, использование результатов одних задач для выполнения других

И все же, есть метрики, которые не удастся посчитать (адекватным способом), используя только описанные выше средства. Простейший пример: гистограмма отклонений от средней гистограммы интенсивностей. Ясно, как подсчитать среднюю гистограмму. Ясно, как достать гистограммы каждого из изображений. Однако как достать для подсчета отклонений среднюю гистограмму? Для таких целей в описание задач было включено опциональное поле "values_to_load" и реализован хитрый механизм, использующий метапрограммирование.

Для пользователя суть проста: в описании задачи можно указать список имен задач, результаты выполнения которых будут нужны в функциях предобработки:

```python
{
	...
	'values_to_load': ['mean_histogram'],
	...
}
```

И затем можно использовать эти результаты:

```python
{
	...
	'values_to_load': ['mean_histogram'],
	'preprocessing': [lambda batch: np.array(list(map(lambda h: np.linalg.norm(h - mean_histogram[0]['value']), batch)))],
	...
}
```

`mean_histogram[0]['value']` -- это значение первой потоковой метрики в результатах выполнения задачи 'mean_histogram'.

Внутри это работает так:

1. Из результатов уже выполненных задач берутся результаты, соответствующие задачам с перечисленными именами
2. Взятые результаты используются как (фейковые) глобальные переменные с соответствующими именами для функций-предобработчиков

### presenter.py, показ результатов

В файле presenter.py реализовано несколько функций для показа результатов вычислений метрик по датасету. Пример использования этих функций:

```python
from presenter import * # Подключение скрипта, отвечающиго за извлечение вычисленных данных о датасетах
dataset_name = 'FMDDS_resized' # Имя датасета для извлечения вычисленных данных
api = 'FMDDS' # имя набора специфичных для датасета функций

# Общее количество объектов, классов и распределение объектов по классам
# vertical -- флаг, указывающий, вертикальные столбцы должны быть в гистограмме (True) или горизонтальные (False)
datasetClasses(dataset_name, vertical=False)

# Примеры изображений из каждого из классов
datasetClassesExampleImages(dataset_name, 5, api=api)

# Примеры изображений из разных кластеров
# 'kmeans clastering' -- это имя задачи (из списка tasks)
datasetMetrics(dataset_name, 'kmeans clastering', log_plots=True, examples_amount=5, api=api)

# Распределение по контрастности внутри каждого из классов
datasetMetrics(dataset_name, 'contrast mean and distribution', log_plots=False, api=api)

# Распределение по отношению ширины к высоте внутри каждого из классов
datasetMetrics(dataset_name, 'width to height ratios mean and distribution (instant version)', log_plots=False, api=api)

# Средняя гистограмма интенсивностей
datasetMetrics(dataset_name, 'mean_histogram', log_plots=False, api=api)

# Отклонение от средней гистограммы интенсивностей
datasetMetrics(dataset_name, 'deviation from mean histogram', log_plots=False, vertical=True, api=api)
```

Предполагается, что показ результатов будет осуществляться в рамках jupyter-ноутбука.

### Вспомогательный инструмент: images_resizer.py

Скрипт images_resizer.py аналогичен скрипту videos_expander.py. Он предназначен для конвертации датасетов с уменьшением размера (разрешения) изображений, размер которых превышает заданный (`--max_width`, `--max_height`). Под датасетом здесь подразумевается заданная входная директория (`--input_dir`). Скрипт создает заданную выходную директорию (`--output_dir`), содержимое которой идентично содержимому входной за исключением изображений, размер которых превышает заданный: их размер минимально уменьшен так, чтобы не превышать заданный. Скрипт поддерживает многопоточную обработку файлов, которая как правило сильно ускоряет конвертацию (`--threads`).
