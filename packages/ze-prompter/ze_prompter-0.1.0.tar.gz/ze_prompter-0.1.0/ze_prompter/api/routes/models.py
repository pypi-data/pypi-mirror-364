from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from ...models import get_db, User
from ...core.model_manager import ModelManager
from ..dependencies import get_current_active_user

router = APIRouter()


class ModelCreate(BaseModel):
    name: str
    description: Optional[str] = None
    extra_fields: Optional[Dict[str, Any]] = None


class ModelUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    extra_fields: Optional[Dict[str, Any]] = None


class ModelResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    extra_fields: Optional[Dict[str, Any]]
    created_at: str
    updated_at: str


@router.post("/", response_model=ModelResponse)
async def create_model(
        model_data: ModelCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
):
    manager = ModelManager(db)
    model = manager.create_model(
        name=model_data.name,
        description=model_data.description,
        extra_fields=model_data.extra_fields
    )

    return ModelResponse(
        id=model.id,
        name=model.name,
        description=model.description,
        extra_fields=model.extra_fields,
        created_at=model.created_at.isoformat(),
        updated_at=model.updated_at.isoformat()
    )


@router.get("/", response_model=List[ModelResponse])
async def list_models(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
):
    manager = ModelManager(db)
    models = manager.list_models()

    return [
        ModelResponse(
            id=model.id,
            name=model.name,
            description=model.description,
            extra_fields=model.extra_fields,
            created_at=model.created_at.isoformat(),
            updated_at=model.updated_at.isoformat()
        )
        for model in models
    ]


@router.get("/{model_id}", response_model=ModelResponse)
async def get_model(
        model_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
):
    manager = ModelManager(db)
    model = manager.get_model(model_id)

    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    return ModelResponse(
        id=model.id,
        name=model.name,
        description=model.description,
        extra_fields=model.extra_fields,
        created_at=model.created_at.isoformat(),
        updated_at=model.updated_at.isoformat()
    )


@router.put("/{model_id}", response_model=ModelResponse)
async def update_model(
        model_id: int,
        model_data: ModelUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
):
    manager = ModelManager(db)
    model = manager.update_model(
        model_id=model_id,
        name=model_data.name,
        description=model_data.description,
        extra_fields=model_data.extra_fields
    )

    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    return ModelResponse(
        id=model.id,
        name=model.name,
        description=model.description,
        extra_fields=model.extra_fields,
        created_at=model.created_at.isoformat(),
        updated_at=model.updated_at.isoformat()
    )


@router.delete("/{model_id}")
async def delete_model(
        model_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
):
    manager = ModelManager(db)
    success = manager.delete_model(model_id)

    if not success:
        raise HTTPException(status_code=404, detail="Model not found")

    return {"message": "Model deleted successfully"}