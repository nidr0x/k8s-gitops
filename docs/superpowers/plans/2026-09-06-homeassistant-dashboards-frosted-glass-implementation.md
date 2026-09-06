# Home Assistant Frosted Glass Dashboards Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convert the live Home Assistant navigation to five visible Frosted Glass dashboards with a compact home overview, today's weather, cameras below it, visible calendar, and preserved domain controls.

**Architecture:** Keep Lovelace dashboards in Storage and use the Home Assistant configuration API. Create `inicio` and `sistema` from verified live entities and existing card configurations, then transform `casa`, `coche`, and `energia` surgically. Hide the four superseded dashboards only after readback and browser verification; keep them available for rollback.

**Tech Stack:** Home Assistant 2026.9.0, Lovelace Storage, `ha_config_get_dashboard`, `ha_config_set_dashboard`, Home Assistant states API, Mushroom, card-mod, navbar-card, atomic-calendar-revive, ha-today-card, vehicle-status-card, Helios, and browser rendering.

**Spec:** `docs/superpowers/specs/2026-09-06-homeassistant-dashboards-frosted-glass-design.md`

## Global Constraints

- Read the live dashboard configuration and `config_hash` immediately before every write batch.
- Write dashboard changes only through `ha_config_set_dashboard`; never edit Home Assistant `.storage` files.
- Use only entity IDs returned by Home Assistant; never invent sensors, values, routes, or card-resource URLs.
- Reuse currently registered resources before considering any new dependency.
- Preserve existing controls and room routes in `casa`, vehicle actions in `coche`, Helios and energy entities in `energia`, and map/security/maintenance content while moving it into `sistema`.
- Use `python_transform` for existing dashboard edits and a complete `config` only when creating `inicio` or `sistema`.
- Treat the four old dashboards as rollback sources: set `show_in_sidebar=false`, do not delete them in this implementation.
- Verify every write by reading the dashboard back, checking entity/card references, and rendering the result in mobile/tablet and desktop browser sizes.
- Keep the repository changes limited to this plan and the already committed design document; the effective dashboard changes are remote Home Assistant state.

---

### Task 1: Fresh live inventory and Frosted Glass preflight

**Files:**
- Read: live Home Assistant dashboards, resources, themes, entities, and states through the Home Assistant tools.
- Modify: none.

**Interfaces:**
- Consumes: the approved design at `docs/superpowers/specs/2026-09-06-homeassistant-dashboards-frosted-glass-design.md`.
- Produces: exact dashboard hashes, card bodies, installed resource URLs, the installed theme key if present, and verified entity states for all following tasks.

- [ ] **Step 1: Enumerate the current dashboard metadata.**

  Call `ha_config_get_dashboard(list_only=true)` and record the metadata for `map`, `casa`, `seguridad`, `energia`, `coche`, `mantenimiento`, and `panel-comedor`. Confirm that all seven are Storage dashboards before editing.

- [ ] **Step 2: Read every source dashboard fresh.**

  Call `ha_config_get_dashboard(url_path=<path>, force_reload=true)` for each source dashboard. For `casa`, also read the main view and each room view by `view_path` so the existing route paths, actions, and card resources are known without truncating the payload.

- [ ] **Step 3: Inventory resources and the actual Frosted Glass theme.**

  Call `ha_config_list_dashboard_resources(limit=100)` and `ha_manage_theme(action="list")`. Record the exact registered resource type and URL for `atomic-calendar-revive`, `ha-today-card`, `vehicle-status-card`, Helios, card-mod, Mushroom, and navbar-card. If an installed theme key matches Frosted Glass, use that exact key; otherwise plan the equivalent card-mod surface styling without adding a theme.

- [ ] **Step 4: Read the states used by the redesign.**

  Call `ha_get_state` with this exact initial set, adding only entities found in the fresh dashboard configs when needed:

  ```text
  weather.everest
  weather.forecast_everest
  calendar.casa
  calendar.trabajo
  camera.entrada_joan_fuster_5_high_resolution_channel
  camera.g5_turret_ultra_high_resolution_channel
  lock.aqara_smart_lock_u200
  alarm_control_panel.ucg_fiber_alarm_manager
  person.casa
  sensor.kitt_battery
  sensor.kitt_usable_battery
  sensor.kitt_charging_state
  sensor.kitt_charger_power
  sensor.kitt_state
  sensor.kitt_temperature_inside
  sensor.kitt_temperature_outside
  sensor.kitt_range_estimated
  binary_sensor.kitt_lock
  binary_sensor.kitt_charging
  device_tracker.kitt
  binary_sensor.tesla_wall_connector_vehicle_connected
  sensor.tesla_wall_connector_total_power
  sensor.potencia_circuito_shelly
  sensor.energia_red_ide_diaria
  sensor.energia_red_ide_mensual
  sensor.energia_coche_tesla_diaria
  ```

- [ ] **Step 5: Validate the preflight evidence.**

  Confirm that every entity used by the proposed cards exists, that the existing calendar card supplies its working options, and that no current source dashboard is YAML-mode or strategy-based. Stop before writing if any new dashboard would require an unavailable custom card or an entity that is absent from the live inventory.

