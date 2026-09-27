# TP3 - Análisis de Proyecto Logístico

## 1. Descripción del proyecto

El proyecto representa un **Diagrama de Red con Actividades en Paralelo**, donde varias tareas pueden realizarse simultáneamente hasta converger en un punto final.

El proceso corresponde a un **pedido online** y presenta las siguientes dependencias:

             ┌── A ──> B ──┐
Inicio ──────┤              ├──> F ──> Fin
             └── C ──> D ──> E ──┘


La actividad **F** depende de que hayan finalizado tanto **B** como **E**.

---

# 2. Matriz de actividades y precedencias

| Código | Actividad    | Descripción | Predecesora |
| ------ | ---------------------------------- | ------------------------------------------------------------------------- | ----------- |
| A      | Verificación de Pago y Stock | El sistema aprueba el cobro y libera la orden.| — |
| B      | Picking en Almacén | Un operario busca el producto en la estantería. | A |
| C      | Impresión de Etiqueta de Envío | El sistema de logística genera la guía de ruta. | — |
| D      | Preparación de Empaque (Packing)   | Se arma la caja y se le adhieren las etiquetas. | C |
| E      | Verificación de Control de Calidad | Se escanea la caja lista para validar pesos y medidas.| D |
| F      | Despacho y Carga al Camión | Se junta el producto (B) con su empaque verificado (E) para salir a ruta.|B y E|

---

# 3. Lógica del diagrama

## 3.1 Ramas en paralelo

Las actividades **A y C pueden comenzar simultáneamente** e independientemente.

Mientras se verifica el pago y stock, el área de sistemas/logística puede imprimir la documentación y preparar el proceso de empaque.

                    ┌── A ──> B ──┐
Inicio ─────────────┤              ├──> F ──> Fin
                    └── C ──> D ──> E ──┘


## 3.2 Secuencias individuales

### Rama del producto
A → B

No se puede realizar el picking del producto hasta que el pago y el stock hayan sido verificados.

### Rama del empaque

```text
C → D → E
```

Primero se imprime la etiqueta, luego se prepara el empaque y finalmente se realiza el control de calidad.

## 3.3 Punto de convergencia

La actividad **F** solamente puede comenzar cuando hayan terminado **B y E**.

B ──┐
    ├──> F
E ──┘


Por lo tanto:

* Si **B** termina pero **E** todavía no, F debe esperar.
* Si **E** termina pero **B** todavía no, F debe esperar.
* F comienza únicamente cuando ambas actividades están finalizadas.

---

# 4. Rutas del proyecto

Al existir dos líneas de trabajo en paralelo, se pueden analizar las siguientes rutas:

## Ruta 1 - Producto

Inicio → A → B → F → Fin


Con los datos fijos del ejemplo:

| Actividad |   Duración |
| --------- | ---------: |
| A         |     15 min |
| B         |     30 min |
| F         |     15 min |
| **Total** | **60 min** |

Por lo tanto:

**Ruta 1 = 60 minutos**

---

## Ruta 2 - Empaque

Inicio → C → D → E → F → Fin


Con los datos fijos del ejemplo:

| Actividad |   Duración |
| --------- | ---------: |
| C         |      5 min |
| D         |     10 min |
| E         |      5 min |
| F         |     15 min |
| **Total** | **35 min** |

Por lo tanto:

**Ruta 2 = 35 minutos**

### Importante

Aunque numéricamente la Ruta 2 suma 35 minutos, el proyecto completo no puede finalizar en 35 minutos porque **F depende simultáneamente de B y E**.

En este ejemplo:

```text
Ruta 1:  A(15) → B(30) ──────────┐
                                  ├→ F(15) → Fin
Ruta 2:  C(5) → D(10) → E(5) ────┘
```

B finaliza a los **45 minutos**.

E finaliza a los **20 minutos**.

Por lo tanto, F comienza cuando B termina, en el minuto **45**, y finaliza en el minuto **60**.

**Duración total del proyecto = 60 minutos.**

Las actividades que forman parte del camino más lento serán consideradas **actividades críticas**.

---

# 5. Simulacro con datos fijos

| Código | Tipo   | Elemento / Actividad                            | Duración | Predecesora |
| ------ | ------ | ----------------------------------------------- | -------: | ----------- |
| Inicio | Evento | Pedido recibido / Confirmación de pedido en Web |    0 min | —           |
| A      | Tarea  | Verificación de Pago y Stock                    |   15 min | Inicio      |
| B      | Tarea  | Picking en Almacén (búsqueda)                   |   30 min | A           |
| C      | Tarea  | Impresión de Etiqueta y Factura                 |    5 min | Inicio      |
| D      | Tarea  | Preparación de Empaque (Packing)                |   10 min | C           |
| E      | Tarea  | Control de Calidad y Pesaje                     |    5 min | D           |
| F      | Tarea  | Despacho y Carga al Camión                      |   15 min | B, E        |
| Fin    | Evento | Pedido Despachado                               |    0 min | F           |

---

# 6. Distribuciones de las variables aleatorias

Para la simulación se deben utilizar las distribuciones propuestas para cada actividad.

## A - Verificación de Pago y Stock

**Distribución:** Constante / Determinística

A = 15 minutos

Probabilidad:
P(A = 15) = 1

Es decir, ocurre durante 15 minutos el **100% de las veces**.

---

## B - Picking en Almacén

**Distribución:** Discreta

Los posibles tiempos son:

