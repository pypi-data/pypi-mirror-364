from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from ..models import Model


class ModelManager:
    def __init__(self, db: Session):
        self.db = db

    def create_model(
            self,
            name: str,
            description: Optional[str] = None,
            extra_fields: Optional[Dict[str, Any]] = None
    ) -> Model:
        """Create a new model"""
        model = Model(
            name=name,
            description=description,
            extra_fields=extra_fields or {}
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return model

    def update_model(
            self,
            model_id: int,
            name: Optional[str] = None,
            description: Optional[str] = None,
            extra_fields: Optional[Dict[str, Any]] = None
    ) -> Optional[Model]:
        """Update a model"""
        model = self.db.query(Model).filter(Model.id == model_id).first()

        if not model:
            return None

        if name:
            model.name = name
        if description is not None:
            model.description = description
        if extra_fields is not None:
            model.extra_fields = extra_fields

        self.db.commit()
        self.db.refresh(model)
        return model

    def get_model(self, model_id: int) -> Optional[Model]:
        """Get a model by ID"""
        return self.db.query(Model).filter(Model.id == model_id).first()

    def get_model_by_name(self, name: str) -> Optional[Model]:
        """Get a model by name"""
        return self.db.query(Model).filter(Model.name == name).first()

    def list_models(self) -> List[Model]:
        """List all models"""
        return self.db.query(Model).all()

    def delete_model(self, model_id: int) -> bool:
        """Delete a model"""
        model = self.db.query(Model).filter(Model.id == model_id).first()

        if not model:
            return False

        self.db.delete(model)
        self.db.commit()
        return True