### Task 2: Create the compact `Inicio` dashboard

**Files:**
- Modify: live Storage dashboard `inicio` through `ha_config_set_dashboard`.
- Read: live `casa` calendar card, live resource list, and live entity states from Task 1.

**Interfaces:**
- Consumes: Task 1 inventory and exact resource/theme keys.
- Produces: a new `inicio` dashboard with a vertical order of header, compact today weather, cameras immediately below, calendar, attention summary, and navigation.

- [ ] **Step 1: Assemble the configuration from verified entities.**

  Create `inicio` with `url_path="inicio"`, title `Inicio`, icon `mdi:home-variant-outline`, and `show_in_sidebar=true`. Use a `sections` view with these sections in order:

  1. A compact header using existing Mushroom/status cards and the verified presence entity.
  2. One weather block for `weather.everest`, using the installed `ha-today-card` only if its registered schema or an existing live config proves its fields; otherwise use the native weather card with only current/today information.
  3. A two-column responsive camera grid containing the exact entry and garage cameras. The unavailable garage entity must remain visibly unavailable rather than being replaced by a fake image.
  4. The existing working `custom:atomic-calendar-revive` configuration for `calendar.casa` and `calendar.trabajo`, retaining the verified colours, Spanish language, all-day events, seven-day limit, and compact glass styling. Include the monthly portion only if the installed card exposes that option in its current schema.
  5. Attention tiles for the verified lock, alarm, garage camera availability, and only other entities that Task 1 shows as actionable.
  6. Navigation cards linking to `casa`, `coche`, `energia`, and `sistema`.

  Apply a shared Frosted Glass style to the new section surfaces: translucent background, blur with an opaque fallback, consistent radius, restrained border/shadow, and readable text. Do not use a hard-coded sensor value.

- [ ] **Step 2: Create the dashboard through the API.**

  Call `ha_config_set_dashboard(url_path="inicio", title="Inicio", icon="mdi:home-variant-outline", show_in_sidebar=true, config=<the six-section sections config>)`. Do not write a `.storage` file or add a resource.

- [ ] **Step 3: Read the new dashboard back.**

  Call `ha_config_get_dashboard(url_path="inicio", force_reload=true)` and assert that the view order is weather → camera grid → calendar, that both camera entities and both calendar entities are present, and that all navigation targets are exactly `casa`, `coche`, `energia`, and `sistema`.

- [ ] **Step 4: Render `Inicio` in both target sizes.**

  Open `/lovelace/inicio` in the browser at tablet/mobile width and desktop width. Verify that the weather block is visibly smaller than the camera area, cameras are below it, the calendar is visible without a broken custom card, and no entity card reports an invalid configuration.

### Task 3: Create the consolidated `Sistema` dashboard

**Files:**
- Modify: live Storage dashboard `sistema` through `ha_config_set_dashboard`.
- Read: live configs of `map`, `seguridad`, and `mantenimiento` from Task 1.

**Interfaces:**
- Consumes: the exact working cards, views, map configuration, security controls, maintenance entities, and routes from the three source dashboards.
- Produces: one `sistema` dashboard with security, infrastructure, maintenance, and map/cameras views; no energy or room-control duplication.

- [ ] **Step 1: Select source cards without inventing replacements.**

  From the live source configs, retain the working alarm, lock, camera, map, update, backup, health, UCG Fiber, Home Assistant, and connectivity cards. Remove only duplicate navigation and cards whose entity is absent or permanently invalid according to Task 1.

- [ ] **Step 2: Build the four `sistema` views.**

  Create a `sections` dashboard titled `Sistema` with paths `seguridad`, `infraestructura`, `mantenimiento`, and `mapa`. Keep the security actions and camera access from `seguridad`, infrastructure health cards from `mantenimiento`, and the existing map/camera composition from `map`. Add the shared Frosted Glass navigation to every view without duplicating the energy or room dashboards.

- [ ] **Step 3: Create and structurally verify the dashboard.**

  Call `ha_config_set_dashboard(url_path="sistema", title="Sistema", icon="mdi:server-security", show_in_sidebar=true, config=<the four-view sections config>)`, then call `ha_config_get_dashboard(url_path="sistema", force_reload=true)`. Verify all critical source entities and each view path are present.

- [ ] **Step 4: Render the consolidated system views.**

  Open `/lovelace/sistema/seguridad`, `/lovelace/sistema/infraestructura`, `/lovelace/sistema/mantenimiento`, and `/lovelace/sistema/mapa` at tablet and desktop widths. Verify that map and camera cards load, unavailable devices are labelled clearly, and no card is silently empty.

### Task 4: Redesign `Casa`, `Coche`, and `Energía` in place

**Files:**
- Modify: live Storage dashboards `casa`, `coche`, and `energia` through `ha_config_set_dashboard`.
- Read: fresh dashboard hashes immediately before each dashboard write.

**Interfaces:**
- Consumes: the source configs and entity/resource inventory from Tasks 1–3.
- Produces: three existing dashboards with common Frosted Glass surfaces, compact first views, and preserved routes/actions.