| Duración | Probabilidad |
| -------: | -----------: |
|   20 min |         0,25 |
|   30 min |         0,40 |
|   40 min |         0,35 |

Por lo tanto:
B ∈ {20, 30, 40}

con:
P(B = 20) = 0,25
P(B = 30) = 0,40
P(B = 40) = 0,35


---

## C - Impresión de Etiqueta

**Distribución:** Constante / Determinística
C = 5 minutos


---

## D - Preparación de Empaque

**Distribución:** Uniforme
D ~ U[5, 25]


Es decir, la duración puede tomar valores entre:
5 ≤ D ≤ 25 minutos


---

## E - Control de Calidad

**Distribución:** Exponencial

E ~ Exponencial


con media:
Media = 5 minutos


---

## F - Despacho y Carga

La duración depende de la disponibilidad del montacargas.

**Distribución:** Discreta

| Estado del montacargas | Duración | Probabilidad |
| ---------------------- | -------: | -----------: |
| Libre                  |   15 min |         0,50 |
| Ocupado                |   25 min |         0,50 |

Por lo tanto:

P(F = 15) = 0,50
P(F = 25) = 0,50


---

# 7. Resumen de distribuciones

| Actividad | Distribución | Parámetros                                  |
| --------- | ------------ | ------------------------------------------- |
| A         | Constante    | 15 min                                      |
| B         | Discreta     | 20 min (0,25), 30 min (0,40), 40 min (0,35) |
| C         | Constante    | 5 min                                       |
| D         | Uniforme     | U[5, 25]                                    |
| E         | Exponencial  | Media = 5 min                               |
| F         | Discreta     | 15 min (0,50), 25 min (0,50)                |

---

# 8. Simulación del caso

Simular el caso utilizando los datos propuestos para las variables aleatorias.

El desarrollo de la aplicación será grupal, pero su evaluación será individual y, en caso de solicitárselo, deberán subir de manera individual el código desarrollado que utilizó.

---

# 9. Generador Congruencial Mixto

Todas las variables aleatorias deberán utilizar un **Generador Congruencial Mixto individual**, diferente para cada variable.

Los coeficientes serán proporcionados al momento de la evaluación.

Esto permite que la prueba pueda ser replicada.

### Datos de prueba

* **Semilla:** 3922
* **Constante multiplicativa:** 1221
* **Constante aditiva:** 1714
* **Módulo:** número de legajo

Las variables mantendrán la distribución proporcionada, aunque pueden variar:

* Media
* Varianza
* Extremos
* Probabilidades

Estos valores serán proporcionados al inicio de la evaluación.

---

# 10. Restricciones del software

El software solamente debe trabajar con:

* Vector actual
* Vector anterior

La excepción es el uso de Excel.

El programa deberá proporcionar los estimadores requeridos en cada instante o iteración simulada.

### No almacenar tablas de datos

No se deben almacenar tablas de datos, ya que algunos valores solicitados podrían estar vinculados a una iteración específica, por ejemplo:

Simulación Nº 100000


---

# 11. Identificación del modelo

Se deben identificar:

## Variables

Todas las variables que intervienen en el problema.

## Parámetros

Todos los parámetros utilizados por el modelo.

## Variable objetivo

Identificar la variable objetivo del análisis.

## Fórmulas

Identificar las fórmulas necesarias para:

* Generar las variables aleatorias.
* Transformar los números aleatorios según cada distribución.
* Calcular los tiempos de las actividades.
* Calcular los estimadores solicitados.

---

# 12. Estimadores solicitados

## 12.1 Tiempo mínimo del proyecto

Calcular el tiempo de duración del proyecto mediante un simulacro para determinar el **tiempo mínimo en que podría haberse realizado el proceso**.

---

## 12.2 Tiempo de duración de cada proceso

Calcular el tiempo de duración de cada actividad/proceso.

---

## 12.3 Tiempo promedio

Calcular el **tiempo promedio de realización del proceso** hasta la iteración o simulación solicitada.

---

## 12.4 Actividades críticas / cuellos de botella

Para cada actividad, identificar la **proporción de veces** en que:

* La actividad es crítica.
* La actividad puede ser considerada cuello de botella.

---

## 12.5 Tiempo con nivel de confianza del 95%

Simulando **99 veces**, identificar cuál es el tiempo a fijar si queremos completar el proceso antes de ese tiempo con un **nivel de confianza del 95%**.

---

## 12.6 Probabilidad de terminar en 60 minutos o menos

Calcular:
P(T ≤ 60)


Es decir, la probabilidad de terminar el proyecto en **60 minutos o menos**, simulando hasta `n` veces.

---

## 12.7 Probabilidad de terminar en 90 minutos o más

Calcular:

P(T ≥ 90)

Es decir, la probabilidad de terminar el proyecto en **90 minutos o más**, simulando hasta `n` veces.

---

# 13. Distribución de frecuencias

Realizar una **distribución de frecuencia con 10 intervalos**.

### Condiciones

* El extremo inferior del primer intervalo debe ser el **tiempo mínimo calculado**.
* Los primeros **9 intervalos** deben tener igual tamaño.
* El último intervalo comienza **90 minutos después que el primer intervalo**.
* El último intervalo debe contener todas las observaciones restantes.

La cantidad de observaciones será proporcionada durante la evaluación.

---

# 14. Consideraciones para la evaluación

En cualquiera de los valores solicitados, se proporcionarán los datos necesarios para realizar la simulación.

El programa deberá poder adaptarse a los valores proporcionados durante la evaluación.
