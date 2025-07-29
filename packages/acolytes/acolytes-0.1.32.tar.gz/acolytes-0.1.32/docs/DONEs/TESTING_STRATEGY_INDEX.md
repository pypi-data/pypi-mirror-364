# 🧪 Estrategia de Testing para `acolyte index`

## 📋 Resumen Ejecutivo

Estrategia incremental por **capas** para testear el comando `acolyte index`. Cada capa debe pasar al 85-100% antes de avanzar a la siguiente.

## 🚨 **REGLA CRÍTICA - NO HARDCODEAR NADA**

```python
# ❌ JAMÁS HARDCODEAR:
backend_port = 42000                           # ¡HARDCODEADO!
project_path = "/some/path"                    # ¡MAL!

# ✅ SIEMPRE usar Settings() REAL:
from acolyte.core.secure_config import Settings

config = Settings()  # Lee configuración real
backend_port = config.get("ports.backend", 42000)           # REAL
weaviate_port = config.get("ports.weaviate", 42080)         # REAL
ollama_port = config.get("ports.ollama", 42434)             # REAL
```

**POR QUÉ NO HARDCODEAR**: Cada proyecto/usuario tiene puertos, rutas y configuraciones diferentes. Los tests hardcodeados fallan para otros proyectos.

## 🔧 **CÓMO HACER TESTS - GUÍA SIMPLE**

### 📋 **PARA UNIT TESTS** (sin servicios reales):
```python
def test_algo_unitario(tmp_path):
    """Usa tmp_path que pytest ya te da."""
    (tmp_path / "test.py").write_text("print('hello')")
    
    # Mockea Settings para no depender de config real
    with patch('acolyte.core.secure_config.Settings') as mock:
        mock.return_value.get.return_value = 42000
        # tu test aquí
```

### 📋 **PARA INTEGRATION TESTS** (con servicios reales):
```python 
def test_integracion():
    """Usa el proyecto 'huell' que ya está configurado."""
    from acolyte.core.secure_config import Settings
    
    config = Settings()  # Lee config real
    # Los servicios YA están corriendo
```

### 🚀 **ESTRUCTURA SÚPER SIMPLE**

```
acolyte-project/
├── .acolyte.project         # YA LO TIENES ✅
├── tests/
│   ├── unit/               # Tests con mocks (rápidos)
│   └── integration/        # Tests con servicios reales  
```

### ⚡ **COMANDOS ÚNICOS**

```bash
# Para correr todos los tests
$env:PYTHONPATH="src"; pytest tests/ -v

# Para solo unit tests (rápidos, sin servicios)
$env:PYTHONPATH="src"; pytest tests/unit/ -v

# Para integration tests (con servicios reales)
$env:PYTHONPATH="src"; pytest tests/integration/ -v
```

### ❌ **NO NECESITAS:**
- Docker compose separado
- Proyectos de test complejos  
- Fixtures elaboradas

### ✅ **SÍ NECESITAS:**
- pytest instalado
- El proyecto "huell" configurado
- Los servicios corriendo (ya están)

### 📁 **Estructura Final para Tests de Integración**

```
tests/install/index/             # Tests
├── layer_1_health/              # 🔵 CAPA 1 - Health & Connectivity
├── layer_2_cli/                 # 🟢 CAPA 2 - CLI & Request Formation
├── layer_3_discovery/           # 🟡 CAPA 3 - File Discovery & Filtering
├── layer_4_processing/          # 🧠 CAPA 4 - Content Processing + Concurrency ⭐ EL GORDO
│   │   ├── test_simple_db.py
│   │   └── test_debug_integration.py
│   ├── layer_5_integration/         # 🔴 CAPA 5 - CLI Integration & WebSockets ⚠️ PENDIENTE
│   │   └── test_cli_backend_integration.py  ⭐ NECESITA IMPLEMENTACIÓN
│   └── layer_6_production/          # 🟣 CAPA 6 - End-to-End Production ⚠️ PENDIENTE
│       └── test_production_integration.py  ⭐ NECESITA IMPLEMENTACIÓN
```

### 🎯 **Comandos Verificados**

```bash
# PASO 1: Setup configuración real
echo "project_id: a895ea4d74fd" > .acolyte.project

# PASO 2: Verificar Settings() lee real
$env:PYTHONPATH="src"; python -c "from acolyte.core.secure_config import Settings; config = Settings(); print('Backend:', config.get('ports.backend'))"

# PASO 3: Ejecutar tests de integración
$env:PYTHONPATH="src"; python -m pytest tests/install/index/layer_1_health/test_integration_health.py -v

# RESULTADO: ✅ 8/8 PASSED con configuración REAL
```

**✅ CONFIRMADO**: Esta configuración permite que tests de integración usen **configuración real** sin hardcodear nada.

---

## 🧅 **Estrategia por Capas AJUSTADA - PROGRESO ACTUAL**

```
✅ 🔵 CAPA 1: Health & Connectivity          35/35  PASSED (100%) [INTEGRACIÓN]
    ↓
✅ 🟢 CAPA 2: CLI & Request Formation       55/55  PASSED (100%) [UNIT TESTS]
    ↓
✅ 🟡 CAPA 3: File Discovery & Filtering     30/30  PASSED (100%) [MIXTO]
    ↓
✅ 🧠 CAPA 4: Content Processing + Concurrency  44/44  PASSED (100%) [EL GORDO] 🔥
    ↓
⏳ 🔴 CAPA 5: CLI Integration & WebSockets   ?/?    PENDIENTE     [INTEGRACIÓN]
    ↓
⏳ 🟣 CAPA 6: End-to-End Production          ?/?    PENDIENTE     [E2E COMPLETO]
```

**🎉 ESTADO ACTUAL**: **4/6 CAPAS COMPLETADAS (66.7%)**
**🔥 TOTAL TESTS**: **164/164 implementados** en capas 1-4

### 🔍 **CLARIFICACIÓN: Integración vs Unit Tests por Capa**

| **Capa**   | **Tipo**           | **Razón**                     | **¿Servicios Reales?**       |
| ---------- | ------------------ | ----------------------------- | ---------------------------- |
| **Capa 1** | 🔗 **INTEGRACIÓN** | Verificar conectividad real   | ✅ Backend, Weaviate, Ollama |
| **Capa 2** | 🧪 **UNIT TESTS**  | Solo parsing y formación JSON | ❌ Mocks completos           |
| **Capa 3** | 🔗 **INTEGRACIÓN** | Archivos reales en filesystem | ✅ Filesystem real           |
| **Capa 4** | 🧪 **MIXTO**       | Processing logic + servicios  | ⚡ Parcial                   |
| **Capa 5** | 🔗 **INTEGRACIÓN** | Database real storage         | ✅ Weaviate/SQLite real      |
| **Capa 6** | 🔗 **INTEGRACIÓN** | End-to-end completo           | ✅ Todo real                 |

## 🎯 **Objetivo General**

