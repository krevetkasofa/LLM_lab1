# Лабораторная работа №1

## Методология

Baseline (3 прогона) и первый прогон "с контекстом" выполнены в **Codex CLI**. Второй прогон "с контекстом" и generalization-прогон выполнены в **Claude Code**.

## Задача 1: пороги уверенности

### Промпт
```
Добавь возможность настраивать пороги уверенности для компонентов pipeline.
Пользователь должен иметь возможность задавать:
- минимальную confidence для детекции автомобиля;
- минимальную confidence для object detection;
- минимальную confidence для результатов классификации сцены.
Должны быть разумные значения по умолчанию, чтобы существующий способ вызова run_pipeline() продолжал работать без изменений.
Некорректные значения должны обрабатываться явно.
Добавь необходимые тесты.
Реализуй задачу в соответствии с существующей архитектурой проекта.
```

### Конвенции
| № | Конвенция | Автоматическая проверка |
|---|---|---|
| R1 | `main.py` используется только для оркестрации pipeline и не загружает ML-модели напрямую | AST-проверка запрещает в `main.py` прямые импорты `torch`, `transformers`, `ultralytics`, `torchvision`, а также прямую инициализацию и загрузку моделей |
| R2 | `main.py` использует компоненты проекта только через публичный API пакета `autocaption` | Проверяются импорты вида `from autocaption.<internal_module> import ...`; такие импорты считаются нарушением |
| R3 | Компоненты, импортируемые через публичный API `autocaption`, должны быть объявлены в `autocaption.__all__` | AST-проверка сопоставляет импорты из `autocaption` с содержимым `__all__` в `autocaption/__init__.py` |
| R4 | Пакет `autocaption` является самодостаточным и не зависит от вспомогательных Python-модулей, расположенных в корне проекта | Проверяются импорты внутри `autocaption/*.py`; импорт вспомогательного модуля из корня проекта считается нарушением |
| R5 | Тяжёлые pipeline-компоненты и ML-модели создаются один раз до цикла обработки изображений | AST-проверка выявляет создание `ImageRotator`, `CarDetector`, `ObjectExtractor`, `SceneExtractor`, `PhotoDescriber` и других тяжёлых компонентов внутри циклов |
| R6 | Логика загрузки изображений по локальному пути или URL централизована в `autocaption/image_loader.py` | Проверяется использование `requests.get()` и `Image.open()` вне `image_loader.py` |
| R7 | Локальные файлы моделей и весов загружаются из каталога `MODELS/` | Проверяются локальные пути, передаваемые в `torch.load(...)`, `YOLO(...)` и другие операции загрузки моделей |

## Baseline (без контекста, 3 прогона)
### Сравнение веток
**Скрипт для анализа изменений:**
```
for branch in baseline-1 baseline-2 baseline-3; do
  echo "===== $branch ====="
  git diff --stat lab-start...$branch
  echo "--- changed files ---"
  git diff --name-only lab-start...$branch
  echo
done
```
**Результат скрипта:**
```
===== baseline-1 =====
 README.md                        | 14 ++++++++++++--
 autocaption/feature_extractor.py | 27 ++++++++++++++++++---------
 autocaption/image_processor.py   | 13 ++++++++++---
 confidence.py                    | 13 +++++++++++++
 main.py                          | 30 +++++++++++++++++++++++++-----
 tests/conftest.py                | 25 +++++++++++++++++++++++++
 tests/test_feature_extractor.py  | 70 ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
 tests/test_image_processor.py    | 36 ++++++++++++++++++++++++++++++++----
 tests/test_pipeline.py           | 61 ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++---
 9 files changed, 263 insertions(+), 26 deletions(-)
--- changed files ---
README.md
autocaption/feature_extractor.py
autocaption/image_processor.py
confidence.py
main.py
tests/conftest.py
tests/test_feature_extractor.py
tests/test_image_processor.py
tests/test_pipeline.py

===== baseline-2 =====
 README.md                        | 11 ++++++++++-
 autocaption/confidence.py        | 17 +++++++++++++++++
 autocaption/feature_extractor.py | 23 ++++++++++++++++-------
 autocaption/image_processor.py   | 11 ++++++++---
 main.py                          | 27 ++++++++++++++++++++++-----
 tests/conftest.py                | 29 ++++++++++++++++++++++++++++-
 tests/test_feature_extractor.py  | 68 ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
 tests/test_image_processor.py    | 45 +++++++++++++++++++++++++++++++++++++++++----
 tests/test_pipeline.py           | 52 ++++++++++++++++++++++++++++++++++++++++++++++++----
 9 files changed, 258 insertions(+), 25 deletions(-)
--- changed files ---
README.md
autocaption/confidence.py
autocaption/feature_extractor.py
autocaption/image_processor.py
main.py
tests/conftest.py
tests/test_feature_extractor.py
tests/test_image_processor.py
tests/test_pipeline.py

===== baseline-3 =====
 README.md                        |  9 ++++++++-
 autocaption/feature_extractor.py | 15 ++++++++++-----
 autocaption/image_processor.py   |  8 +++++---
 confidence.py                    | 10 ++++++++++
 main.py                          | 25 ++++++++++++++++++++-----
 tests/conftest.py                |  1 +
 tests/test_feature_extractor.py  | 73 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
 tests/test_image_processor.py    | 37 +++++++++++++++++++++++++++++++++----
 tests/test_pipeline.py           | 56 ++++++++++++++++++++++++++++++++++++++++++++++++++------
 9 files changed, 210 insertions(+), 24 deletions(-)
--- changed files ---
README.md
autocaption/feature_extractor.py
autocaption/image_processor.py
confidence.py
main.py
tests/conftest.py
tests/test_feature_extractor.py
tests/test_image_processor.py
tests/test_pipeline.py
```

