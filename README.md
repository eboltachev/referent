# Интеллектуальная Стенограмма

Production-ready scaffold сервиса для обработки аудио/видео конференций: FastAPI API, отдельный worker с WhisperX large-v3/CUDA, PostgreSQL + PGVector, Redis queue/event bus, React/Vite frontend и DOCX export.

## Требования

- Docker и Docker Compose.
- NVIDIA Container Toolkit.
- CUDA-compatible сервер для worker.
- `.env`, созданный из `.env.example`, с `OPENAI_API_KEY`, `OPENAI_BASE_URL`, `HF_TOKEN`.

## Запуск

```bash
cp .env.example .env
docker compose up --build -d
```

Снаружи публикуется только frontend: `http://server:6004`. Backend, PostgreSQL, Redis и worker доступны только внутри docker network.

## Проверка

```bash
docker compose logs -f backend
docker compose logs -f worker
```

Frontend проксирует `/api/*` во внутренний `backend:8000` через nginx.

## Как загрузить файл

Нажмите зелёную кнопку «Загрузить», выберите поддерживаемый аудио/видео файл (`wav`, `mp3`, `m4a`, `flac`, `ogg`, `webm`, `mp4`, `mov`, `mkv`, `avi`). API асинхронно сохраняет файл через `aiofiles`, создаёт `processing_jobs` со статусом `PENDING`, публикует Redis задачу и быстро возвращает `job_id`.

## Как записать с микрофона

Нажмите красную кнопку «Записать». Frontend использует `MediaRecorder`; при повторном нажатии запись останавливается и blob отправляется в `/api/recordings`. Таймер отображается внутри кнопки.

## Pipeline обработки

Worker берёт job из Redis и выполняет WhisperX pipeline: ASR → alignment → diarization → `assign_word_speakers`. Видео конвертируется в audio через ffmpeg только внутри worker. Модель large-v3 загружается лениво и переиспользуется процессом worker.

## Как скачать DOCX

После `SUCCESS` появляется блок результатов и кнопка «Скачать». Endpoint `/api/jobs/{job_id}/download` генерирует `.docx` через `python-docx`: заголовок, имя файла, дата, языки, таблица спикеров и стенограмма с интервалами `[MM:SS–MM:SS]`.

## Как задать вопрос

Введите вопрос в поле «Вопрос». Streaming endpoint `/api/jobs/{job_id}/questions/stream` отдаёт SSE события `agent_action`, `tool_start`, `tool_end`, `token`, `final`; до токенов показывается действие агента. Агент использует typed tools contract: PGVector/RAG retriever, reranker, SQL/time/calculator, summarizer, speaker resolver и Karpathy LLM Wiki wrapper.

## Как обновляется БД спикеров

В панели «Спикеры» измените имя напротив `SPEAKER_XX`. PATCH endpoint обновляет `speaker_aliases`, все `transcript_segments.speaker_name` для job и делает upsert в глобальную таблицу `speakers`. Если имя уже существует, `speaker_vector` обновляется weighted average с учётом `samples_count`.

## Multilingual correction

После первичной транскрипции `LanguageDetectionService` собирает множество языков по сегментам/окнам. Для каждого сегмента определяется локальный язык; короткие или неоднозначные фрагменты пропускаются с событием `SegmentLanguageDetectionSkipped`, остальные могут быть переобработаны с корректным language и переиндексированы.

## Неблокирующее логирование

`AsyncEventLogger.emit()` кладёт структурированное событие в `asyncio.Queue` и Redis Stream/PubSub, публикует подписчикам SSE/WebSocket broker и не делает прямой blocking insert. Отдельный flusher пишет события батчами в `processing_events`. Секреты (`OPENAI_API_KEY`, `HF_TOKEN`) не логируются.

## Quality gates

```bash
cd backend
uv run ruff check src
uv run mypy src --ignore-missing-imports
uv run pytest
```