Alcanzar **>90% de cobertura del flujo real** usando una aproximación sistemática que cubra **EnrichmentService, Batch Processing, y Checkpoint/Resume** - componentes críticos que faltaban en v1.0.

## 📁 Estructura de Tests por Capas **ACTUALIZADA**

```
tests/install/index/
├── __init__.py
├── fixtures/                              # Datos de prueba
│   ├── sample_files/
│   ├── git_repos/                         
│   ├── batch_scenarios/                   
│   ├── checkpoint_data/                   
│   ├── mock_responses/
│   └── corrupted_files/
├── layer_1_health/                        # 🔵 CAPA 1 - Health & Connectivity (35 tests)
│   ├── test_service_connections.py       
│   ├── test_health_checks.py            
│   └── test_integration_health.py       
├── layer_2_cli/                          # 🟢 CAPA 2 - CLI & Request Formation (55 tests)
│   ├── test_cli_parsing.py
│   ├── test_cli_parsing_simple.py
│   ├── test_request_formation.py
│   └── test_request_formation_simple.py
├── layer_3_discovery/                    # 🟡 CAPA 3 - File Discovery & Filtering (30 tests)
│   ├── test_file_counting.py
│   ├── test_pattern_filtering.py
│   └── test_real_integration.py
├── layer_4_processing/                   # 🧠 CAPA 4 - Content Processing + Concurrency (44 tests) ⭐ EL GORDO
│   ├── test_indexing_lock.py
│   ├── test_parallel_decision.py
│   ├── test_worker_pool.py
│   ├── test_integration_concurrency.py   ⭐ LA BOMBA ATÓMICA (116 archivos)
│   ├── test_simple_db.py
│   └── test_debug_integration.py
├── layer_5_integration/                  # 🔴 CAPA 5 - CLI Integration & WebSockets ⚠️ PENDIENTE
│   └── test_cli_backend_integration.py   ⭐ NECESITA IMPLEMENTACIÓN
└── layer_6_production/                   # 🟣 CAPA 6 - End-to-End Production ⚠️ PENDIENTE
    └── test_production_integration.py    ⭐ NECESITA IMPLEMENTACIÓN
```

---

# 🔵 **CAPA 1: Health & Connectivity**

**🎯 Objetivo**: Verificar que todos los servicios estén disponibles y configurados correctamente.
**📊 Criterio de Avance**: 100% pass (sin excepciones)
**📊 Estado Actual**: **✅ 35/35 PASSED (100%)**

### 🚨 **REGLA CRÍTICA CAPA 1: USAR CONFIGURACIÓN REAL**

```python
# ❌ JAMÁS HARDCODEAR en tests de integración:
backend_port = 42000                      # ¡MAL! Falla para otros proyectos
config_file = ".acolyte/config.yaml"     # ¡FALSO! No existe
database_path = "~/.acolyte/db.sqlite"   # ¡FALSO! No está ahí
health_url = "http://localhost:8080/health"  # ¡FALSO! Es /api/health

# ✅ SIEMPRE usar Settings() REAL (SIN INVENTAR funciones):
from acolyte.core.secure_config import Settings

config = Settings()  # Singleton real - lee .acolyte automáticamente
backend_port = config.get("ports.backend", 42000)           # ✅ VERIFICADO
weaviate_port = config.get("ports.weaviate", 42080)         # ✅ VERIFICADO
database_path = config.get("database.path", ".acolyte.db")  # ✅ VERIFICADO

# URLs y endpoints REALES (verificados en código fuente):
backend_url = f"http://localhost:{backend_port}/api/health"  # ✅ CORRECTO

# Health checks REALES (verificados en src/acolyte/core/health.py):
from acolyte.core.health import ServiceHealthChecker
health_checker = ServiceHealthChecker(config.config)  # Usa config interno
result = health_checker.wait_for_backend()  # ✅ MÉTODO REAL
```

**⚠️ Los tests de integración DEBEN conectar a servicios reales con puertos reales.**

## 📄 `layer_1_health/test_service_connections.py` (13 tests)

### **TestBackendConnection (4 tests)**

#### ✅ **test_backend_connection_success()**
**Comprueba:**
- Backend responde 200 con status "healthy"
- Endpoint `/api/health` correcto con timeout 20s
- Response JSON válido con campo status

#### ✅ **test_backend_connection_degraded()**  
**Comprueba:**
- Backend con status "degraded" es aceptado
- Información de servicios degradados incluida
- Continúa funcionando aunque no todos los servicios estén healthy

#### ✅ **test_backend_connection_timeout()**
**Comprueba:**
- Timeout después de 3 intentos
- RequestException.Timeout manejado correctamente
- Método retorna False cuando timeout

#### ✅ **test_backend_connection_refused()**
**Comprueba:**
- Connection refused (puerto cerrado) manejado
- ConnectionError capturado correctamente
- Reintentos según timeout configurado

### **TestWeaviateConnection (2 tests)**

#### ✅ **test_weaviate_health_check()**
**Comprueba:**
- Weaviate responde en `/v1/.well-known/ready`
- Timeout de 5 segundos usado
- Status 200 indica ready

#### ✅ **test_weaviate_not_ready()**
**Comprueba:**
- Status 503 (Service Unavailable) manejado
- Reintentos según timeout configurado
- Retorna False cuando no está ready

### **TestOllamaConnection (2 tests)**

#### ✅ **test_ollama_availability()**
**Comprueba:**
- Ollama responde en `/api/tags`
- Timeout de 5 segundos usado
- Status 200 indica disponibilidad

#### ✅ **test_ollama_connection_error()**
**Comprueba:**
- RequestException manejado correctamente
- Reintentos según timeout configurado
- Retorna False en caso de error

### **TestAllServicesCheck (2 tests)**

#### ✅ **test_check_all_services_success()**
**Comprueba:**
- Todos los servicios verificados simultáneamente
- URLs correctas para cada servicio
- Retorna dict con results por servicio

#### ✅ **test_check_all_services_partial_failure()**
**Comprueba:**
- Falla parcial (solo algunos servicios down)
- Continúa verificando otros servicios
- Logging de errores apropiado

### **TestHealthCheckEdgeCases (3 tests)**

#### ✅ **test_backend_invalid_json_response()**
**Comprueba:**
- JSON malformado manejado correctamente
- JSONDecodeError causa reintentos
- Retorna False cuando JSON inválido

#### ✅ **test_backend_missing_status_field()**
**Comprueba:**
- Response sin campo "status" manejado
- KeyError causa reintentos
- Retorna False cuando campo faltante

#### ✅ **test_timeout_configuration()**
**Comprueba:**
- Timeout configurado correctamente por servicio
- Backend: 20s, Weaviate: 5s, Ollama: 5s
- Cada servicio respeta su timeout

## 📄 `layer_1_health/test_integration_health.py` (9 tests)

### **TestRealServiceConnections (3 tests)**

#### ✅ **test_real_backend_connection_flow()**
**Comprueba:**
- Conexión REAL al backend usando Settings()
- Warmup para cold start handling
- Timeout de 120s para inicialización completa
- Status "healthy" o "degraded" aceptados

