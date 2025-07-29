# Guía de Formato para Logs Útiles y Claros

Este documento define cómo deben verse los logs del sistema, con ejemplos de antes y después, y el uso de emojis para identificar rápidamente el origen de cada mensaje.

> **Nota 1:** Todos los logs deben estar siempre en inglés, independientemente del contexto o el módulo.
> **Nota 2:** Siempre omite la parte de la hora T (por ejemplo, `18:55:20.725`). Solo se debe mostrar la hora normal (por ejemplo, `16:55:20`), que es la que realmente aparece en los logs.
> **Nota 3:** Es altamente recomendable que el campo de origen (archivo:función) aparezca siempre después de la hora y antes del emoji/etiqueta. Esto facilita la trazabilidad y el debugging. No es difícil de implementar si se personaliza el logger.
> **Nota 4:** La columna del emoji/etiqueta (por ejemplo, 🗂️ [INDEX]) debe estar siempre alineada en vertical, usando padding en el campo de origen para que el emoji/etiqueta empiece siempre en la misma posición. Esto mejora mucho la legibilidad visual de los logs.

---

## Ejemplo visual de alineación

Así deben verse los logs, con la columna del emoji/etiqueta perfectamente alineada:

```
16:55:20 | services.indexing_service:_index_files_in_batches      | 🗂️ [INDEX]   Indexing started   | total=336, batches=7, batch_size=48, trigger=manual, task_id=idx_1752684913_a74d8f33
16:55:21 | services.indexing_worker_pool:_worker                  | 🗂️ [INDEX]   Batch 1 started    | files=48, worker=0
16:55:22 | backend.api:main                                      | 🖥️ [BACKEND] Service started    | port=8080, env=prod
16:55:23 | progress.monitor:track_progress                       | ⏳ [PROGRESS]10% completed      | batch=1, files_done=5
16:55:24 | enrichment.service:enrich_chunks                      | 🧩 [ENRICH]   Enrichment done    | chunks=124, elapsed_ms=77890.96
16:55:25 | services.indexing_worker_pool:_worker                  | ⚠️ [WARN]     File skipped      | file=README.md, reason=empty
16:55:26 | services.indexing_worker_pool:_worker                  | ❌ [ERROR]    Indexing failed   | file=main.py, error=TimeoutError
```

- El campo de origen tiene un ancho fijo (rellenado con espacios).
- El emoji/etiqueta empieza siempre en la misma columna, alineado verticalmente.
- El mensaje principal y los detalles van después, separados por el mismo delimitador (`|`).

---

## Ejemplo real: primeras líneas del proceso de indexado

### Antes

```
16:55:20 | INFO     | services.indexing_service:_index_files_in_batches | Starting batch processing with advanced progress tracking{'total_files': 336, 'total_batches': 7, 'batch_size': 48, 'trigger': 'manual', 'task_id': 'idx_1752684913_a74d8f33'}
16:55:20 | INFO     | services.indexing_service:_index_files_in_batches | Processing batch with progress tracking{'batch_number': 1, 'total_batches': 7, 'files_in_batch': 48, 'progress_percentage': 0.0, 'files_processed_so_far': 0, 'estimated_remaining_minutes': 'calculating...'}
16:55:20 | INFO     | core.secure_config:_find_config_file             | Using local configuration{'config_path': '/.acolyte'}
16:55:20 | INFO     | core.secure_config:_find_config_file             | Using local configuration{'config_path': '/.acolyte'}
16:55:20 | INFO     | core.secure_config:__init__                      | Settings initialized{'config_source': '.acolyte'}
16:55:20 | INFO     | services.indexing_worker_pool:__init__            | IndexingWorkerPool created{'num_workers': 4, 'embeddings_semaphore': 2}
16:55:20 | INFO     | services.indexing_worker_pool:initialize          | Initializing worker pool{}
16:55:20 | INFO     | services.indexing_worker_pool:_create_weaviate_clients | Created shared Weaviate client for all workers - v3.26.7 workaround{'workers': 4}
16:55:21 | INFO     | enrichment.git_manager:initialize                 | Initializing shared Git repository{'repo_path': '/project'}
16:55:21 | INFO     | enrichment.git_manager:initialize                 | Git repository loaded successfully{'git_dir': '/project/.git', 'instance_id': '0x7faec86555d0'}
```

### Después (Propuesto)

```
16:55:20 | services.indexing_service:_index_files_in_batches      | 🗂️ [INDEX]   Indexing started           | total=336, batches=7, batch_size=48, trigger=manual, task_id=idx_1752684913_a74d8f33
16:55:20 | services.indexing_service:_index_files_in_batches      | 🗂️ [INDEX]   Batch 1 processing         | batch=1, total_batches=7, files_in_batch=48
16:55:20 | core.secure_config:_find_config_file                   | 🖥️ [BACKEND] Using local configuration  | config_path=/.acolyte
16:55:20 | core.secure_config:_find_config_file                   | 🖥️ [BACKEND] Using local configuration  | config_path=/.acolyte
16:55:20 | core.secure_config:__init__                            | 🖥️ [BACKEND] Settings initialized       | config_source=.acolyte
16:55:20 | services.indexing_worker_pool:__init__                 | 🗂️ [INDEX]   Worker pool created        | num_workers=4, embeddings_semaphore=2
16:55:20 | services.indexing_worker_pool:initialize               | 🗂️ [INDEX]   Initializing worker pool   |
16:55:20 | services.indexing_worker_pool:_create_weaviate_clients | 🗂️ [INDEX]   Weaviate clients created   | workers=4
16:55:21 | enrichment.git_manager:initialize                      | 🧩 [ENRICH]  Initializing shared Git    | repo_path=/project
16:55:21 | enrichment.git_manager:initialize                      | 🧩 [ENRICH]  Git repository loaded      | git_dir=/project/.git, instance_id=0x7faec86555d0
```

