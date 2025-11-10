# 08 (anexo) - Servicios para Categorías e integración con Items

Este anexo documenta la nueva funcionalidad de categorías (relación N:N con Items), los servicios creados y las extensiones aplicadas al servicio de ítems.

## Servicio de Categorías: `app/services/category_service.py`

Funciones disponibles:
- `list_categories(db, skip=0, limit=100, q=None)`: Lista categorías con búsqueda opcional y carga de `items` mediante `selectinload`.
- `get_category(db, category_id)`: Devuelve una categoría por id con sus ítems.
- `get_category_by_name(db, name)`: Recupera por nombre (útil para validaciones únicas).
- `create_category(db, payload: CategoryCreate)`: Crea una categoría.
- `update_category(db, category_id, payload: CategoryUpdate)`: Actualiza `name` y/o `description`.
- `delete_category(db, category_id)`: Elimina la categoría por id.

## Extensiones en Servicio de Ítems: `app/services/item_service.py`

- `list_items(..., category_id=None)`: Filtra ítems por categoría, y hace eager-load de `owner` y `categories`.
- `get_item(db, item_id)`: Carga `owner` y `categories` para respuestas consistentes (`ItemReadWithOwner`).
- `create_item(db, payload: ItemCreate)`: Asigna categorías iniciales si se envía `category_ids`.
- `update_item(db, item_id, payload: ItemUpdate)`: Reemplaza categorías si se envía `category_ids` (lista vacía borra todas).

## Esquemas Pydantic relacionados

- `app/schemas/category.py`: `CategoryRead`, `CategoryReadWithItems` (incluye `items` resumidos).
- `app/schemas/item.py`: `ItemCreate`/`ItemUpdate` aceptan `category_ids`; `ItemReadWithOwner` incluye `categories` embebidas.

## Notas de implementación

- Las consultas usan `selectinload` para evitar N+1 y mantener respuestas rápidas.
- El filtro por `category_id` realiza `JOIN` sobre la relación `Item.categories`.
- Se validan existencias de `owner` y categorías al crear/actualizar.