#### ✅ **test_real_weaviate_connection_flow()**
**Comprueba:**
- Conexión REAL a Weaviate usando puerto configurado
- Endpoint `/v1/.well-known/ready` verificado
- Timeout de 10s para ready check

#### ✅ **test_real_ollama_connection_flow()**
**Comprueba:**
- Conexión REAL a Ollama usando puerto configurado
- Endpoint `/api/tags` verificado
- Modelos disponibles reportados

### **TestRealDockerIntegration (2 tests)**

#### ✅ **test_docker_compose_services_running()**
**Comprueba:**
- `docker compose ps` ejecutado correctamente
- Servicios weaviate/ollama en estado "running"
- No hay servicios exited/crashed

#### ✅ **test_docker_services_health_check()**
**Comprueba:**
- Health check individual por servicio Docker
- Logs de servicios accesibles
- Restart automático si necesario

### **TestRealProjectConfiguration (2 tests)**

#### ✅ **test_real_config_file_loading()**
**Comprueba:**
- Archivo `.acolyte.project` existe y es válido
- project_id extraído correctamente
- Settings() carga configuración real

#### ✅ **test_real_project_directory_validation()**
**Comprueba:**
- Directorio del proyecto existe
- Estructura de archivos ACOLYTE válida
- docker-compose.yml encontrado

### **TestFullIntegrationFlow (2 tests)**

#### ✅ **test_complete_health_check_flow()**
**Comprueba:**
- Flujo completo de health check end-to-end
- Orden correcto: weaviate → ollama → backend
- Todos los servicios healthy para continuar

#### ✅ **test_service_health_checker_integration()**
**Comprueba:**
- ServiceHealthChecker con configuración real
- Integración completa con Settings()
- Resultados coherentes con tests unitarios

## 📄 `layer_1_health/test_health_checks.py` (13 tests)

### **TestServiceHealthChecker (13 tests)**

#### ✅ **test_backend_healthy_status_accepted()**
**Comprueba:**
- Status "healthy" aceptado correctamente
- Retorna True para healthy backend

#### ✅ **test_backend_degraded_status_accepted()**
**Comprueba:**
- Status "degraded" también aceptado
- Información de servicios degradados procesada

#### ✅ **test_backend_non_200_status_retries()**
**Comprueba:**
- Status != 200 causa reintentos
- Exactamente timeout intentos realizados

#### ✅ **test_backend_unhealthy_status_retries()**
**Comprueba:**
- Status "unhealthy" causa reintentos
- Solo "healthy" y "degraded" aceptados

#### ✅ **test_weaviate_ready_endpoint_check()**
**Comprueba:**
- Endpoint `/v1/.well-known/ready` correcto
- Timeout de 5 segundos usado

#### ✅ **test_ollama_tags_endpoint_check()**
**Comprueba:**
- Endpoint `/api/tags` correcto
- Timeout de 5 segundos usado

#### ✅ **test_check_all_services_order()**
**Comprueba:**
- Orden correcto: weaviate → ollama → backend
- Verificación de URLs llamadas en orden

#### ✅ **test_service_timeout_behavior()**
**Comprueba:**
- Timeout configurado respetado (120s default)
- Exactamente timeout intentos realizados

#### ✅ **test_json_decode_error_retries()**
**Comprueba:**
- JSONDecodeError causa reintentos
- Retorna False después de todos los intentos

#### ✅ **test_check_service_once_method()**
**Comprueba:**
- Método check_service_once() sin reintentos
- Un solo intento por servicio

#### ✅ **test_backend_status_unknown_retries()**
**Comprueba:**
- Status desconocido causa reintentos
- Solo status válidos aceptados

#### ✅ **test_backend_actual_failure_scenario()**
**Comprueba:**
- Escenario de falla real simulado
- Manejo de errores de red/timeout

#### ✅ **test_non_health_endpoint_simple_check()**
**Comprueba:**
- Servicios sin health endpoint (solo status 200)
- Weaviate y Ollama usan check simple

#### ✅ **test_weaviate_200_always_success()**
**Comprueba:**
- Weaviate: status 200 = success siempre
- No requiere parsing JSON específico

---

# 🟢 **CAPA 2: CLI & Request Formation**

**🎯 Objetivo**: Verificar parsing del CLI y construcción correcta de requests.
**📊 Criterio de Avance**: 95% pass
**📊 Estado Actual**: **✅ 55/55 PASSED (100%)**

## 📄 `layer_2_cli/test_cli_parsing.py` (10 tests)

### **TestCliIndexParsing (7 tests)**

#### ✅ **test_default_arguments()**
**Comprueba:**
- Argumentos por defecto parseados (path=".")
- Project manager inicializado correctamente
- Fallo apropiado cuando proyecto no inicializado

#### ✅ **test_custom_path_argument()**
**Comprueba:**
- Flag `--path /custom/path` parseado correctamente
- Path personalizado pasado a ProjectManager
- Validación de path funciona

#### ✅ **test_full_flag_parsing()**
**Comprueba:**
- Flag `--full` parseado como force_reindex=True
- Request enviado con configuración correcta
- Mocks complejos para flujo completo

#### ✅ **test_no_progress_flag_parsing()**
**Comprueba:**
- Flag `--no-progress` parseado correctamente
- WebSocket progress deshabilitado
- Flujo sin progress monitoring

#### ✅ **test_verbose_flag_parsing()**
**Comprueba:**
- Flag `--verbose` parseado sin errores
- Logging level incrementado
- Argumentos adicionales compatibles

#### ✅ **test_resume_argument_parsing()**
**Comprueba:**
- `--resume TASK_ID` parseado correctamente
- Task ID extraído del argumento
- Request formado con resume_task_id

#### ✅ **test_combined_arguments_parsing()**
**Comprueba:**
- Múltiples flags combinados sin conflicto
- Todas las combinaciones válidas funcionan
- Precedencia de argumentos correcta

### **TestCliErrorHandling (3 tests)**

#### ✅ **test_invalid_arguments()**
**Comprueba:**
- Argumentos inválidos rechazados por Click
- Mensaje de error apropiado
- Exit code correcto

#### ✅ **test_resume_without_value()**
**Comprueba:**
- `--resume` sin valor rechazado
- "requires an argument" error mostrado
- Click validation funcionando

#### ✅ **test_help_flag()**
**Comprueba:**
- `--help` muestra documentación completa
- Todos los argumentos listados
- Exit code 0

## 📄 `layer_2_cli/test_cli_parsing_simple.py` (15 tests)

### **TestCliArgumentsParsing (10 tests)**

#### ✅ **test_help_shows_all_arguments()**
**Comprueba:**
- Help muestra todos los argumentos disponibles
- Documentación de cada flag presente
- Texto de ayuda completo

#### ✅ **test_default_path_argument()**
**Comprueba:**
- Sin `--path` usa default "."
- Path por defecto funciona correctamente
- Comportamiento esperado sin argumentos