### Нарушение конвенций
| Прогон       | Нарушения | Что произошло                                                                                                                               |
| ------------ | --------: | ------------------------------------------------------------------------------------------------------------------------------------------- |
| `baseline-1` |     **3** | `main.py` импортирует корневой `confidence.py`; ещё `feature_extractor.py` и `image_processor.py` зависят от этого helper вне `autocaption` |
| `baseline-2` |     **1** | helper помещён внутрь `autocaption`, но `main.py` обходит публичный API через `from autocaption.confidence import ...`                      |
| `baseline-3` |     **3** | практически та же архитектурная ошибка, что и в baseline-1                                                                                  |      

#### Нарушение конвенций baseline-1
```
========================================================================
[R1] PASS - main.py is orchestration-only (no direct ML framework/model loading)
[R2] FAIL (1) - main.py uses project code only through the public autocaption API
      main.py:3: imports project-root helper 'confidence' instead of public autocaption API
[R3] PASS - symbols imported from autocaption are declared in autocaption.__all__
[R4] FAIL (2) - autocaption is self-contained and does not import project-root helpers
      autocaption/feature_extractor.py:13: package module imports project-root helper 'confidence'; keep shared pipeline code inside autocaption
      autocaption/image_processor.py:5: package module imports project-root helper 'confidence'; keep shared pipeline code inside autocaption
[R5] PASS - heavy pipeline components are initialized outside image-processing loops
[R6] PASS - new image path/URL loading goes through ImageLoader (legacy direct loads are allowlisted)
[R7] PASS - local model files are loaded from MODELS/
========================================================================
Violations: 3
```
#### Нарушение конвенций baseline-2
```
Convention check
========================================================================
[R1] PASS - main.py is orchestration-only (no direct ML framework/model loading)
[R2] FAIL (1) - main.py uses project code only through the public autocaption API
      main.py:3: bypasses public API with 'from autocaption.confidence import ...'
[R3] PASS - symbols imported from autocaption are declared in autocaption.__all__
[R4] PASS - autocaption is self-contained and does not import project-root helpers
[R5] PASS - heavy pipeline components are initialized outside image-processing loops
[R6] PASS - new image path/URL loading goes through ImageLoader (legacy direct loads are allowlisted)
[R7] PASS - local model files are loaded from MODELS/
========================================================================
Violations: 1
```
#### Нарушение конвенций baseline-3
```
Convention check
========================================================================
[R1] PASS - main.py is orchestration-only (no direct ML framework/model loading)
[R2] FAIL (1) - main.py uses project code only through the public autocaption API
      main.py:3: imports project-root helper 'confidence' instead of public autocaption API
[R3] PASS - symbols imported from autocaption are declared in autocaption.__all__
[R4] FAIL (2) - autocaption is self-contained and does not import project-root helpers
      autocaption/feature_extractor.py:13: package module imports project-root helper 'confidence'; keep shared pipeline code inside autocaption
      autocaption/image_processor.py:5: package module imports project-root helper 'confidence'; keep shared pipeline code inside autocaption
[R5] PASS - heavy pipeline components are initialized outside image-processing loops
[R6] PASS - new image path/URL loading goes through ImageLoader (legacy direct loads are allowlisted)
[R7] PASS - local model files are loaded from MODELS/
========================================================================
Violations: 3
```

### Какие ошибки агент совершал изначально

Ошибка была одна и та же, менялась только форма:

- В baseline-1 и baseline-3 агент выносил новый файл `confidence.py` в корень проекта, и на него ссылались и `main.py`, и модули внутри `autocaption` - нарушение R4 (пакет должен быть самодостаточным) плюс R2 (использование не через публичный API).
- В baseline-2 агент поместил файл внутрь `autocaption/confidence.py` (R4 не нарушено), но `main.py` всё равно импортировал его напрямую — `from autocaption.confidence import ...` вместо `from autocaption import ...`,т.е R4 устранилось, но R2 осталось.

Вся проблема baseline сводится к одной архитектурной привычке модели - тянуть новый вспомогательный модуль как top-level helper вместо того, чтобы держать его внутри пакета и экспортировать через публичный API.

## С контекстом (AGENTS.md + skill)
После добавления AGENTS.md и SKILL.md прогоняем тот же промпт с нововедениями.

### Прогон 1 — Codex CLI

