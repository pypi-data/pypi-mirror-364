from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from ...models import get_db, User
from ...core.prompt_manager import PromptManager
from ..dependencies import get_current_active_user

router = APIRouter()


class PromptTemplateCreate(BaseModel):
    name: str
    content: str
    description: Optional[str] = None


class PromptTemplateUpdate(BaseModel):
    content: str
    name: Optional[str] = None
    description: Optional[str] = None


class PromptTemplateResponse(BaseModel):
    id: int
    name: str
    content: str
    description: Optional[str]
    version: int
    created_at: str
    updated_at: str


class PromptTemplateVersionResponse(BaseModel):
    id: int
    name: str
    content: str
    description: Optional[str]
    version: int
    created_at: str


@router.post("/", response_model=PromptTemplateResponse)
async def create_prompt_template(
        prompt_data: PromptTemplateCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
):
    manager = PromptManager(db)
    template = manager.create_prompt_template(
        name=prompt_data.name,
        content=prompt_data.content,
        description=prompt_data.description,
        user_id=current_user.id
    )

    return PromptTemplateResponse(
        id=template.id,
        name=template.name,
        content=template.content,
        description=template.description,
        version=template.version,
        created_at=template.created_at.isoformat(),
        updated_at=template.updated_at.isoformat()
    )


@router.get("/", response_model=List[PromptTemplateResponse])
async def list_prompt_templates(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
):
    manager = PromptManager(db)
    templates = manager.list_prompt_templates()

    return [
        PromptTemplateResponse(
            id=template.id,
            name=template.name,
            content=template.content,
            description=template.description,
            version=template.version,
            created_at=template.created_at.isoformat(),
            updated_at=template.updated_at.isoformat()
        )
        for template in templates
    ]


@router.get("/{template_id}", response_model=PromptTemplateResponse)
async def get_prompt_template(
        template_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
):
    manager = PromptManager(db)
    template = manager.get_prompt_template(template_id)

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    return PromptTemplateResponse(
        id=template.id,
        name=template.name,
        content=template.content,
        description=template.description,
        version=template.version,
        created_at=template.created_at.isoformat(),
        updated_at=template.updated_at.isoformat()
    )


@router.put("/{template_id}", response_model=PromptTemplateResponse)
async def update_prompt_template(
        template_id: int,
        prompt_data: PromptTemplateUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
):
    manager = PromptManager(db)

    try:
        template = manager.update_prompt_template(
            template_id=template_id,
            content=prompt_data.content,
            name=prompt_data.name,
            description=prompt_data.description,
            user_id=current_user.id
        )

        return PromptTemplateResponse(
            id=template.id,
            name=template.name,
            content=template.content,
            description=template.description,
            version=template.version,
            created_at=template.created_at.isoformat(),
            updated_at=template.updated_at.isoformat()
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{template_id}/versions", response_model=List[PromptTemplateVersionResponse])
async def list_template_versions(
        template_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
):
    manager = PromptManager(db)
    versions = manager.list_template_versions(template_id)

    return [
        PromptTemplateVersionResponse(
            id=version.id,
            name=version.name,
            content=version.content,
            description=version.description,
            version=version.version,
            created_at=version.created_at.isoformat()
        )
        for version in versions
    ]


@router.delete("/{template_id}")
async def delete_prompt_template(
        template_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
):
    manager = PromptManager(db)
    success = manager.delete_prompt_template(template_id)

    if not success:
        raise HTTPException(status_code=404, detail="Template not found")

    return {"message": "Template deleted successfully"}