
# Logita

**Logita** es una utilidad ligera y personalizable de logging en Python diseñada para mejorar la impresión de mensajes en consola exclusivamente, con soporte para colores opcionales y manejo de contexto para uso con `with`.

## Características

- Imprime mensajes de log con timestamp en la consola.
- Soporte para múltiples niveles de log: `debug`, `info`, `success`, `warning`, `error`, `critical` y `exception`.
- Salida con colores opcionales usando `colorama`.
- No usa logging a archivos, solo consola para mayor simplicidad.
- Permite impresión con o sin salto de línea (`line=False`).
- Soporte para uso con contexto (`with`).

## Instalación

```bash
pip install logita
```

Asegúrate de tener `colorama` instalado:

```bash
pip install colorama
```

## Uso

```python
from logita import Logita

with Logita(use_colors=True) as log:
    log.info("Mensaje informativo")
    log.success("Operación exitosa")
    log.warning("Advertencia importante")
    log.error("Ocurrió un error")
    log.debug("Detalles para debugging", line=False)
    log.debug(" -> continuación sin salto de línea")
    log.critical("Problema crítico")
    log.exception("Excepción ocurrida")
```

## Parámetros del constructor

- `use_colors` (bool): Indica si se usan colores en la consola (por defecto `True`).

## Licencia

MIT License
