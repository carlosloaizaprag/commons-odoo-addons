# 🧩 Módulos Comunes - Pragmatic Ingeniería

Este repositorio contiene los **módulos base y comunes** desarrollados por **Pragmatic Ingeniería** para su uso en múltiples proyectos y versiones de **Odoo**.  
Su propósito es **centralizar las funcionalidades compartidas**, garantizando **consistencia, mantenibilidad y escalabilidad** en las implementaciones empresariales.

---

## 🏗️ Propósito

Estos módulos están diseñados para:
- Reutilizar código y configuraciones entre proyectos.
- Estandarizar procesos y modelos comunes.
- Asegurar compatibilidad con distintas versiones de Odoo.
- Reducir el tiempo de desarrollo y mantenimiento.

---

## 📦 Estructura

Cada módulo dentro de este repositorio cumple una función específica dentro del ecosistema Odoo de Pragmatic Ingeniería.  
A continuación se listan los módulos incluidos y su descripción general:

| Módulo | Descripción |
|--------|--------------|
| `base_api` | CEl módulo amplía el modelo *base* con el fin de crear y consultar objetos. Funciones y métodos básicos de la API para openapi o XML-RPC. |
| `openapi` | API RESTful para integrar Odoo con cualquier sistema que necesites. |
| `restict_logins` | Garantiza sesiones simultáneas restringidas, obliga al usuario a cerrar sesión y automatiza la caducidad de la sesión para mejorar la seguridad. |
| `l10n_co_base` | Ciudades y estados de Colombia. |


---