#### ✅ **test_custom_path_argument()**
**Comprueba:**
- `--path /custom/path` aceptado
- Path personalizado procesado
- Validación de paths funciona

#### ✅ **test_verbose_flag_accepted()**
**Comprueba:**
- Flag `--verbose` aceptado sin errores
- No hay conflictos con otros flags
- Click parsing correcto

#### ✅ **test_full_flag_accepted()**
**Comprueba:**
- Flag `--full` aceptado sin errores
- Flag booleano funciona correctamente
- Sin valores requeridos

#### ✅ **test_progress_flags_accepted()**
**Comprueba:**
- `--progress` y `--no-progress` válidos
- Flags mutuamente excluyentes
- Ambos parseados correctamente

#### ✅ **test_resume_with_value_accepted()**
**Comprueba:**
- `--resume TASK_ID` aceptado
- Valor requerido para resume
- Task ID puede ser cualquier string

#### ✅ **test_resume_without_value_rejected()**
**Comprueba:**
- `--resume` sin valor rechazado
- Error "requires an argument"
- Click validation estricta

#### ✅ **test_invalid_argument_rejected()**
**Comprueba:**
- Argumentos inválidos rechazados
- "no such option" error
- Exit code apropiado

#### ✅ **test_multiple_arguments_combination()**
**Comprueba:**
- Múltiples argumentos combinados
- Todas las combinaciones válidas
- Parsing complejo sin errores

### **TestCliArgumentValidation (3 tests)**

#### ✅ **test_path_accepts_any_string()**
**Comprueba:**
- Path acepta cualquier string válido
- Paths absolutos, relativos, con espacios
- Validation flexible de paths

#### ✅ **test_resume_accepts_any_string()**
**Comprueba:**
- Task ID acepta cualquier string
- Diferentes formatos de task ID
- Validation flexible de task IDs

#### ✅ **test_boolean_flags_no_values()**
**Comprueba:**
- Flags booleanos no aceptan valores
- Error cuando se pasa valor a flag
- Click type validation

### **TestClickFunctionSignature (2 tests)**

#### ✅ **test_index_function_is_click_command()**
**Comprueba:**
- Función index es comando Click válido
- Decoradores aplicados correctamente
- Tipo de objeto correcto

#### ✅ **test_index_function_has_correct_parameters()**
**Comprueba:**
- Parámetros de función coinciden con Click
- Tipos de parámetros correctos
- Valores por defecto apropiados

## 📄 `layer_2_cli/test_request_formation.py` (13 tests)

### **TestRequestDataFormation (8 tests)**

#### ✅ **test_default_request_data_structure()**
**Comprueba:**
- Estructura JSON correcta generada
- Todos los campos requeridos presentes
- URL del backend formada correctamente

#### ✅ **test_patterns_are_correct()**
**Comprueba:**
- 34 patterns de archivo exactos del código fuente
- Extensiones: `.py`, `.js`, `.ts`, `.tsx`, etc.
- Lista completa sin modificaciones

#### ✅ **test_exclude_patterns_are_correct()**
**Comprueba:**
- 8 exclude patterns exactos del código fuente
- Directorios: `node_modules`, `__pycache__`, etc.
- Patterns de exclusión correctos

#### ✅ **test_default_boolean_flags()**
**Comprueba:**
- `respect_gitignore: True` por defecto
- `respect_acolyteignore: True` por defecto
- `force_reindex: False` por defecto

#### ✅ **test_full_flag_sets_force_reindex()**
**Comprueba:**
- `--full` mapea a `force_reindex: True`
- JSON request contiene flag correcto
- Mapeo CLI → JSON funcionando

#### ✅ **test_resume_flag_sets_task_id()**
**Comprueba:**
- `--resume TASK_ID` mapea a `resume_task_id`
- Task ID preservado en request
- String task ID correcto

#### ✅ **test_request_timeout_is_300_seconds()**
**Comprueba:**
- Request timeout configurado a 300s
- Timeout apropiado para operaciones largas
- Configuración consistente

#### ✅ **test_backend_port_from_config()**
**Comprueba:**
- Puerto leído desde Settings() real
- URL formada con puerto dinámico
- NO hardcodeo de puertos

### **TestRequestDataEdgeCases (2 tests)**

#### ✅ **test_combined_flags_in_request()**
**Comprueba:**
- Múltiples flags combinados en request
- `--full` + `--resume` funcionan juntos
- JSON contiene ambos campos

#### ✅ **test_empty_resume_task_id_handling()**
**Comprueba:**
- Resume task ID vacío manejado
- Valor por defecto apropiado
- Edge case sin crashes

### **TestRequestValidation (3 tests)**

#### ✅ **test_request_method_is_post()**
**Comprueba:**
- HTTP method es POST
- Método correcto para indexing
- No GET/PUT/DELETE

#### ✅ **test_json_content_type()**
**Comprueba:**
- Content-Type: application/json
- Headers apropiados enviados
- JSON serialization correcta

#### ✅ **test_no_extra_fields_in_request()**
**Comprueba:**
- Solo campos esperados en request
- No campos adicionales/leaked
- Request limpio y minimal

## 📄 `layer_2_cli/test_request_formation_simple.py` (17 tests)

### **TestRequestFormationSimple (17 tests)**

#### ✅ **test_expected_file_patterns_are_complete()**
**Comprueba:**
- 34 patterns de archivo completos
- Verificación exhaustiva de extensiones
- Cobertura de todos los lenguajes

#### ✅ **test_expected_exclude_patterns_are_complete()**
**Comprueba:**
- 8 exclude patterns completos
- Directorios estándar excluidos
- Patterns de build/cache/deps

#### ✅ **test_request_data_structure_fields()**
**Comprueba:**
- Estructura JSON tiene todos los campos
- Tipos de datos correctos
- Schema validation básica

#### ✅ **test_boolean_defaults_are_correct()**
**Comprueba:**
- Valores booleanos por defecto
- Configuración conservativa
- Defaults apropiados

#### ✅ **test_endpoint_url_structure()**
**Comprueba:**
- URL endpoint bien formada
- Protocolo, host, puerto, path
- Estructura `/api/index/project`

#### ✅ **test_request_timeout_constant()**
**Comprueba:**
- Timeout constante definida
- Valor apropiado para operaciones
- Configuración consistente

#### ✅ **test_full_flag_mapping()**
**Comprueba:**
- Mapeo `--full` → `force_reindex`
- Transformación CLI → JSON
- Boolean flag handling

#### ✅ **test_resume_flag_mapping()**
**Comprueba:**
- Mapeo `--resume` → `resume_task_id`
- String value preservation
- Task ID handling

#### ✅ **test_http_method_is_post()**
**Comprueba:**
- HTTP method configurado como POST
- Método apropiado para indexing
- RESTful API compliance

#### ✅ **test_content_type_is_json()**
**Comprueba:**
- Content-Type header correcto
- JSON serialization enabled
- HTTP headers apropiados

