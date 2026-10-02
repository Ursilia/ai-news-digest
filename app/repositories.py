from sqlalchemy.orm import Session
from app import models
from sqlalchemy import select

class SourceRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, name: str, url: str, owner_id: int) -> models.Source:
        new_source = models.Source(name=name, url=url, owner_id=owner_id)
        self.db.add(new_source)
        self.db.commit()
        self.db.refresh(new_source)
        return new_source

    def get_by_url(self, url: str, owner_id: int) -> models.Source | None:
        return self.db.query(models.Source).filter(models.Source.url == url,
                                                   models.Source.owner_id == owner_id).first()

    def get_by_id(self, source_id: int, owner_id: int) -> models.Source | None:
        return self.db.query(models.Source).filter(models.Source.id == source_id,
                                                   models.Source.owner_id == owner_id).first()

    def get_all(self,owner_id: int, limit: int = 10, search: str | None = None) -> list[models.Source]:
        query = self.db.query(models.Source).filter(models.Source.owner_id == owner_id)
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


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> models.User | None:
        return self.db.query(models.User).filter(models.User.email == email).first()

    def get_by_id(self, user_id: int) -> models.User | None:
        return self.db.query(models.User).filter(models.User.id == user_id).first()

    def create(self, email: str, hashed_password: str) -> models.User:
        new_user = models.User(email=email, hashed_password=hashed_password)
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return new_user


class DocumentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, title: str, content: str, owner_id: int) -> models.Document:
        new_doc = models.Document(title=title, content=content, owner_id=owner_id)
        self.db.add(new_doc)
        self.db.commit()
        self.db.refresh(new_doc)
        return new_doc

    def get_by_id(self, document_id: int, owner_id: int) -> models.Document | None:
        return (self.db.query(models.Document)
                .filter(models.Document.id==document_id, 
                models.Document.owner_id==owner_id,
                ).first())

    def get_all(self, owner_id: int, limit: int = 20) -> list[models.Document]:
        return (self.db.query(models.Document)
                .filter(models.Document.owner_id==owner_id)
                .order_by(models.Document.created_at.desc()).limit(limit).all()
                )

    def delete(self, document: models.Document) -> None:
        self.db.delete(document)
        self.db.commit()

    def add_chunks(self, document_id: int, chunks: list[tuple[str, list[float]]],
                   ) -> list[models.Chunk]:
        chunks_objects = [
            models.Chunk(
                document_id=document_id,
                content=text,
                chunk_index=i,
                embedding=embedding,
            )
            for i, (text, embedding) in enumerate(chunks)
        ]
        self.db.add_all(chunks_objects)
        self.db.commit()
        return chunks_objects

    def search_chunks(self, query_embedding: list[float], 
                      owner_id: int, 
                      limit: int = 5,) -> list[tuple[models.Chunk, float]]:
        
        distance = models.Chunk.embedding.cosine_distance(query_embedding).label("distance")

        stmt = (
            select(models.Chunk, distance)
            .join(models.Document, models.Chunk.document_id == models.Document.id)
            .where(models.Document.owner_id == owner_id)
            .order_by(distance)
            .limit(limit)
        )
        return self.db.execute(stmt).all()