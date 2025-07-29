# Auditoría de Calidad de Código: Análisis de Código Muerto y Consistencia del Sistema

## Objetivo

Realizar un análisis estático exhaustivo del proyecto para identificar código muerto, verificar consistencia con las dependencias declaradas, y detectar duplicación funcional siguiendo los patrones establecidos.

## Archivos de Referencia

- **Especificación del Sistema**: pyproject.toml / requirements.txt
- **Patrones del Proyecto**: docs/PROMPT_PATTERNS.md
- **Arquitectura**: docs/ARCHITECTURE*DECISION*\*.md
- **Esquemas**: src/acolyte/core/database_schemas/schemas.sql
- **Tipos**: src/acolyte/types.py (si existe)

## Tareas de Análisis

### 1. Detección de Código Muerto

**Identificar y categorizar**:

```python
# Funciones/métodos nunca llamados
def funcion_abandonada():  # ❌ Sin referencias
    pass

# Imports no utilizados
from typing import Protocol  # ❌ Importado pero no usado

# Clases huérfanas
class ModeloViejo:  # ❌ Definida pero nunca instanciada
    pass

# Ramas muertas
if False:  # ❌ Código inalcanzable
    ejecutar_algo()

# Decoradores obsoletos
@deprecated  # ❌ Decorador que ya no aplica
def metodo():
    pass
```

### 2. Verificación de Consistencia con Dependencias

**Para cada dependencia en pyproject.toml**:

```yaml
# Si usa Pydantic v2+:
- Verificar modelos complejos tienen .pyi si:
    - Usan validators personalizados
    - Tienen model_config con extras
    - Usan Generic types
    - Tienen forward references

# Si usa SQLAlchemy/SQLite:
- Verificar que schemas.sql coincide con modelos
- Buscar queries SQL hardcodeadas fuera de services
- Validar que FetchType se use consistentemente

# Si usa FastAPI:
- Verificar que todos los endpoints tienen type hints
- Buscar respuestas sin modelo Pydantic
- Validar dependency injection correcta
```

### 3. Detección de Duplicación Funcional

**Buscar implementaciones redundantes**:

```python
# EJEMPLO: Si existe esto...
class ConversationService:
    def save_message(self, content: str):
        # guarda en BD
        pass

# NO debería existir esto:
class ChatManager:
    def store_message(self, text: str):
        # hace lo mismo
        pass
```

**Patrones a buscar**:

- Misma lógica con nombres diferentes
- Utilidades duplicadas (ej: format_date en múltiples lugares)
- Validadores redundantes
- Conversiones de tipos repetidas
- Manejo de errores inconsistente

### 4. Validación de Patrones del Proyecto

**Verificar adherencia a PROMPT_PATTERNS.md**:

```python
# ✅ CORRECTO - Según patrones
logger.info("Procesando archivo", file_path=path, count=10)

# ❌ INCORRECTO - No sigue el patrón
logger.info(f"Procesando archivo {path} con {10} items")
```

**Verificar**:

- Logging estructurado (NO f-strings)
- Lazy loading correcto
- Uso de MetricsCollector sin namespace
- execute_async con FetchType
- Retry logic donde corresponde

### 5. Análisis de Imports y Dependencias

**Verificar estructura de imports**:

```python
# ❌ MAL - Import pesado a nivel módulo
import torch
import transformers

# ✅ BIEN - Lazy loading
def _load_model(self):
    if self._model is None:
        import torch
        self._model = torch.load(...)
```

### 6. Consistencia de Tipos y Esquemas

**Comparar**:

- Tipos en código Python vs esquemas SQL
- Modelos Pydantic vs API responses
- Type hints vs implementación real
- Enums consistentes en todo el proyecto

## Formato de Salida