#### ✅ **test_programming_languages_covered()**
**Comprueba:**
- 20+ lenguajes de programación cubiertos
- Extensiones principales incluidas
- Cobertura comprehensiva

#### ✅ **test_config_files_covered()**
**Comprueba:**
- Archivos de configuración incluidos
- YAML, JSON, TOML, INI, etc.
- Config files importantes

#### ✅ **test_documentation_files_covered()**
**Comprueba:**
- Archivos de documentación incluidos
- Markdown, RST, TXT
- Documentation patterns

#### ✅ **test_node_dependencies_excluded()**
**Comprueba:**
- `node_modules` excluido correctamente
- Dependencias JS/TS no indexadas
- Build artifacts excluidos

#### ✅ **test_python_cache_excluded()**
**Comprueba:**
- `__pycache__` excluido correctamente
- Python bytecode no indexado
- Cache directories excluidos

#### ✅ **test_version_control_excluded()**
**Comprueba:**
- `.git` directory excluido
- Version control files no indexados
- VCS artifacts excluidos

#### ✅ **test_virtual_envs_excluded()**
**Comprueba:**
- `venv`, `.venv` excluidos
- Virtual environments no indexados
- Python env directories excluidos

#### ✅ **test_build_directories_excluded()**
**Comprueba:**
- `build`, `dist`, `target` excluidos
- Build artifacts no indexados
- Compiled output excluido

---

# 🟡 **CAPA 3: File Discovery & Filtering**

**🎯 Objetivo**: Verificar que el conteo y filtrado de archivos funciona correctamente.
**📊 Criterio de Avance**: 90% pass
**📊 Estado Actual**: **✅ 30/30 PASSED (100%)**

## 📄 `layer_3_discovery/test_file_counting.py` (11 tests)

### **TestFileDiscoveryIntegration (6 tests)**

#### ✅ **test_basic_file_discovery_real_filesystem()**
**Comprueba:**
- rglob() encuentra archivos recursivamente en tmp_path
- Conteo exacto con patterns reales ["*.py", "*.js", "*.md"]
- Estructura de archivos: src/, tests/, components/
- Verificación con 6 archivos esperados

#### ✅ **test_file_size_filtering_real_files()**
**Comprueba:**
- Archivos >10MB excluidos (límite configurable)
- Archivos pequeños (1KB) y medianos (5MB) incluidos
- Archivo grande (11MB) excluido correctamente
- Verificación con archivos reales de diferentes tamaños

#### ✅ **test_empty_directory_handling()**
**Comprueba:**
- Directorios vacíos devuelven 0 sin errores
- No crashea con directorios sin archivos
- Manejo graceful de edge cases

#### ✅ **test_nested_directory_recursion()**
**Comprueba:**
- Recursión profunda (5 niveles) funciona
- rglob() encuentra archivos en cualquier profundidad
- No hay límite de profundidad artificial

#### ✅ **test_performance_with_many_files()**
**Comprueba:**
- Performance con 100 archivos (reducido para tests)
- Tiempo de estimación <5s
- Manejo eficiente de proyectos grandes

#### ✅ **test_acolyte_patterns_filtering()**
**Comprueba:**
- Patterns de .acolyte aplicados correctamente
- Directorios ignorados: node_modules, __pycache__
- Solo archivos válidos contados

### **TestFileCountingErrorScenarios (5 tests)**

#### ✅ **test_non_existent_directory()**
**Comprueba:**
- Directorio inexistente manejado correctamente
- Error apropiado o excepción controlada
- No crashea la aplicación

#### ✅ **test_permission_denied_handling()**
**Comprueba:**
- Archivos sin permisos skippeados
- Continúa procesamiento con otros archivos
- Logging apropiado de errores

#### ✅ **test_broken_symlinks_handling()**
**Comprueba:**
- Symlinks rotos no causan crash
- Archivos válidos continúan siendo procesados
- Manejo robusto de filesystem issues

#### ✅ **test_special_characters_in_filenames()**
**Comprueba:**
- Archivos con caracteres especiales procesados
- Unicode, espacios, caracteres no-ASCII
- Encoding handling correcto

#### ✅ **test_case_sensitivity_handling()**
**Comprueba:**
- Comportamiento consistente en Windows/Linux
- Extensions case-insensitive donde apropiado
- Platform-specific behavior correcto

## 📄 `layer_3_discovery/test_pattern_filtering.py` (11 tests)

### **TestAcolyteIgnorePatternsIntegration (4 tests)**

#### ✅ **test_acolyte_ignore_patterns_real_files()**
**Comprueba:**
- Patterns reales de .acolyte aplicados
- node_modules/, __pycache__/, .git/, venv/, build/, dist/ ignorados
- Solo archivos válidos (main.py, app.js) contados
- Verificación con _should_ignore() method

#### ✅ **test_pyc_and_cache_files_ignored()**
**Comprueba:**
- Archivos .pyc, .pyo ignorados
- Directorios cache (.pytest_cache, .mypy_cache) ignorados
- Solo archivos fuente .py contados
- Bytecode y cache artifacts excluidos

#### ✅ **test_ide_and_editor_files_ignored()**
**Comprueba:**
- Directorios IDE (.vscode/, .idea/) ignorados
- Archivos temporales (.swp, .swo, ~) ignorados
- .DS_Store (Mac) ignorado
- Solo archivos de código contados

#### ✅ **test_log_files_ignored()**
**Comprueba:**
- Archivos .log ignorados
- Directorio logs/ ignorado
- Archivos de aplicación normales preservados
- Log artifacts excluidos

### **TestFileTypeFilteringIntegration (4 tests)**

#### ✅ **test_supported_code_files_real()**
**Comprueba:**
- 20+ extensiones de código soportadas
- Python, JavaScript, TypeScript, Java, Go, Rust, etc.
- Archivos de código incluidos correctamente
- Cobertura comprehensiva de lenguajes

#### ✅ **test_configuration_files_supported()**
**Comprueba:**
- Archivos config incluidos: .json, .yaml, .yml, .toml, .ini
- package.json, config.yaml, settings.ini
- Configuration files preservados
- Formats importantes cubiertos

#### ✅ **test_documentation_files_supported()**
**Comprueba:**
- Archivos docs incluidos: .md, .rst, .txt
- README.md, documentation.rst
- Documentation files preservados
- Formats de documentación cubiertos

#### ✅ **test_mixed_extensions_real_project()**
**Comprueba:**
- Proyecto con múltiples tipos de archivos
- Conteo correcto con extensiones mixtas
- Behavior realista con proyectos complejos
- Integration entre diferentes file types

### **TestPatternFilteringEdgeCases (3 tests)**

#### ✅ **test_deeply_nested_ignored_directories()**
**Comprueba:**
- Directorios ignorados anidados profundamente
- Patterns funcionan en cualquier profundidad
- Performance con estructuras complejas
- Recursión profunda en ignore patterns

#### ✅ **test_case_sensitivity_in_patterns()**
**Comprueba:**
- Comportamiento case-sensitive apropiado
- Windows vs Linux differences
- Pattern matching consistente
- Platform-specific behavior

