# ShiftPlanner

Distribución automática del personal de una fábrica en líneas y turnos, usando [Google OR-Tools](https://developers.google.com/optimization).

## Estructura

```
library/        Funciones del proyecto (modelos, carga de JSON, solver)
tests/          Tests unitarios (pytest); fixtures/ contiene JSON de prueba
data/source/    Datos de entrada: operarios.json, lineas.json
data/output/    Distribuciones generadas (JSON)
main.py         Punto de entrada
```

## Uso

```bash
pip install -r requirements.txt
python main.py
pytest
```
