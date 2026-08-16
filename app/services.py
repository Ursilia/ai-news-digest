from app.schemas import Source

sources_db: list[dict] = []

def create_source(source: Source) -> dict:
    new_item = {"id": len(sources_db) + 1, **source.model_dump()}
    sources_db.append(new_item)
    return new_item

def get_all_sources(limit: int = 10, search: str | None = None) -> list[dict]:
    if search:
        result = [item for item in sources_db if search.lower() in item["name"].lower()]
        return result[:limit]
    return sources_db[:limit]

def get_source(source_id: int) -> dict | None:
    for item in sources_db:
        if item["id"] == source_id:
            return item
    return None

def update_source(source_id: int, source: Source) -> dict | None:
    updated = {"id": source_id, **source.model_dump()}
    for i, item in enumerate(sources_db):
        if item["id"] == source_id:
            sources_db[i] = updated
            return updated
    return None

def delete_source(source_id: int) -> bool:
    for item in sources_db:
        if item["id"] == source_id:
            sources_db.remove(item)
            return True
    return False