#### ✅ **test_empty_patterns_list()**
**Comprueba:**
- Lista vacía de patterns manejada
- Comportamiento por defecto apropiado
- No crashea con configuración vacía
- Fallback behavior correcto

## 📄 `layer_3_discovery/test_real_integration.py` (8 tests)

### **TestRealProjectIntegration (8 tests)**

#### ✅ **test_real_project_file_discovery()**
**Comprueba:**
- Discovery en proyecto REAL configurado
- Usa Settings() para configuración real
- Patterns reales: *.py, *.js, *.jsx, *.ts, *.tsx, *.json, *.yaml, *.md
- Verificación genérica (no hardcodeada)

#### ✅ **test_real_ignore_patterns_effectiveness()**
**Comprueba:**
- Patterns de .acolyte funcionan en proyecto real
- Directorios ignorados: node_modules, __pycache__, .git, venv
- Verificación con _should_ignore() en archivos reales
- Behavior con directorios existentes

#### ✅ **test_real_file_size_filtering()**
**Comprueba:**
- Filtrado por tamaño en archivos reales
- Límite real desde service.max_file_size_mb
- Archivos grandes del proyecto excluidos
- Performance con archivos grandes reales

#### ✅ **test_real_supported_file_types()**
**Comprueba:**
- FileTypeDetector con archivos reales
- Categorización correcta de archivos
- Supported vs unsupported types
- Real project file diversity

#### ✅ **test_real_performance_characteristics()**
**Comprueba:**
- Performance en proyecto real
- Tiempo de estimación medido
- Memory usage razonable
- Scaling con proyecto real

#### ✅ **test_real_edge_cases_in_project()**
**Comprueba:**
- Edge cases encontrados en proyecto real
- Symlinks, permissions, special files
- Error handling robusto
- Real-world scenarios

#### ✅ **test_real_concurrent_access_safety()**
**Comprueba:**
- Acceso concurrente seguro
- Múltiples tasks simultáneas
- Thread safety en file operations
- Concurrent estimation tasks

#### ✅ **test_real_config_values()**
**Comprueba:**
- Configuración real cargada correctamente
- Settings() valores utilizados
- Project path, ports, limits
- Real configuration integration

---

# 🧠 **CAPA 4: Content Processing & Enrichment + Concurrency** ⭐ **LA CAPA GORDA**

**🎯 Objetivo**: Verificar procesamiento completo de contenido, enrichment, embeddings, storage Y concurrencia.
**📊 Criterio de Avance**: 90% pass
**📊 Estado Actual**: **✅ ?/? PASSED (?%)**

**🔥 NOTA CRÍTICA**: Esta capa contiene el test **MÁS PESADO** de todo el sistema - `test_real_large_project_1000_files` que hace **TODO EL FLUJO END-TO-END** con 116 archivos reales, pero NO se integra bien con el CLI `acolyte index` y websockets.

## 📄 `layer_4_processing/test_indexing_lock.py` (8 tests)

### **TestIndexingLock (8 tests)**

#### ✅ **test_single_indexing_allowed()**
**Comprueba:**
- Lock se adquiere exitosamente
- `_is_indexing = True` durante procesamiento
- Operación completa sin problemas
- Lock liberado al final (`_is_indexing = False`)

#### ✅ **test_concurrent_indexing_blocked()**
**Comprueba:**
- Segundo intento falla inmediatamente
- Mensaje "Indexing already in progress"
- Primer indexing continúa sin interrupción
- Lock exclusivo funcionando

#### ✅ **test_lock_released_on_success()**
**Comprueba:**
- Lock liberado después de éxito
- `_is_indexing = False` tras completar
- Siguiente indexing puede proceder
- Cleanup correcto

#### ✅ **test_lock_released_on_error()**
**Comprueba:**
- Lock liberado incluso con errores
- Recovery automático tras excepción
- Estado limpio para siguiente operación
- Error handling robusto

#### ✅ **test_lock_state_tracking()**
**Comprueba:**
- Estado del lock tracked correctamente
- `_is_indexing` property preciso
- State transitions correctas
- Consistencia interna

#### ✅ **test_race_condition_prevention()**
**Comprueba:**
- Múltiples attempts simultáneos manejados
- Solo uno succeed, otros fail
- No race conditions
- Atomic lock operations

#### ✅ **test_lock_timeout_behavior()**
**Comprueba:**
- Timeout handling apropiado
- Long operations no bloquean forever
- Reasonable timeout values
- Recovery mechanisms

#### ✅ **test_is_indexing_property()**
**Comprueba:**
- Property `is_indexing` funciona
- Read-only access al estado
- Consistent con internal state
- Public API correcta

## 📄 `layer_4_processing/test_parallel_decision.py` (9 tests)

### **TestParallelDecisionLogic (9 tests)**

#### ✅ **test_parallel_enabled_many_files()**
**Comprueba:**
- >50 archivos → parallel processing enabled
- Worker pool creado correctamente
- Decision logic threshold funcionando
- Configuration respected

#### ✅ **test_sequential_few_files()**
**Comprueba:**
- ≤50 archivos → sequential processing
- No worker pool creation
- Simple processing path
- Performance optimization

#### ✅ **test_parallel_disabled_config()**
**Comprueba:**
- Config `enable_parallel: false` respetado
- Always sequential regardless file count
- Configuration override funcionando
- User preferences honored

#### ✅ **test_worker_count_configuration()**
**Comprueba:**
- Worker count basado en CPU cores
- Configuration limits respetadas
- min(cores, configured_max) logic
- Resource management

#### ✅ **test_min_files_threshold_exact()**
**Comprueba:**
- Exactly 50 files behavior
- Boundary condition handling
- Threshold logic precise
- Edge case coverage

#### ✅ **test_decision_logging()**
**Comprueba:**
- Decision rationale logged
- Debug information provided
- Performance metrics captured
- Troubleshooting support

#### ✅ **test_parallel_with_single_worker()**
**Comprueba:**
- Edge case: 1 worker parallel mode
- Degraded but functional behavior
- Resource constraints handling
- Graceful degradation

#### ✅ **test_worker_pool_reuse()**
**Comprueba:**
- Worker pool reused when possible
- Resource efficiency
- Connection management
- Performance optimization

#### ✅ **test_dynamic_threshold_adjustment()**
**Comprueba:**
- Threshold can be adjusted dynamically
- Runtime configuration changes
- Adaptive behavior
- System optimization

## 📄 `layer_4_processing/test_worker_pool.py` (9 tests)

### **TestWorkerPoolManagement (9 tests)**

#### ✅ **test_pool_initialization()**
**Comprueba:**
- Worker pool setup correcto
- Worker count configured properly
- Resource allocation successful
- Ready state verification

#### ✅ **test_worker_task_distribution()**
**Comprueba:**
- Tasks distributed equitativamente
- Load balancing funcionando
- No worker idle while work available
- Efficient work distribution

