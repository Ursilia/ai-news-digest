from sqlalchemy.orm import Session
from app import models

class SourceRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, name: str, url: str) -> models.Source:
        new_source = models.Source(name=name, url=url)
        self.db.add(new_source)
        self.db.commit()
        self.db.refresh(new_source)
        return new_source

    def get_by_url(self, url: str) -> models.Source | None:
        return self.db.query(models.Source).filter(models.Source.url == url).first()

    def get_by_id(self, source_id: int) -> models.Source | None:
        return self.db.query(models.Source).filter(models.Source.id == source_id).first()

    def get_all(self, limit: int = 10, search: str | None = None) -> list[models.Source]:
        query = self.db.query(models.Source)
        if search:
            query = query.filter(models.Source.name.ilike(f"%{search}%"))
        return query.limit(limit).all()

    def update(self, source: models.Source, name: str, url: str) -> models.Source:
        source.name = name
        source.url = url
        self.db.commit()
        self.db.refresh(source)
        return source

    def delete(self, source: models.Source) -> None:
        self.db.delete(source)
        self.db.commit()

class TagRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, name: str, description: str | None) -> models.Tag:
        creating = models.Tag(name=name, description=description)
        self.db.add(creating)
        self.db.commit()
        self.db.refresh(creating)
        return creating

    def get_by_name_or_create(self, name: str, description: str | None) -> models.Tag:
        checking = self.db.query(models.Tag).filter(models.Tag.name == name).first()
        if checking is not None:
            return checking
        creating = models.Tag(name=name, description=description)
        self.db.add(creating)
        self.db.commit()
        self.db.refresh(creating)
        return creating

    def get_by_id(self, tag_id: int) -> models.Tag | None:
        return self.db.query(models.Tag).filter(models.Tag.id == tag_id).first()

    def get_by_name(self, name: str) -> models.Tag | None:
        return self.db.query(models.Tag).filter(models.Tag.name == name).first()

    def get_all(self, limit: int = 10, search: str | None = None) -> list[models.Tag]:
        query = self.db.query(models.Tag)
        if search:
            query = query.filter(models.Tag.name.ilike(f"%{search}%"))
        return query.limit(limit).all()

    def update(self, tag: models.Tag, name: str, description: str) -> models.Tag:
        tag.name = name
        tag.description = description
        self.db.commit()
        self.db.refresh(tag)
        return tag

    def delete(self, tag: models.Tag) -> None:
        self.db.delete(tag)
        self.db.commit()

    