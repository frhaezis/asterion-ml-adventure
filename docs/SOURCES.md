# Источники и границы использования — V2

В реестре **52 записи**: 45 ранее зарегистрированных и 7 добавленных при педагогической переработке. Дата записи не означает повторное чтение всего сайта. У каждой указаны прочитанная область, назначение и ограничение. Полный аудит внешних курсов не заявляется.

Источники из пользовательской коллекции используются как ориентир для объяснения: LensaML, Agent Course Mobile, UvA DL и Hugging Face. Сама коллекция находится отдельно от RnD; RnD использован для актуального уровня и требований вакансии. Обязательная теория находится в APK, ссылки — для углубления. Текст уроков, маленькие случаи и игровые изображения оригинальные; внешние страницы и иллюстрации не скопированы.

Новые записи: `lensaml-regularization-v2`, `agent-course-mobile-v2`, `uva-pytorch-v2`, `hf-course-v2`, `pandas-alignment-v2`, `pytorch-dropout-v2`, `vllm-prefix-v2`. Для Dropout проверены вероятность обнуления и масштабирование; для pandas — индексное выравнивание; для prefix cache — экономия prefill без устранения нового decode.

Прочитанные GitHub skills сохранены как справочные записи; они не являются исполняемыми зависимостями. Инструкции о скачивании или запуске стороннего кода не переносятся автоматически в сборку.

Android использует CPython/Chaquopy; Pyodide относится к браузерной поставке. Ни публикация документации, ни прохождение тестов не подтверждают обучение человека или качество на произвольном Android-устройстве.

## python-data-structures