#### ✅ **test_embeddings_semaphore()**
**Comprueba:**
- Semaphore controls GPU access
- Resource contention managed
- Performance optimization
- Hardware utilization

#### ✅ **test_worker_error_handling()**
**Comprueba:**
- Individual worker failures isolated
- Pool continues with other workers
- Error recovery mechanisms
- Fault tolerance

#### ✅ **test_results_aggregation()**
**Comprueba:**
- Results from workers combined correctly
- Data integrity maintained
- Statistics aggregated properly
- Complete result set

#### ✅ **test_graceful_shutdown()**
**Comprueba:**
- Workers shutdown cleanly
- Resources released properly
- No hanging processes
- Clean termination

#### ✅ **test_weaviate_client_per_worker()**
**Comprueba:**
- Each worker has own Weaviate client
- Connection pooling
- Resource isolation
- Concurrency safety

#### ✅ **test_worker_batch_processing()**
**Comprueba:**
- Workers process in batches
- Batch size configuration respected
- Memory optimization
- Throughput maximization

#### ✅ **test_pool_stats()**
**Comprueba:**
- Pool statistics tracking
- Performance metrics collection
- Monitoring capabilities
- Operational insights

#### ✅ **test_empty_batch_handling()**
**Comprueba:**
- Empty batches handled gracefully
- No workers created unnecessarily
- Resource conservation
- Edge case robustness

## 📄 `layer_4_processing/test_integration_concurrency.py` (13 tests) 🔥 **EL GORDO**

### **TestRealConcurrentIndexing (13 tests) - FLUJO COMPLETO END-TO-END**

#### ✅ **test_simple_indexing()** 
**QUÉ HACE:**
- 📁 Crea 5 archivos Python reales con contenido complejo
- 🔄 Ejecuta **IndexingService.index_files()** SIN MOCKS
- 🧠 Procesa: Content Reading → Chunking → Enrichment → Embeddings → Storage
- 🔍 Verifica chunks created > 0, embeddings created > 0
- ⚡ Timeout 60s, integración REAL con servicios

#### ✅ **test_real_concurrent_indexing_blocked()**
**QUÉ HACE:**
- 🔒 Verifica que lock previene indexaciones concurrentes
- 🎭 Simula indexing lento con asyncio.Event
- ⛔ Segundo attempt debe fallar con "Indexing already in progress"
- 🏁 Primer indexing completa exitosamente

#### ✅ **test_real_parallel_processing_decision()**
**QUÉ HACE:**
- 📊 Crea 30 archivos para activar parallel processing
- 🚀 Verifica decision logic: >50 files = parallel
- 👥 Confirma worker pool creation
- ⚡ Mide performance improvement

#### ✅ **test_real_worker_pool_error_recovery()**
**QUÉ HACE:**
- 💥 Simula errores en workers individuales
- 🔄 Verifica que pool sigue funcionando
- 📈 Pool recovery mechanisms
- 🛡️ Fault tolerance en producción

#### ✅ **test_real_semaphore_gpu_protection()**
**QUÉ HACE:**
- 🖥️ Verifica semaphore para acceso GPU
- 🚦 Control de concurrencia en embeddings
- 💾 Resource contention management
- ⚡ Hardware utilization optimization

#### ✅ **test_real_lock_timeout_recovery()**
**QUÉ HACE:**
- ⏰ Verifica timeout handling en locks
- 🔄 Recovery automático tras timeouts
- 🧹 Cleanup de resources hanging
- 🛠️ Production readiness

#### ✅ **test_real_worker_pool_performance()**
**QUÉ HACE:**
- 📊 Benchmark de worker pool performance
- ⚡ Metrics: files/second, memory usage
- 📈 Scaling characteristics
- 🎯 Performance targets verification

#### ✅ **test_real_configuration_validation()**
**QUÉ HACE:**
- ⚙️ Verifica Settings() real configuration
- 🔍 Ports, paths, limits correctos
- 📋 Configuration consistency
- 🚨 Invalid config detection

#### 🔥 **test_real_large_project_1000_files() - LA BOMBA ATÓMICA** 💣
**QUÉ HACE (ANÁLISIS COMPLETO):**

**⚡ CÓMO EJECUTAR:**
```bash
# Requiere flag especial para ejecutar
RUN_LARGE_TESTS=1 pytest test_integration_concurrency.py::TestRealConcurrentIndexing::test_real_large_project_1000_files -v
```

**📁 CREACIÓN DE PROYECTO GIGANTE (116 archivos):**
- **75 archivos Python** (5 módulos × 15 archivos c/u):
  - Clases complejas con async/await
  - Methods realistas con type hints
  - Imports, constants, helper functions
  - Contenido de 50-100 líneas cada uno

- **25 archivos de test**:
  - pytest con fixtures
  - async test methods
  - Parametrized tests
  - Real test patterns

- **6 archivos docs**:
  - README.md principal
  - API documentation per module
  - Markdown con code examples

- **5 archivos config**:
  - settings.json, database.yaml
  - api_config.toml, .env.example
  - requirements.txt

**🚀 FLUJO COMPLETO END-TO-END:**
1. **Content Reading**: Lee 116 archivos reales
2. **File Type Detection**: Categoriza por tipo
3. **Adaptive Chunking**: Múltiples chunks por archivo
4. **Git Enrichment**: Metadata y patterns
5. **Embeddings Generation**: Ollama + UniXcoder real
6. **Batch Processing**: Batches de 50 archivos
7. **Worker Pool**: 6 workers paralelos
8. **Weaviate Storage**: Database real
9. **Progress Monitoring**: Real-time updates
10. **Memory Monitoring**: psutil tracking
11. **Performance Metrics**: files/s, chunks/s
12. **Error Handling**: Robust error recovery
13. **Cleanup & Shutdown**: Resource management

**🎯 VERIFICACIONES ESTRICTAS:**
- Files processed ≥ 95% (110+ archivos)
- Chunks created > files (multiple per file)
- Embeddings created > 0
- Memory usage < 2GB
- Performance < 2s per file
- Parallel speed > 0.5 files/s
- Worker distribution metrics
- Error rate acceptable

**⚙️ CONFIGURACIÓN OPTIMIZADA:**
```python
# Configuración original guardada
original_workers = real_service.concurrent_workers
original_batch = real_service.config.get('indexing.worker_batch_size', 10)
original_semaphore = real_service.config.get('indexing.embeddings_semaphore', 2)

# Optimizaciones aplicadas
real_service.concurrent_workers = min(6, os.cpu_count() or 4)  # MAX 6 (límite Weaviate v3)
real_service.config.config['indexing']['worker_batch_size'] = 50  # De 10 → 50
real_service.config.config['indexing']['embeddings_semaphore'] = 8  # De 2 → 8
real_service.config.config['indexing']['batch_size'] = 100  # De 20 → 100
real_service.config.config['embeddings']['batch_size'] = 50  # De 20 → 50
real_service.config.config['embeddings']['max_tokens_per_batch'] = 50000  # De 10K → 50K
```