---

## Real backend startup example: before and after

### Before

```
17:34:03 | INFO     | core.secure_config:_find_config_file    | Using local configuration{'config_path': '/.acolyte'}
17:34:03 | INFO     | core.secure_config:_find_config_file    | Using local configuration{'config_path': '/.acolyte'}
17:34:03 | INFO     | core.secure_config:__init__             | Settings initialized{'config_source': '.acolyte'}
17:34:03 | INFO     | api.index:<module>                      | Indexing API initializing...{'module': 'index'}
17:34:03 | INFO     | api.openai:<module>                     | OpenAI API initializing...{'module': 'openai'}
17:34:03 | INFO     | core.secure_config:_find_config_file    | Using local configuration{'config_path': '/.acolyte'}
17:34:03 | INFO     | core.secure_config:_find_config_file    | Using local configuration{'config_path': '/.acolyte'}
17:34:03 | INFO     | core.secure_config:__init__             | Settings initialized{'config_source': '.acolyte'}
17:34:03 | INFO     | api.dream:<module>                      | Dream API initialized{'module': 'dream'}
17:34:03 | INFO     | core.secure_config:_find_config_file    | Using local configuration{'config_path': '/.acolyte'}
17:34:03 | INFO     | core.secure_config:_find_config_file    | Using local configuration{'config_path': '/.acolyte'}
17:34:03 | INFO     | core.secure_config:__init__             | Settings initialized{'config_source': '.acolyte'}
17:34:04 | INFO     | websockets.progress:<module>            | WebSocket configuration validated{'max_connections': 100, 'heartbeat_interval': 30, 'connection_timeout': 60}
```

### After (proposed)

```
17:34:03 | core.secure_config:_find_config_file    | 🖥️ [BACKEND] Using local configuration      | config_path=/.acolyte
17:34:03 | core.secure_config:_find_config_file    | 🖥️ [BACKEND] Using local configuration      | config_path=/.acolyte
17:34:03 | core.secure_config:__init__             | 🖥️ [BACKEND] Settings initialized           | config_source=.acolyte
17:34:03 | api.index:<module>                      | 📁 [INDEX]   Indexing API initializing...   | module=index
17:34:03 | api.openai:<module>                     | 🤖 [OPENAI]  OpenAI API initializing...     | module=openai
17:34:03 | core.secure_config:_find_config_file    | 🖥️ [BACKEND] Using local configuration      | config_path=/.acolyte
17:34:03 | core.secure_config:_find_config_file    | 🖥️ [BACKEND] Using local configuration      | config_path=/.acolyte
17:34:03 | core.secure_config:__init__             | 🖥️ [BACKEND] Settings initialized           | config_source=.acolyte
17:34:03 | api.dream:<module>                      | 🌙 [DREAM]   Dream API initialized          | module=dream
17:34:03 | core.secure_config:_find_config_file    | 🖥️ [BACKEND] Using local configuration      | config_path=/.acolyte
17:34:03 | core.secure_config:_find_config_file    | 🖥️ [BACKEND] Using local configuration      | config_path=/.acolyte
17:34:03 | core.secure_config:__init__             | 🖥️ [BACKEND] Settings initialized           | config_source=.acolyte
17:34:04 | websockets.progress:<module>            | 🔗 [WS]      WebSocket configuration validated | max_connections=100, heartbeat_interval=30, connection_timeout=60
```

---

## Emoji legend (final selection)

- 📁 **[INDEX]**: Indexing, file/collection operations
- 🖥️ **[BACKEND]**: Backend, configuration, startup
- ⏳ **[PROGRESS]**: Task progress, steps, percentages
- 🧩 **[ENRICH]**: Enrichment, extra processing
- 🤖 **[IA]**: AI/LLM/OpenAI calls
- 🌙 **[DREAM]**: Dream module, analysis, generation
- 🔗 **[WS]**: WebSocket, real-time connections
- 🧮 **[DB]**: Database, queries, storage
- 🌐 **[API]**: API endpoints, HTTP/REST
- 🧠 **[NEURAL]**: Neural graph, neural network, graph operations
- ⚠️ **[WARN]**: Warnings
- ❌ **[ERROR]**: Critical errors
- ✅ **[SUCCESS]**: Successful operations
- 🔒 **[SECURITY]**: Security, authentication, permissions
- 🚀 **[PERF]**: Performance, metrics, timings
- 🧪 **[TEST]**: Tests, unit/integration

---

> Continúa este formato para cada tipo de log relevante. Si necesitas más ejemplos, dime qué líneas quieres transformar.