```yaml
codigo_muerto:
  funciones_sin_uso:
    - modulo: "src/acolyte/utils/helpers.py"
      funcion: "format_old_date"
      linea: 142
      ultima_modificacion: "2024-01-15"
      confianza: 0.95

  imports_sin_uso:
    - archivo: "src/acolyte/services/chat.py"
      import: "from typing import Protocol"
      linea: 7

  clases_huerfanas:
    - archivo: "src/acolyte/models/legacy.py"
      clase: "OldProcessor"
      referencias: 0

problemas_consistencia:
  dependencias_fantasma:
    - codigo_usa: "import redis"
      no_en: "pyproject.toml"
      archivos: ["cache.py", "queue.py"]

  versiones_incompatibles:
    - paquete: "pydantic"
      instalado: "2.5.0"
      codigo_espera: "1.10.0" # usa BaseModel.dict()

  modelos_sin_stubs:
    - modelo: "ComplexModel"
      archivo: "models/complex.py"
      requiere_pyi: true
      razon: "Usa validators complejos"

duplicacion_funcional:
  - categoria: "Validación de emails"
    implementaciones:
      - ubicacion: "validators/email.py::validate_email()"
        uso: 5
      - ubicacion: "models/user.py::User.check_email()"
        uso: 2
    similitud: 0.92
    recomendacion: "Consolidar en validators.email"

  - categoria: "Formateo de fechas"
    implementaciones:
      - ubicacion: "utils/time.py::format_timestamp()"
      - ubicacion: "services/conversation.py::_format_date()"
      - ubicacion: "api/responses.py::date_to_string()"
    recomendacion: "Crear datetime_utils unificado"

violaciones_patrones:
  logging_incorrecto:
    - archivo: "services/indexing.py"
      linea: 234
      actual: 'logger.info(f"Indexed {count} files")'
      esperado: 'logger.info("Indexed files", count=count)'

  imports_pesados_globales:
    - archivo: "embeddings/unixcoder.py"
      imports: ["torch", "transformers"]
      debe_ser: "lazy loading en métodos"

  metricas_con_namespace:
    - archivo: "services/chat.py"
      actual: 'MetricsCollector(namespace="chat")'
      esperado: "MetricsCollector()"

inconsistencias_tipos:
  sql_vs_python:
    - tabla: "conversations"
      campo: "metadata"
      sql_tipo: "TEXT"
      python_tipo: "Dict[str, Any]"
      problema: "No hay serialización explícita"

  pydantic_vs_api:
    - modelo: "SessionResponse"
      campo: "created_at"
      pydantic: "datetime"
      api_retorna: "str"
      falta: "json_encoders en ConfigDict"

estadisticas:
  total_archivos: 127
  archivos_analizados: 127
  codigo_muerto_lineas: 342
  duplicacion_porcentaje: 8.5
  cobertura_tipos: 87.3
  adherencia_patrones: 91.2
```

## Prioridades de Corrección

1. **🔴 CRÍTICO**:

   - Código que viola patrones de seguridad
   - Inconsistencias de tipos que pueden causar runtime errors
   - Duplicación en lógica crítica de negocio

2. **🟡 ALTO**:

   - Código muerto en hot paths
   - Dependencias fantasma
   - Logging con f-strings (pierde estructura)

3. **🟢 MEDIO**:

   - Duplicación de utilidades
   - Imports no lazy en módulos secundarios
   - Modelos sin .pyi

4. **⚪ BAJO**:
   - Código muerto en tests/debug
   - Comentarios TODO antiguos

## Consideraciones Especiales

- **Preservar**: Código marcado con `# TODO:`, `# DEPRECATED:`, `# LEGACY:`
- **Verificar**: Imports dinámicos y metaprogramming
- **Ignorar**: Código en `__pycache__`, `.venv`, `node_modules`
- **Contexto**: Este es un sistema mono-usuario, priorizar simplicidad

## Comandos para Ejecutar

```bash
# Antes del análisis, actualizar dependencias
pip install vulture mypy pyright

# Generar reporte completo
python -m audit_tool --config=pyproject.toml --patterns=docs/PROMPT_PATTERNS.md

# Solo código muerto
python -m audit_tool --only-dead-code

# Solo consistencia
python -m audit_tool --only-consistency
```

### 💡 Ejemplo de uso específico:

```markdown
Por favor, analiza el proyecto ACOLYTE enfocándote en:

1. **Código muerto en servicios principales** (src/acolyte/services/)
2. **Duplicación entre** ConversationService y ChatService
3. **Consistencia de logging** - todos deben usar kwargs, NO f-strings
4. **Lazy loading** - torch y transformers NUNCA a nivel módulo
5. **job_states vs runtime_state** - verificar que se use cada uno correctamente según docs/ARCHITECTURE_DECISION_runtime_vs_jobstates.md

Prioriza problemas en el core del sistema sobre utilidades secundarias.
```
