# Rediseño de dashboards de Home Assistant con Frosted Glass

## Estado

Propuesta aprobada en conversación. Este documento fija el alcance de la
implementación sobre la configuración viva de Home Assistant.

## Objetivo

Reducir la navegación visible de Home Assistant a cinco dashboards útiles y
coherentes, manteniendo los controles existentes y concentrando la información
de un vistazo:

1. `Inicio`: estado general, tiempo de hoy, cámaras y agenda.
2. `Casa`: habitaciones, luces, persianas, climatización, medios y
   electrodomésticos.
3. `Coche`: Kitt/Tesla y el Wall Connector.
4. `Energía`: consumo actual, diario/mensual, flujos, histórico y cargas.
5. `Sistema`: seguridad, infraestructura, mantenimiento, mapa y cámaras.

La apariencia común será Frosted Glass: superficies translúcidas, desenfoque,
bordes suaves, contraste suficiente y una jerarquía visual compacta. Se
reutilizarán los recursos ya instalados. No se instalarán tarjetas HACS nuevas
como parte de este cambio.

## Situación de partida relevante

La instancia usa dashboards Lovelace almacenados en Storage y dispone de los
recursos Mushroom, card-mod, navbar-card, atomic-calendar-revive,
ha-today-card, vehicle-status-card, Helios y otros recursos ya cargados. Los
dashboards actuales son `map`, `casa`, `seguridad`, `energia`, `coche`,
`mantenimiento` y `panel-comedor`.

Entidades de referencia ya comprobadas:

- Tiempo: `weather.everest` y `weather.forecast_everest`.
- Calendarios: `calendar.casa` y `calendar.trabajo`.
- Cámara de entrada:
  `camera.entrada_joan_fuster_5_high_resolution_channel`.
- Cámara del garaje:
  `camera.g5_turret_ultra_high_resolution_channel`.
- Seguridad: `lock.aqara_smart_lock_u200` y
  `alarm_control_panel.ucg_fiber_alarm_manager`.
- Coche: sensores `sensor.kitt_*`, `binary_sensor.kitt_*` y
  `device_tracker.kitt`.
- Carga: entidades `sensor.tesla_wall_connector_*`.
- Energía: sensores `sensor.energia_*`, `sensor.potencia_*` y la tarjeta
  Helios existente.

Antes de cada escritura se volverán a comprobar las entidades y los hashes,
porque los estados y la configuración viva pueden haber cambiado.

## Arquitectura de navegación

### Dashboards visibles

- Crear `inicio` como dashboard principal y mostrarlo en la barra lateral.
- Renombrar la experiencia visible de `casa` a `Casa` y mostrarla en la barra
  lateral, manteniendo sus vistas de habitaciones y sus rutas existentes.
- Mantener `coche` y `energia` como dashboards especializados, con navegación
  común.
- Crear `sistema` para reunir seguridad, mantenimiento, mapa e infraestructura.

### Dashboards antiguos durante la migración

Después de validar las nuevas rutas, ocultar de la barra lateral `map`,
`seguridad`, `mantenimiento` y `panel-comedor`. No se eliminarán en este lote:
se conservan como rollback hasta comprobar que no quedan enlaces, accesos de
tablet ni controles dependientes. Ocultar estos dashboards reduce la
navegación visible de siete a cinco sin una operación destructiva irreversible.

Las rutas antiguas se conservarán mientras sea posible, y las nuevas tarjetas
de navegación usarán rutas explícitas hacia `inicio`, `casa`, `coche`,
`energia` y `sistema`.

## Composición visual y funcional

### `Inicio`

Orden de lectura vertical:

1. Encabezado compacto con hora, presencia y accesos principales.
2. Bloque de tiempo reducido, limitado al estado actual y la previsión de
   hoy. Se usará el recurso `ha-today-card` si su esquema activo lo permite;
   si no, se usará una tarjeta nativa de tiempo con la mínima información
   equivalente. No se mostrará una previsión de varios días en la portada.
3. Cámaras inmediatamente debajo del tiempo, en una fila responsive. La
   entrada tendrá prioridad visual; el garaje conservará una indicación clara
   si la cámara sigue no disponible, sin inventar imagen ni estado.
4. Calendario estilo agenda/glass, usando `atomic-calendar-revive` con
   `calendar.casa` y `calendar.trabajo`, eventos próximos y vista mensual o
   equivalente sólo si el recurso activo lo soporta. Se mantendrán colores,
   idioma y eventos de todo el día de la tarjeta actual.
5. Resumen de atención: cerradura, alarma, cámara no disponible y estados que
   requieran acción.
6. Accesos rápidos a Casa, Coche, Energía y Sistema.

El tiempo y las cámaras serán bloques separados: el primero será pequeño y
legible; las cámaras quedarán debajo, tal como se pidió.

### `Casa`