```
arpo@MacBook-Pro-Artemij car-scene-captioning % pytest -q

...................................................                                                                                                                                     [100%]
51 passed in 2.51s
arpo@MacBook-Pro-Artemij car-scene-captioning % python3 check.py
Convention check
========================================================================
[R1] PASS - main.py is orchestration-only (no direct ML framework/model loading)
[R2] PASS - main.py uses project code only through the public autocaption API
[R3] PASS - symbols imported from autocaption are declared in autocaption.__all__
[R4] PASS - autocaption is self-contained and does not import project-root helpers
[R5] PASS - heavy pipeline components are initialized outside image-processing loops
[R6] PASS - new image path/URL loading goes through ImageLoader (legacy direct loads are allowlisted)
[R7] PASS - local model files are loaded from MODELS/
========================================================================
Violations: 0
```
### Прогон 2 — Claude Code (такой же промт)

Полный diff кода - [with-context-1.diff](with-context-1.diff).

```
pytest -q
............................................................. [100%]
61 passed in 6.45s

python check.py
Convention check
========================================================================
[R1] PASS - main.py is orchestration-only (no direct ML framework/model loading)
[R2] PASS - main.py uses project code only through the public autocaption API
[R3] PASS - symbols imported from autocaption are declared in autocaption.__all__
[R4] PASS - autocaption is self-contained and does not import project-root helpers
[R5] PASS - heavy pipeline components are initialized outside image-processing loops
[R6] PASS - new image path/URL loading goes through ImageLoader (legacy direct loads are allowlisted)
[R7] PASS - local model files are loaded from MODELS/
========================================================================
Violations: 0
```
## Какими правилами это устранено

Конкретно на ошибку baseline (R2+R4) в AGENTS.md направлены пункты **2** («Use the public `autocaption` API from `main.py`») и **4** («Keep shared pipeline code inside `autocaption`») — с явным примером GOOD/BAD и списком запрещённых импортов. В skill'е та же мысль продублирована в разделах «2. Preserve the package boundary» и «3. Preserve the public API».

**Результат подтверждён дважды, на двух разных агентах** (0 нарушений и на Codex CLI, и на Claude Code) - эффект даёт именно содержимое AGENTS.md/skill, а не особенности конкретного агента.

**Правки, которые сделаны:** файл skill'а скопирован в `.claude/skills/modify-ml-pipeline/SKILL.md`, плюс добавлен `CLAUDE.md` с единственной строкой `@AGENTS.md` (Claude Code в первой сессии после установки ещё не читает `AGENTS.md` напрямую - задокументированное ограничение). Содержимое самого `AGENTS.md` и `SKILL.md` при этом **не редактировалось** - только пути их обнаружения, чтобы не исказить сопоставимость с прогонами в Codex CLI.

## Генерализация 

Ниже воспроизведённый и полностью задокументированный generalization-прогон. Полный diff кода — [generalization-1.diff](generalization-1.diff).

### Промпт
```
Добавь возможность выборочно отключать этапы pipeline.
Пользователь должен иметь возможность через run_pipeline() указать:
- нужно ли выполнять классификацию сцены (scene classification);
- нужно ли выполнять генерацию текстового описания через BLIP (PhotoDescriber/PhotoDescriberWithQuestion).
По умолчанию все этапы включены, чтобы существующий способ вызова run_pipeline() продолжал работать без изменений и с тем же результатом.
Некорректные значения (не bool) должны обрабатываться явно.
Отключённые этапы не должны замедлять обработку — соответствующие тяжёлые модели не должны загружаться, если этап отключён.
Добавь необходимые тесты.
Реализуй задачу в соответствии с существующей архитектурой проекта.
```

Задача намеренно давит на конвенции **R1** и **R5** (не грузить лишние модели, не переносить инициализацию тяжёлых компонентов в цикл) 
### Результат (Claude Code)
```
pytest -q
.........................................                     [100%]
41 passed in 3.55s

python check.py
Convention check
========================================================================
[R1] PASS - main.py is orchestration-only (no direct ML framework/model loading)
[R2] PASS - main.py uses project code only through the public autocaption API
[R3] PASS - symbols imported from autocaption are declared in autocaption.__all__
[R4] PASS - autocaption is self-contained and does not import project-root helpers
[R5] PASS - heavy pipeline components are initialized outside image-processing loops
[R6] PASS - new image path/URL loading goes through ImageLoader (legacy direct loads are allowlisted)
[R7] PASS - local model files are loaded from MODELS/
========================================================================
Violations: 0
```

0 нарушений, включая R1 и R5. Значит, правила сработали не только на исходном кейсе, под который формулировались, но и на структурно другой задаче

(`AGENTS.md`/`SKILL.md` не редактировались между прогонами - оба файла существуют одним коммитом в истории репозитория и больше нигде не менялись, кроме путей обнаружения)

## Итог

| | Baseline (без контекста) | С контекстом |
|---|---|---|
| Нарушений (среднее) | 2.33 (3 прогона) | 0 (2 прогона, 2 агента) |
| Задача 1 (confidence thresholds) | 3 / 1 / 3 | 0 |
| Задача 2, структурно другая (toggle stages) | — | 0 |

AGENTS.md + skill устранили систематическую ошибку baseline и удержали результат на структурно другой задаче, с подтверждением на двух независимых агентах.