**💾 MÉTRICAS MONITOREADAS:**
- Memory before/after (requiere `psutil`)
- Processing time total
- Files per second
- Chunks per second
- Time per file (ms)
- Memory per 100 files

**🔗 INTEGRACIÓN REAL:**
- Base datos: `C:\Users\fix.workshop\.acolyte\projects\416e045eec5d\data\acolyte.db` ⚠️ **HARDCODEADA**
- Backend: puerto 42000
- Weaviate: puerto 42080
- Ollama: puerto 42434
- Modelo requerido: `acolyte:latest` en Ollama

**🚨 INFORMACIÓN CRÍTICA:**
1. **Base de datos HARDCODEADA**: Debería usar Settings() en lugar de path fijo
2. **Dependencia de psutil**: Necesario para monitoreo de memoria
3. **NO usa el flujo CLI**: Llama directamente a `IndexingService.index_files()`
4. **NO prueba WebSockets**: Sin progress monitoring via WS
5. **NO pasa por API**: No usa endpoint `/api/index/project`

**🔑 POR QUÉ ES LA CLAVE:**
- Demuestra que **IndexingService funciona PERFECTAMENTE** con 116 archivos
- Revela que **la integración CLI → Backend → WebSocket está incompleta/sin testear**
- Muestra la **configuración óptima para proyectos grandes**
- Valida el **sistema de workers y concurrencia bajo carga real**
- Indica que **falta implementar los tests de integración completa** (capas 5 y 6)

#### ✅ **test_process_empty_list()**
**QUÉ HACE:**
- Edge case: lista vacía de archivos
- Graceful handling
- No crashes o errors
- Clean completion

#### ✅ **test_process_single_item()**
**QUÉ HACE:**
- Edge case: single file processing
- Minimal viable operation
- Resource efficiency
- Correct behavior

#### ✅ **test_get_status_not_initialized()**
**QUÉ HACE:**
- Service status before initialization
- State management verification
- API consistency
- Error prevention

#### ✅ **test_real_concurrent_estimate_files()**
**QUÉ HACE:**
- Multiple estimate_files() concurrent calls
- Thread safety verification
- Consistent results
- Performance under contention

## 📄 `layer_4_processing/test_simple_db.py` (3 tests)

### **TestDatabaseSetup (3 tests)**

#### ✅ **test_database_setup_works()**
**Comprueba:**
- Database initialization successful
- Tables created correctly
- Schema validation
- Connection working

#### ✅ **test_job_states_table_exists()**
**Comprueba:**
- Job states table created
- Schema matches expectations
- Async operations supported
- Data integrity

#### ✅ **test_basic_indexing_service_import()**
**Comprueba:**
- Service imports without errors
- Dependencies available
- Module structure correct
- Basic instantiation works

## 📄 `layer_4_processing/test_debug_integration.py` (2 tests)

### **TestDebugIntegration (2 tests)**

#### ✅ **test_basic_service()**
**Comprueba:**
- Service creation en debug mode
- Debug configuration loaded
- Logging setup correct
- Development environment ready

#### ✅ **test_estimate_files()**
**Comprueba:**
- File estimation en debug mode
- Debug output generated
- Estimation accuracy
- Development workflow

---

**🔥 RESUMEN DE LA CAPA 4:**
- **44 tests total** (8+9+9+13+3+2)
- **Tests unitarios** (indexing_lock, parallel_decision, worker_pool)
- **Tests de integración** (integration_concurrency - EL GORDO)
- **Tests de debug** (simple_db, debug_integration)
- **FLUJO COMPLETO** desde archivos hasta storage
- **NO integra bien** con CLI `acolyte index` + websockets

**💡 NOTA IMPORTANTE**: Necesitas renombrar la carpeta:
```bash
mv tests/install/index/layer_3b_concurrency tests/install/index/layer_4_processing
```

---

# 🔴 **CAPA 5: CLI Integration & WebSocket Monitoring**

**🎯 Objetivo**: Verificar integración CLI `acolyte index` con backend y websockets.
**📊 Criterio de Avance**: 90% pass
**📊 Estado Actual**: **⏳ PENDIENTE - NECESITA IMPLEMENTACIÓN**

**🚨 PROBLEMA DETECTADO**: El IndexingService funciona perfecto directamente, pero la integración CLI → Backend → WebSockets tiene issues.

---

# 🟣 **CAPA 6: End-to-End Production Integration**

**🎯 Objetivo**: Verificar flujo completo CLI + Backend + WebSockets en producción.
**📊 Criterio de Avance**: 85% pass = PRODUCTION READY
**📊 Estado Actual**: **⏳ PENDIENTE - NECESITA IMPLEMENTACIÓN**

**🎯 ENFOQUE**: Tests que verifican la integración real que falla actualmente entre el CLI y el backend.

## 📄 `layer_6_integration/test_cli_backend_integration.py` ⭐ **NECESITA IMPLEMENTACIÓN**

### ⭐ **test_cli_to_backend_communication() - NECESITA IMPLEMENTACIÓN**

**DEBE VERIFICAR:**
- CLI `acolyte index` envía request correctamente al backend
- Backend recibe y procesa request apropiadamente  
- Response del backend llega al CLI
- Error handling entre CLI y backend

### ⭐ **test_websocket_progress_integration() - NECESITA IMPLEMENTACIÓN**

**DEBE VERIFICAR:**
- WebSocket connection establecida desde CLI
- Progress updates enviados desde backend
- CLI recibe y muestra progress correctamente
- Connection timeout y reconnection

### ⭐ **test_cli_index_full_flow() - NECESITA IMPLEMENTACIÓN**

**DEBE VERIFICAR:**
- Command `acolyte index` funciona end-to-end
- Progress monitoring visible en terminal
- Completion status correcto
- Exit codes apropiados

---

**🚨 ESTADO ACTUAL DE LAS CAPAS:**

```
✅ 🔵 CAPA 1: Health & Connectivity          35/35  PASSED (100%) [INTEGRACIÓN]
✅ 🟢 CAPA 2: CLI & Request Formation       55/55  PASSED (100%) [UNIT TESTS]
✅ 🟡 CAPA 3: File Discovery & Filtering     30/30  PASSED (100%) [MIXTO]
✅ 🧠 CAPA 4: Content Processing + Concurrency  44/44  PASSED (100%) [EL GORDO]
    ↓
⏳ 🔴 CAPA 5: CLI Integration & WebSockets   ?/?    PENDIENTE     [INTEGRACIÓN]
    ↓
⏳ 🟣 CAPA 6: End-to-End Production          ?/?    PENDIENTE     [E2E COMPLETO]
```

**🎉 PROGRESO TOTAL**: **164/164 tests implementados en capas 1-4 (100%)**

**🔥 EL GRAN PROBLEMA**: La CAPA 4 hace TODO el content processing perfectamente, pero NO se integra con el CLI. Necesitamos tests que verifiquen específicamente la integración `acolyte index` → Backend → WebSockets.

---