- [ ] **Step 1: Transform `casa` without losing room routes.**

  Re-read `casa` and its full-config hash. Use one `python_transform` to set its visible title/icon/sidebar metadata as agreed, add the shared navigation to the main view, move the useful status/action sections above secondary details, and apply the common surface style. Preserve the existing paths for kitchen, dining room, stairs, bathrooms, bedrooms, and any room-specific card actions. Read back and compare the set of view paths and critical entity references with the pre-transform inventory.

- [ ] **Step 2: Transform `coche` from verified Kitt and Wall Connector cards.**

  Re-read `coche` and its hash. Keep the working `vehicle-status-card` and its entity mappings, then arrange the first sections as Kitt summary, battery/temperatures/lock/location, and Wall Connector connection/power. Use the current `sensor.kitt_*`, `binary_sensor.kitt_*`, `device_tracker.kitt`, and `sensor.tesla_wall_connector_*` IDs only. Read back and verify all vehicle controls, routes, and card types.

- [ ] **Step 3: Transform `energia` while preserving Helios.**

  Re-read `energia` and its hash. Retain `custom:helios-card` and its actual entity configuration. Reorder sections into current power, today/month totals, energy flows, historical power, appliances, and laundry. Replace only redundant headings or duplicate navigation; retain real appliance states and do not insert the example `1.8 kW` value from the mockup. Read back and verify the Helios card, all energy entities, and every existing energy route.

- [ ] **Step 4: Render all three dashboards.**

  Open the compact first view of `casa`, `coche`, and `energia` at tablet and desktop widths. Verify that primary controls remain reachable, the vehicle card is not clipped, Helios renders, and the Frosted Glass styling does not reduce text or control contrast.

### Task 5: Reduce visible navigation reversibly

**Files:**
- Modify: metadata of live dashboards `casa`, `coche`, `energia`, `inicio`, `sistema`, `map`, `seguridad`, `mantenimiento`, and `panel-comedor` through `ha_config_set_dashboard`.

**Interfaces:**
- Consumes: successful structural and visual checks from Tasks 2–4.
- Produces: exactly five dashboards shown in the sidebar, with old dashboards hidden but recoverable.

- [ ] **Step 1: Re-read all nine dashboard metadata records.**

  Call `ha_config_get_dashboard(list_only=true)` and confirm the new dashboards exist and the source dashboards are still present. Do not hide anything if `inicio` or `sistema` failed a previous check.

- [ ] **Step 2: Hide only the superseded dashboards.**

  For `map`, `seguridad`, `mantenimiento`, and `panel-comedor`, re-read the full config hash and call `ha_config_set_dashboard(url_path=<path>, config_hash=<fresh hash>, show_in_sidebar=false)`. Keep their configs and paths unchanged. Set `show_in_sidebar=true` for `inicio`, `casa`, `coche`, `energia`, and `sistema` using fresh metadata or hashes.

- [ ] **Step 3: Verify sidebar count and navigation links.**

  Call `ha_config_get_dashboard(list_only=true)` again. Assert that the five visible entries are exactly `inicio`, `casa`, `coche`, `energia`, and `sistema`, while the four old entries still exist with `show_in_sidebar=false`. Click each shared navigation target in the browser and confirm it resolves.

### Task 6: Cross-dashboard acceptance and rollback evidence

**Files:**
- Read: live dashboard configs, hashes, browser renders, and browser console/runtime state.
- Modify: live dashboards only if a verification finds a regression; no repository source changes beyond the committed plan/spec.

**Interfaces:**
- Consumes: readback and renders from Tasks 2–5.
- Produces: evidence that the five-dashboard end state is true and a safe rollback boundary for the hidden dashboards.

- [ ] **Step 1: Re-read the final live state.**

  Read all five visible dashboards with `force_reload=true` and capture their current hashes. Confirm the explicit requirements: compact today weather, cameras directly beneath it, visible calendar, Frosted Glass surfaces, dedicated car dashboard, dedicated energy dashboard, and consolidated system dashboard.

- [ ] **Step 2: Check entity and route preservation.**

  Search the final dashboards for the critical lock, alarm, calendars, cameras, Kitt sensors, Wall Connector, Helios, energy sensors, room controls, map, maintenance, and navigation routes. Confirm no search result points to an entity absent from the current state inventory.

- [ ] **Step 3: Perform visual acceptance.**

  Visit the five visible dashboards at tablet/mobile and desktop widths. Record whether each loads, whether the top-of-page hierarchy is correct, and whether there are broken-card, clipping, contrast, or route errors. Treat config readback as insufficient if the browser render contradicts it.

- [ ] **Step 4: Retain rollback state.**

  Confirm that `map`, `seguridad`, `mantenimiento`, and `panel-comedor` still return valid configs and remain hidden rather than deleted. If a new dashboard fails after hiding, restore its prior visible dashboard by setting `show_in_sidebar=true` through a fresh hash-protected API call before investigating further.

- [ ] **Step 5: Finish the coordination boundary.**

  Release this task's coordination claim only after the final readback and browser checks pass. Report the remote dashboards changed, the four hidden rollback dashboards, structural proof, visual proof, and any remaining device-level unavailability separately.