[Data Structures](https://docs.python.org/3/tutorial/datastructures.html) — Python; primary.

Назначение: Списки, стек, очередь, множества, словарь и обход коллекций.

Прочитанная область: Lists as Stacks; Lists as Queues; Dictionaries; Looping Techniques

Граница: В учебных алгоритмах отдельно учитываются предварительные условия и сложность; наличие словаря не гарантирует worst-case O(1).

Происхождение: Проверенный реестр первой версии (2026-11-16); библиографические поля сохранены.

Связанный материал: [bisect — Array bisection algorithm](https://docs.python.org/3/library/bisect.html). Introduction; bisect_left partition invariant

## pandas-basics

[How do I select a subset of a DataFrame?](https://pandas.pydata.org/docs/getting_started/intro_tutorials/03_subset_data.html) — pandas; primary.

Назначение: DataFrame/Series; выбор колонок; boolean filtering; форма таблицы.

Прочитанная область: Specific columns; filtering rows

Граница: Данные Titanic из источника не включены в игру; используются собственные маленькие таблицы.

Происхождение: Проверенный реестр первой версии (2026-11-16); библиографические поля сохранены.

## numpy-basics

[NumPy: the absolute basics for beginners](https://numpy.org/doc/stable/user/absolute_beginners.html) — NumPy; primary.

Назначение: Массивы, shape, axis, dtype, срезы, elementwise operations и broadcasting.

Прочитанная область: What is an array?; Array fundamentals; Array attributes; Basic array operations; Broadcasting

Граница: Elementwise multiplication не совпадает с матричным произведением; срез NumPy часто является view.

Происхождение: Проверенный реестр первой версии (2026-11-16); библиографические поля сохранены.

## sklearn-pitfalls

[Common pitfalls and recommended practices](https://scikit-learn.org/stable/common_pitfalls.html) — scikit-learn; primary.

Назначение: Разделение данных до обучения преобразований; fit только на train; transform на остальных данных; Pipeline против утечки.

Прочитанная область: Inconsistent preprocessing; Data leakage; How to avoid data leakage

Граница: Pipeline помогает только при корректном разбиении; временная и групповая утечки требуют подходящей схемы split.

Происхождение: Проверенный реестр первой версии (2026-11-16); библиографические поля сохранены.

Связанный материал: [Imputation of missing values](https://scikit-learn.org/stable/modules/impute.html). Introduction; SimpleImputer

## sklearn-metrics

[Metrics and scoring: quantifying the quality of predictions](https://scikit-learn.org/stable/modules/model_evaluation.html) — scikit-learn; primary.

Назначение: Precision, recall, F1, confusion matrix; выбор метрики в соответствии с ценой ошибки.

Прочитанная область: Which scoring function should I use?; Precision, recall and F-measures; Binary classification

Граница: Порог меняет рабочую точку; высокая accuracy сама по себе не доказывает качество на редком классе.

Происхождение: Проверенный реестр первой версии (2026-11-16); библиографические поля сохранены.

## sklearn-supervised

[Supervised learning](https://scikit-learn.org/stable/supervised_learning.html) — scikit-learn; primary.

Назначение: Семейства supervised-моделей; линейная регрессия, SVM, деревья, ансамбли.

Прочитанная область: Обзор главы и релевантные введения связанных страниц

Граница: Обзор не означает, что один алгоритм подходит всем задачам. XGBoost, LightGBM и CatBoost все поддерживают разные настройки; сходство или преимущество проверяется на своей задаче, а не по бренду.

Происхождение: Проверенный реестр первой версии (2026-11-16); библиографические поля сохранены.

Связанный материал: [Linear Models](https://scikit-learn.org/stable/modules/linear_model.html). Ordinary Least Squares; Ridge; Lasso; Logistic regression; binary formula

Связанный материал: [Support Vector Machines](https://scikit-learn.org/stable/modules/svm.html). Introduction; Classification

Связанный материал: [Decision Trees](https://scikit-learn.org/stable/modules/tree.html). Introduction; advantages and limitations

Связанный материал: [Ensembles](https://scikit-learn.org/stable/modules/ensemble.html). Introduction; Gradient-boosted trees; Random Forests

Связанный материал: [Introduction to Boosted Trees — XGBoost](https://xgboost.readthedocs.io/en/stable/tutorials/model.html). Introduction; training loss plus regularization

Связанный материал: [Features — LightGBM](https://lightgbm.readthedocs.io/en/stable/Features.html). Histogram algorithm; leaf-wise growth; categorical features

Связанный материал: [How training is performed — CatBoost](https://catboost.ai/docs/en/concepts/algorithm-main-stages). Overview; consecutive trees; categorical feature stage

Связанный материал: [Nearest Neighbors](https://scikit-learn.org/stable/modules/neighbors.html). Introduction; neighbors-based classification and regression

Связанный материал: [Naive Bayes](https://scikit-learn.org/stable/modules/naive_bayes.html). Introduction; conditional independence assumption; probability caveat

Связанный материал: [CatBoost: unbiased boosting with categorical features](https://arxiv.org/abs/1706.09516). Abstract: ordered boosting and categorical features

Связанный материал: [Categorical features — CatBoost](https://catboost.ai/docs/en/features/categorical-features). Categorical support; internal feature transformations; one-hot conditions

## sklearn-unsupervised

[Unsupervised learning](https://scikit-learn.org/stable/unsupervised_learning.html) — scikit-learn; primary.

Назначение: Различие кластеризации и задачи с целевой меткой; K-means, DBSCAN, PCA как семейства.

Прочитанная область: Обзор главы; Clustering introduction, K-means and DBSCAN

Граница: Кластеры не становятся истинными классами автоматически; масштаб признаков и расстояние влияют на результат.

Происхождение: Проверенный реестр первой версии (2026-11-16); библиографические поля сохранены.

Связанный материал: [Clustering](https://scikit-learn.org/stable/modules/clustering.html). Overview; K-means; DBSCAN

Связанный материал: [Principal component analysis](https://scikit-learn.org/stable/modules/decomposition.html). Exact PCA; centering without scaling

## sklearn-model-selection

[Cross-validation: evaluating estimator performance](https://scikit-learn.org/stable/modules/cross_validation.html) — scikit-learn; primary.

Назначение: Роли train, validation и test; k-fold CV; опасность настройки модели по test.

Прочитанная область: Введение, validation holdout и описание k-fold

Граница: Обычная случайная CV не подходит автоматически временным и связанным наблюдениям.

Происхождение: Проверенный реестр первой версии (2026-11-16); библиографические поля сохранены.

## pytorch-quickstart

[Quickstart](https://docs.pytorch.org/tutorials/beginner/basics/quickstart_tutorial.html) — PyTorch; primary.

Назначение: nn.Module, DataLoader, loss, backward, optimizer.step, zero_grad; train/eval и no_grad.

Прочитанная область: Optimizing Model Parameters; training loop; test loop

Граница: Учебные примеры игры используют маленькие синтетические данные и CPU; они не воспроизводят benchmark из документации.

Происхождение: Проверенный реестр первой версии (2026-11-16); библиографические поля сохранены.

## pytorch-autograd

[Automatic Differentiation with torch.autograd](https://docs.pytorch.org/tutorials/beginner/basics/autogradqs_tutorial.html) — PyTorch; primary.

Назначение: requires_grad, вычислительный граф, backward, .grad, накопление градиентов, no_grad и detach.

Прочитанная область: Computing Gradients; Disabling Gradient Tracking; More on Computational Graphs

Граница: backward вычисляет градиенты; сами веса обновляет optimizer. Градиенты нелистовых узлов можно сохранять специально, это не поведение по умолчанию.

Происхождение: Проверенный реестр первой версии (2026-11-16); библиографические поля сохранены.

## pytorch-losses

[CrossEntropyLoss](https://docs.pytorch.org/docs/2.15/generated/torch.nn.CrossEntropyLoss.html) — PyTorch; primary.

Назначение: CrossEntropyLoss принимает logits; варианты целевых индексов и распределений; связь с LogSoftmax и NLLLoss.

Прочитанная область: Описание входов и targets; формулы; note on LogSoftmax

Граница: Для обычной многоклассовой классификации перед CrossEntropyLoss не нужно отдельно применять softmax к входу. Contrastive loss — семейство функций, а не одно название API; в упражнениях явно задано соглашение о метках пары.

Происхождение: Проверенный реестр первой версии (2026-11-16); библиографические поля сохранены.

Связанный материал: [MSELoss](https://docs.pytorch.org/docs/2.15/generated/torch.nn.MSELoss.html). Formula; reduction; tensor shapes

Связанный материал: [CosineEmbeddingLoss](https://docs.pytorch.org/docs/2.15/generated/torch.nn.CosineEmbeddingLoss.html). Pair labels; cosine and margin loss formula

Связанный материал: [A Simple Framework for Contrastive Learning of Visual Representations](https://arxiv.org/abs/2002.05709). Abstract

## pytorch-normalization

[LayerNorm](https://docs.pytorch.org/docs/2.15/generated/torch.nn.LayerNorm.html) — PyTorch; primary.

Назначение: LayerNorm нормализует последние normalized_shape измерения; сравнение с BatchNorm и роль train/eval.

Прочитанная область: Formula, normalized_shape, statistics in train/eval; BatchNorm1d formula and running statistics

Граница: BatchNorm обычно использует running statistics в eval; при track_running_stats=False поведение другое.

Происхождение: Проверенный реестр первой версии (2026-11-16); библиографические поля сохранены.

Связанный материал: [BatchNorm1d](https://docs.pytorch.org/docs/2.15/generated/torch.nn.BatchNorm1d.html). Formula; running statistics; track_running_stats

Связанный материал: [Dropout](https://docs.pytorch.org/docs/2.15/generated/torch.nn.Dropout.html). Training zeroing probability; scaling; evaluation identity

## transformer-paper

[Attention Is All You Need](https://arxiv.org/html/1706.03762v7) — Vaswani et al.; primary.

Назначение: Scaled dot-product attention, Q/K/V, масштаб 1/sqrt(d_k), multi-head attention.

Прочитанная область: Abstract; section 3.2, especially 3.2.1 and 3.2.2

Граница: Метафора внимания в игре не утверждает наличие человеческого сознания; наиболее высокий вес внимания не является доказательством причинности.

Происхождение: Проверенный реестр первой версии (2026-11-16); библиографические поля сохранены.

## hf-tokenizers

[Tokenization algorithms](https://huggingface.co/docs/transformers/main/en/tokenizer_summary) — Hugging Face; primary.

Назначение: Токены и subword-разбиение; BPE, WordPiece и Unigram; словарь и зависимость разбиения от tokenizer.

Прочитанная область: Introduction; Byte pair encoding

Граница: Токен не равен слову; приведённое разбиение является учебным и зависит от конкретного словаря. Страница main может меняться.

Происхождение: Проверенный реестр первой версии (2026-11-16); библиографические поля сохранены.

## hf-architectures

[Transformer Architectures](https://huggingface.co/learn/llm-course/chapter1/6) — Hugging Face; primary.

Назначение: Различие encoder-only, decoder-only и encoder-decoder; типичные задачи и causal attention.

Прочитанная область: Introduction; Encoder models; Decoder models

Граница: Это распространённые архитектурные семейства, а не исчерпывающая классификация всех моделей.

Происхождение: Проверенный реестр первой версии (2026-11-16); библиографические поля сохранены.

## hf-kv-cache

[How caching works](https://huggingface.co/docs/transformers/cache_explanation) — Hugging Face; primary.

Назначение: Повторное использование K/V прошлых токенов во время autoregressive inference; цена памяти.

Прочитанная область: Introduction; Attention matrices

Граница: KV cache не база знаний и не долгосрочная память агента; его применение и размер зависят от архитектуры.

Происхождение: Проверенный реестр первой версии (2026-11-16); библиографические поля сохранены.

## hf-generation

[Generation strategies](https://huggingface.co/docs/transformers/generation_strategies) — Hugging Face; primary.

Назначение: Greedy decoding, sampling и beam search; generate и max_new_tokens. Temperature меняет распределение logits, top-k ограничивает число кандидатов, top-p ограничивает накопленную вероятность.

Прочитанная область: Basic decoding methods: Greedy search, Sampling, Beam search

Граница: Случайность декодирования не измеряет истинность; remote custom generation из документации игра не загружает.

Происхождение: Проверенный реестр первой версии (2026-11-16); библиографические поля сохранены.

Связанный материал: [GenerationConfig](https://huggingface.co/docs/transformers/main_classes/text_generation). Output length; generation strategy; temperature, top_k, top_p

Связанный материал: [Prompt engineering](https://huggingface.co/docs/transformers/main/tasks/prompting). Introduction; Best practices; Few-shot prompting and chat templates

## hf-sft

[SFT Trainer](https://huggingface.co/docs/trl/sft_trainer) — Hugging Face TRL; primary.

Назначение: Обучение на примерах; language-modeling и prompt-completion datasets; conversational format и chat template.

Прочитанная область: Overview; Expected dataset type and format

Граница: В игре SFT объясняется на небольших примерах: полноценное дообучение внешней LLM не требуется.

Происхождение: Проверенный реестр первой версии (2026-11-16); библиографические поля сохранены.

Связанный материал: [Chat templates](https://huggingface.co/docs/transformers/chat_templating). Token sequence; roles and control tokens; model-specific templates

## peft-lora

[LoRA](https://huggingface.co/docs/peft/v0.21.0/package_reference/lora) — Hugging Face PEFT; primary.

Назначение: Ранг адаптера, target_modules, lora_alpha и число обучаемых параметров.

Прочитанная область: LoRA usage; rank and alpha; LoraConfig parameter reference

Граница: Конкретные названия target_modules зависят от архитектуры; адаптеры должны соответствовать базовой модели.

Происхождение: Проверенный реестр первой версии (2026-11-16); библиографические поля сохранены.

## qlora-paper

[QLoRA: Efficient Finetuning of Quantized LLMs](https://arxiv.org/abs/2305.14314) — Dettmers et al.; primary.

Назначение: Замороженная 4-bit база и обучаемые LoRA-адаптеры; NF4, double quantization, paged optimizers.

Прочитанная область: Abstract

Граница: Показатели статьи относятся к её экспериментам; гарантия одинакового качества для любой модели не следует из результатов.

Происхождение: Проверенный реестр первой версии (2026-11-16); библиографические поля сохранены.

## dpo-paper

[Direct Preference Optimization: Your Language Model is Secretly a Reward Model](https://arxiv.org/abs/2305.18290) — Rafailov et al.; primary.

Назначение: Обучение по парам предпочтений; отличие DPO от SFT и от схемы с отдельной reward model и PPO.

Прочитанная область: Abstract

Граница: Предпочтение в датасете не является гарантией объективной истинности или безопасности ответа.

Происхождение: Проверенный реестр первой версии (2026-11-16); библиографические поля сохранены.

## hf-quantization

[Quantization overview](https://huggingface.co/docs/transformers/quantization/overview) — Hugging Face; primary.

Назначение: Меньшая битность весов/активаций; компромисс памяти, скорости и качества; загрузка квантованных checkpoints. GGUF как формат контейнера, а не отдельная битность.

Прочитанная область: Overview; Two ways to use a quantized model; Quantize a model while loading

Граница: Память на веса не равна полной RAM/VRAM: есть cache, activations, metadata и runtime. Ускорение зависит от железа и kernels.

Происхождение: Проверенный реестр первой версии (2026-11-16); библиографические поля сохранены.

Связанный материал: [GGUF specification](https://raw.githubusercontent.com/ggml-org/ggml/master/docs/gguf.md). Introduction; specification goals; metadata

## distillation

[Distilling the Knowledge in a Neural Network](https://arxiv.org/abs/1503.02531) — Hinton, Vinyals and Dean; primary.

Назначение: Передача поведения teacher/ensemble компактному student; отличие от уменьшения битности.

Прочитанная область: Abstract

Граница: Distillation требует обучения student; маленькая модель не обязана сохранять все способности teacher.

Происхождение: Проверенный реестр первой версии (2026-11-16); библиографические поля сохранены.

## rag-paper

[Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401) — Lewis et al.; primary.

Назначение: Комбинация параметрической модели с внешним индексом и retrieval; проверяемая опора на найденные документы.

Прочитанная область: Abstract

Граница: Современный RAG шире конкретной архитектуры статьи. Retrieval не гарантирует релевантность или правильную интерпретацию.

Происхождение: Проверенный реестр первой версии (2026-11-16); библиографические поля сохранены.

Связанный материал: [Retrieve & Re-Rank](https://sbert.net/examples/sentence_transformer/applications/retrieve_rerank/README.html). Retrieve & Re-Rank Pipeline; Bi-Encoder; Cross-Encoder; paragraph example

Связанный материал: [RAG in Transformers](https://huggingface.co/docs/transformers/model_doc/rag). Introduction; conditioning generation on passages; index updates

## agent-react

[ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629) — Yao et al.; primary.

Назначение: Цикл выбора действия, обращения к инструменту, наблюдения и следующего решения.

Прочитанная область: Abstract

Граница: Учебный симулятор показывает видимые действия и наблюдения; не выдаёт детерминированную цепочку карточек за работающую автономную LLM.

Происхождение: Проверенный реестр первой версии (2026-11-16); библиографические поля сохранены.

Связанный материал: [Building effective agents](https://www.anthropic.com/research/building-effective-agents). What are agents?; When to use agents; Parallelization; Orchestrator-workers; Agents

## mcp-tools

[Tools — Model Context Protocol](https://modelcontextprotocol.io/specification/2025-06-18/server/tools) — Model Context Protocol; primary.

Назначение: Имена инструментов, JSON Schema, tools/list, tools/call, результаты и ошибки. Resources дают контекст, адресованный URI.

Прочитанная область: User interaction model; capabilities; protocol messages; tool data types

Граница: Прочитана версия спецификации 2025-06-18. MCP стандартизует интерфейс, но не создаёт интеллект агента и не делает сервер доверенным.

Происхождение: Проверенный реестр первой версии (2026-11-16); библиографические поля сохранены.

Связанный материал: [Resources — Model Context Protocol](https://modelcontextprotocol.io/specification/2025-06-18/server/resources). Resources, URIs, application-driven model; resources/list and resources/read

## lm-eval

[Language Model Evaluation Harness](https://github.com/EleutherAI/lm-evaluation-harness) — EleutherAI; primary.

Назначение: Воспроизводимые наборы задач, prompt/config, метрики и сравнение моделей.

Прочитанная область: README: Overview; Basic Usage; backend table

Граница: Игра учит принципам оценки; она не запускает полный lm-evaluation-harness и не присваивает своим мини-задачам статус benchmark.

Происхождение: Проверенный реестр первой версии (2026-11-16); библиографические поля сохранены.

## llm-judge

[Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena](https://arxiv.org/abs/2306.05685) — Zheng et al.; primary.

Назначение: Ограничения LLM-оценщика: смещение по позиции, многословию, собственной модели и ограничения рассуждений.

Прочитанная область: Abstract

Граница: Оценка по рубрике и сверка с человеком необходимы; результат одного оценщика не абсолютная истина.

Происхождение: Проверенный реестр первой версии (2026-11-16); библиографические поля сохранены.

## vllm-serving

[OpenAI-Compatible Server](https://docs.vllm.ai/en/latest/serving/online_serving/openai_compatible_server/) — vLLM; primary.

Назначение: HTTP-serving; /v1/chat/completions; зависимость Chat API от chat template; отличие model weights от inference server. Continuous batching заполняет освободившиеся места запросами между шагами генерации.

Прочитанная область: Introduction; Supported APIs; extra request parameters

Граница: Прочитан интерфейс HTTP, не подтверждена установка vLLM на Windows пользователя. Для игры сервер необязателен; соединение только localhost.

Происхождение: Проверенный реестр первой версии (2026-11-16); библиографические поля сохранены.

Связанный материал: [Continuous batching — Transformers](https://huggingface.co/docs/transformers/continuous_batching). Introduction; scheduling requests at generation steps

Связанный материал: [Automatic Prefix Caching](https://docs.vllm.ai/en/latest/features/automatic_prefix_caching/). Introduction; Example workloads; Limits (prefill reuse, not faster decode)

## skill-feel

[maximizing-game-feel / SKILL.md](https://github.com/abagames/agentic-gamedev-skills/blob/main/.agents/skills/maximizing-game-feel/SKILL.md) — abagames; community-skill.

Назначение: Сдержанная обратная связь, читаемость, честные границы объектов, сохранение отклика.

Прочитанная область: Полный SKILL.md

Граница: Справочный материал; внешние скрипты не установлены и не запускались. Полезен для полировки работающей игры, не заменяет игровой цикл.

Происхождение: Проверенный реестр первой версии (2026-11-16); библиографические поля сохранены.

## skill-design

[game-design / SKILL.md](https://github.com/saschb2b/skills/blob/main/skills/productivity/game-design/SKILL.md) — saschb2b; community-skill.

Назначение: Осмысленный выбор, самостоятельная ценность core loop, обучение и читаемость интерфейса.

Прочитанная область: Полный SKILL.md

Граница: Не приняты предложения автоматически внедрять hooks/CLAUDE.md, обязательные согласования и категоричные жанровые правила. Использован как критически прочитанная справка.

Происхождение: Проверенный реестр первой версии (2026-11-16); библиографические поля сохранены.

## skill-browser-feel

[game-feel / SKILL.md](https://github.com/xhuozhong/codex-game-studio/blob/main/skills/game-feel/SKILL.md) — xhuozhong; community-skill.

Назначение: Проверка реальным вводом, отклик перед декором, reduced motion, ограничения browser audio.

Прочитанная область: Полный SKILL.md

Граница: Короткий общий чеклист; не самостоятельная методология и не доказательство качества готовой игры.

Происхождение: Проверенный реестр первой версии (2026-11-16); библиографические поля сохранены.

## instructgpt-paper

[Training language models to follow instructions with human feedback](https://arxiv.org/html/2203.02155v1) — Ouyang et al., 2022; primary.

Назначение: Один конкретный RLHF pipeline: SFT demonstrations → preference comparisons/reward model → PPO; границы представительности human feedback.

Прочитанная область: Abstract; Introduction; §3.1 High-level methodology; начало §5.3 Limitations

Граница: Описан метод InstructGPT, а не универсальная обязательная последовательность всех preference methods. Предпочтения оценщиков не равны истине или единому набору человеческих ценностей.

Происхождение: Проверенный реестр первой версии (2026-11-16); библиографические поля сохранены.

## corrigibility-paper

[Corrigibility](https://intelligence.org/files/Corrigibility.pdf) — Soares et al., AAAI Workshop 2015; primary.

Назначение: Краткий контекст: система должна допускать исправление и остановку; простая кнопка и лимит цикла не решают общую исследовательскую проблему.

Прочитанная область: Abstract; §1 Introduction; §1.1 Corrigibility

Граница: Теоретическое введение и формальные постановки. В игре только распознавание понятия, без доказательства corrigibility или заявлений о сознании моделей.

Происхождение: Проверенный реестр первой версии (2026-11-16); библиографические поля сохранены.

## python-control-flow

[More Control Flow Tools](https://docs.python.org/3.12/tutorial/controlflow.html) — Python; primary.

Назначение: Условия, циклы, функции и аргументы.

Прочитанная область: if; for; range; break and continue; defining functions and arguments.

Граница: Первый десяток уровней даёт практический фундамент; не обещает исчерпывающее знание каждой конструкции языка.

Происхождение: Официальная документация, проверена для v2.

## python-classes

[Classes](https://docs.python.org/3.12/tutorial/classes.html) — Python; primary.

Назначение: Состояние экземпляра, self, методы, композиция, итераторы.

Прочитанная область: Introduction; scopes and namespaces; class and instance variables; iterators and generators.

Граница: Композиция игровых объектов не равна моделированию полноценной агентной платформы.

Происхождение: Официальная документация, проверена для v2.

## python-errors

[Errors and Exceptions](https://docs.python.org/3.12/tutorial/errors.html) — Python; primary.

Назначение: Различать синтаксическую ошибку и исключение, обработать невалидные входы.

Прочитанная область: Syntax Errors; Exceptions; Handling Exceptions.

Граница: Перехватываются ожидаемые типы ошибок; blanket except не считается корректным исправлением.

Происхождение: Официальная документация, проверена для v2.

## python-io

[Input and Output](https://docs.python.org/3.12/tutorial/inputoutput.html) — Python; primary.

Назначение: Строковое форматирование и чтение текстовых данных.

Прочитанная область: Fancier Output Formatting; formatted string literals; Reading and Writing Files.

Граница: В игре используется виртуальная файловая система Python или StringIO; личные файлы телефона недоступны.

Происхождение: Официальная документация, проверена для v2.

## python-modules

[Modules](https://docs.python.org/3.12/tutorial/modules.html) — Python; primary.

Назначение: Импорт модулей и отдельные пространства имён.

Прочитанная область: Introduction; import module; from module import name; More on Modules.

Граница: Задания используют встроенную стандартную библиотеку, не требуют pip или сети.

Происхождение: Официальная документация, проверена для v2.

## python-collections

[collections — Container datatypes](https://docs.python.org/3.12/library/collections.html) — Python; primary.

Назначение: Выбор deque, Counter и defaultdict для игровых данных.

Прочитанная область: Container datatype overview and documented purpose of deque/Counter/defaultdict.

Граница: deque подходит для очереди; список сохраняется для индексируемой последовательности.

Происхождение: Официальная документация, проверена для v2.

## python-heapq

[heapq — Heap queue algorithm](https://docs.python.org/3.12/library/heapq.html) — Python; primary.

Назначение: Приоритетная очередь и обслуживание задач.

Прочитанная область: Heap invariant; heappush; heappop; heapify; merge.

Граница: Min-heap возвращает минимальный ключ; одинаковые приоритеты требуют явно заданного разрешения ничьей.

Происхождение: Официальная документация, проверена для v2.

## pyodide-worker

[Using Pyodide in a web worker — 0.26.4](https://pyodide.org/en/0.26.4/usage/webworker.html) — Pyodide; primary.

Назначение: Настоящий CPython 3.12 в браузерной версии вне UI-потока, сообщения между worker и интерфейсом.

Прочитанная область: Web Worker setup, loading Pyodide, exchanging messages and namespaces.

Граница: Зафиксирована версия 0.26.4: её classic-worker API не следует смешивать с новым module-worker API Pyodide 314.

Происхождение: Официальная документация, проверена для v2.

## pyodide-deploy

[Downloading and deploying Pyodide — 0.26.4](https://pyodide.org/en/0.26.4/usage/downloading-and-deploying.html) — Pyodide; primary.

Назначение: Локальная поставка core runtime и stdlib для полностью офлайн-запуска.

Прочитанная область: Core files; local deployment; pyodide.js and pyodide.mjs distinction; pyodide-lock.json.

Граница: CDN использован только при сборке. Браузерная версия загружает wasm и stdlib с локального сервера; Android использует отдельный нативный процесс CPython.

Происхождение: Официальная документация, проверена для v2.

## hf-multimodal

[Multimodal chat templates](https://huggingface.co/docs/transformers/main/en/chat_templating_multimodal) — Hugging Face; primary.

Назначение: Текст, изображение и звук как разные входы; Processor и multimodal content; ASR и TTS в интерфейсе смартфонного агента.

Прочитанная область: Multimodal chat templates introduction; ImageTextToTextPipeline; Using apply_chat_template. Related ASR and TTS introduction/pipeline sections.

Граница: В APK нет загруженной multimodal LLM, ASR или TTS-модели. Урок объясняет архитектуру и проверку переходов. Код примеров и команды установки документации не запускались; ветка main изменяется.

Происхождение: Официальная документация, разделы проверены для v2.

Связанный материал: [Automatic speech recognition](https://huggingface.co/docs/transformers/main/en/tasks/asr). Introduction: speech signal to text; task distinction.

Связанный материал: [Text to speech](https://huggingface.co/docs/transformers/main/en/tasks/text-to-speech). Introduction and text-to-audio / text-to-speech pipeline.

## chaquopy-runtime

[Chaquopy licensing and version summary](https://chaquo.com/chaquopy/license/) — Chaquopy; primary.

Назначение: Бесплатный нативный CPython 3.12.15 в Android через Chaquopy 17.2.0; проверка лицензии и платформенных требований.

Прочитанная область: Licensing: open-source versions12.0.1+; open-source announcement MIT; version17.2 Python/API compatibility.

Граница: Официальная таблица совместимости не заменяет испытание APK. В игре нативные библиотеки arm64-v8a и x86_64; фактическая проверка проводится в x86_64 эмуляторе.

Происхождение: Официальная документация и объявление проекта, проверены для нативного runtime v2.

Связанный материал: [Chaquopy is now open-source](https://chaquo.com/chaquopy/chaquopy-is-now-open-source/). MIT source license and first open-source release12.0.1

Связанный материал: [Version summary — Chaquopy17.2](https://chaquo.com/chaquopy/doc/current/versions.html). 17.2 supports Python3.10–3.15 and minimum AndroidAPI24

## lensaml-regularization-v2

[LensaML — Regularization](https://lensaml.com/explainers/regularization) — LensaML; reference.

Назначение: Наглядное разделение data loss, penalty и силы регуляризации; эпизод23.

Прочитанная область: Страница regularization; идея визуального сравнения. Иллюстрации и текст не копировались.

Граница: Педагогический ресурс, не первичная спецификация оптимизатора. Формулы и оговорку AdamW проверяют по первичной документации.

Происхождение: Проверка конкретных разделов при переработке V2; авторские объяснения и маленькие примеры.

## agent-course-mobile-v2

[Agentic AI — Mobile Course](https://agenticai.varasrinivas.com/courses/opensource/mobile/index.html) — Agentic AI Course; reference.

Назначение: Последовательность concept → diagram → pseudocode → pitfall для темы агентов.

Прочитанная область: Доступный индекс курса и описание карточек; полный набор модулей не проверен.

Граница: Внешняя коллекция для углубления. Не заявляется аудит всего курса; обязательное объяснение включено в игру.

Происхождение: Проверка конкретных разделов при переработке V2; авторские объяснения и маленькие примеры.

## uva-pytorch-v2

[UvA DL — Introduction to PyTorch](https://uvadlc-notebooks.readthedocs.io/en/latest/tutorial_notebooks/tutorial2/Introduction_to_PyTorch.html) — University of Amsterdam / Phillip Lippe; teaching.

Назначение: Связь тензоров, автодифференцирования, модели, batch и проверки; эпизоды33–40.

Прочитанная область: Introduction; The Basics of PyTorch; The data loader class, batch_size и drop_last.

Граница: Большой notebook не встроен; мобильная практика использует стандартную библиотеку Python, без выполнения PyTorch.

Происхождение: Проверка конкретных разделов при переработке V2; авторские объяснения и маленькие примеры.

## hf-course-v2

[Hugging Face LLM Course — Introduction](https://huggingface.co/learn/llm-course/chapter1/1) — Hugging Face; teaching.

Назначение: Последовательность понятий Transformers/LLM и самостоятельное продолжение теоретического трека.

Прочитанная область: Вводный раздел курса и структура; не весь курс.

Граница: Внешние модели и датасеты не включены; курс может обновляться независимо от APK.

Происхождение: Проверка конкретных разделов при переработке V2; авторские объяснения и маленькие примеры.

## pandas-alignment-v2

[pandas — Data structures and label alignment](https://pandas.pydata.org/docs/user_guide/dsintro.html) — pandas; primary.

Назначение: DataFrame, Series, соответствие по меткам индекса; эпизод17.

Прочитанная область: Series; Vectorized operations and label alignment; Data alignment and arithmetic.

Граница: Числовой пример оригинальный. Поиск по позиции и сопоставление по ID явно различаются; pandas не требуется в мобильном runtime.

Происхождение: Проверка конкретных разделов при переработке V2; авторские объяснения и маленькие примеры.

## pytorch-dropout-v2

[PyTorch — nn.Dropout](https://docs.pytorch.org/docs/stable/generated/torch.nn.Dropout.html) — PyTorch; primary.

Назначение: Вероятность обнуления, inverted dropout, train/eval; эпизод39.

Прочитанная область: Описание класса, p, scaling и evaluation. Stable URL при проверке перенаправлялся на версию2.15.

Граница: Сравнение no_grad и eval также опирается на сохранённые PyTorch beginner/autograd источники. Не утверждается, что ровно p доля маленького вектора обнулится.

Происхождение: Проверка конкретных разделов при переработке V2; авторские объяснения и маленькие примеры.

## vllm-prefix-v2

[vLLM — Automatic Prefix Caching](https://docs.vllm.ai/en/latest/features/automatic_prefix_caching/) — vLLM; primary.

Назначение: Различие prefix reuse, prefill и генерации новых токенов; эпизод87.

Прочитанная область: Introduction; Example workloads; Limits.

Граница: Описан механизм, без обещания ускорения любой нагрузки и без привязки к меняющимся CLI-флагам.

Происхождение: Проверка конкретных разделов при переработке V2; авторские объяснения и маленькие примеры.