Conservar la organización por estancias y controles actuales, pero unificar el
encabezado, la navegación y las superficies Frosted Glass. La primera vista
priorizará acciones y estados útiles; las vistas de cocina, comedor, escaleras,
baños y habitaciones seguirán siendo accesibles. Se eliminarán duplicaciones
visuales, no controles.

### `Coche`

Reordenar la vista para que el estado de Kitt aparezca primero: batería, estado,
ubicación, temperaturas, bloqueo y carga. El Wall Connector aparecerá como
segundo bloque con conexión del vehículo y potencia. Se conservará la tarjeta
especializada `vehicle-status-card` si sus entidades siguen siendo válidas y se
mantendrán sus acciones/rutas actuales.

### `Energía`

Concentrar la información actual en este orden:

1. Potencia de ahora, consumo de hoy y consumo del mes.
2. Flujo entre red, casa, coche y cargas disponibles.
3. Histórico de potencia.
4. Electrodomésticos y lavado únicamente con estados reales.

Se conservará Helios y se reutilizarán sus entidades existentes. Los valores
se tomarán de la configuración y los estados leídos justo antes de escribir;
no se fijarán cifras de ejemplo en YAML.

### `Sistema`

Agrupar en vistas compactas los dominios que hoy están separados:

- Seguridad: alarma, cerradura, presencia, cámaras y detecciones.
- Infraestructura: Home Assistant, UCG Fiber, red y dispositivos con estado
  anómalo.
- Mantenimiento: actualizaciones, copias, salud y tareas pendientes.
- Mapa/cámaras: conservar el mapa y el acceso a las cámaras existentes.

El sistema no repetirá el detalle del dashboard de Energía ni el control de las
habitaciones de Casa.

## Tema y estilos

Primero se verificará si el tema llamado `Frosted Glass` está realmente
disponible en la instancia y cuál es su clave exacta. Si existe, se aplicará
esa clave al dashboard o a las vistas donde Home Assistant lo soporte. Si no
existe como tema seleccionable, se reproducirá el lenguaje visual mediante
`card-mod` y estilos ya instalados, sin crear una falsa referencia de tema ni
instalar dependencias nuevas.

La capa común usará:

- fondos translúcidos y gradientes suaves;
- `backdrop-filter` sólo donde el navegador lo soporte, con fondo opaco de
  respaldo;
- bordes de bajo contraste, radios consistentes y sombras contenidas;
- estados por color sólo como apoyo, acompañados de texto o icono;
- tipografía y espaciado que mantengan legibilidad en tablet y escritorio.

No se aplicará estilo global destructivo a tarjetas que ya tengan controles
funcionales; las reglas se limitarán a las superficies y contenedores nuevos o
reordenados.

## Migración y flujo de datos

1. Leer lista, configuración completa, recursos, temas disponibles y estados
   críticos desde Home Assistant.
2. Capturar el hash de cada dashboard que vaya a cambiar.
3. Generar o transformar cada dashboard con `python_transform` mediante
   `ha_config_set_dashboard`; nunca editar `.storage` directamente.
4. Leer de nuevo cada dashboard y validar vistas, rutas, entidades, acciones y
   ausencia de tarjetas con entidades inventadas.
5. Ocultar los cuatro dashboards antiguos sólo después de que `Inicio` y
   `Sistema` carguen correctamente y la navegación nueva esté comprobada.
6. Recorrer la interfaz en navegador en viewport móvil/tablet y escritorio,
   verificando especialmente tiempo → cámaras → calendario en `Inicio`.

Cada lote será pequeño y reversible. Si falla una tarjeta custom, se preferirá
la tarjeta nativa o la versión ya existente antes que introducir otra
dependencia.

## Verificación y criterios de aceptación

La implementación se considera correcta cuando:

- la barra lateral muestra cinco dashboards útiles y no siete;
- `Inicio` carga sin tarjetas rotas y muestra, en este orden, tiempo compacto,
  cámaras debajo y calendario visible;
- el bloque de tiempo muestra sólo hoy y no ocupa el espacio de una previsión
  semanal;
- `Casa`, `Coche`, `Energía` y `Sistema` mantienen sus entidades y controles
  críticos;
- Kitt, Wall Connector, Helios, alarma, cerradura, cámaras y calendarios
  muestran estados reales o un estado de no disponibilidad explícito;
- las rutas principales y la navegación inferior/superior cargan en móvil y
  escritorio;
- la configuración se lee correctamente después de cada escritura y la
  verificación visual confirma la jerarquía solicitada;
- los dashboards antiguos permanecen recuperables y ocultos, no borrados, en
  este lote.

## Límites

- No se editarán archivos internos `.storage`.
- No se crearán entidades, sensores ni valores simulados.
- No se instalarán recursos HACS.
- No se migrarán automatizaciones, scripts ni helpers.
- No se eliminarán dashboards antiguos hasta un lote posterior y una decisión
  explícita basada en la verificación de uso.
