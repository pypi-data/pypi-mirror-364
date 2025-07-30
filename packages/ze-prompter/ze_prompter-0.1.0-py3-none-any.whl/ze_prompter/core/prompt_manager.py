from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from ..models import PromptTemplate, PromptTemplateVersion


class PromptManager:
    def __init__(self, db: Session):
        self.db = db

    def create_prompt_template(
            self,
            name: str,
            content: str,
            description: Optional[str] = None,
            user_id: Optional[int] = None
    ) -> PromptTemplate:
        """Create a new prompt template"""
        template = PromptTemplate(
            name=name,
            content=content,
            description=description,
            version=1,
            created_by=user_id
        )
        self.db.add(template)
        self.db.commit()
        self.db.refresh(template)

        # Create first version entry
        version = PromptTemplateVersion(
            template_id=template.id,
            name=name,
            content=content,
            description=description,
            version=1,
            created_by=user_id
        )
        self.db.add(version)
        self.db.commit()

        return template

    def update_prompt_template(
            self,
            template_id: int,
            content: str,
            name: Optional[str] = None,
            description: Optional[str] = None,
            user_id: Optional[int] = None
    ) -> PromptTemplate:
        """Update a prompt template and increment version"""
        template = self.db.query(PromptTemplate).filter(
            PromptTemplate.id == template_id
        ).first()

        if not template:
            raise ValueError("Template not found")

        # Increment version
        new_version = template.version + 1

        # Update template
        if name:
            template.name = name
        if description is not None:
            template.description = description
        template.content = content
        template.version = new_version

        # Create new version entry
        version = PromptTemplateVersion(
            template_id=template.id,
            name=template.name,
            content=content,
            description=template.description,
            version=new_version,
            created_by=user_id
        )
        self.db.add(version)
        self.db.commit()
        self.db.refresh(template)

        return template

    def get_prompt_template_by_id(self, template_id: int) -> Optional[PromptTemplate]:
        """Get a prompt template by ID"""
        return self.db.query(PromptTemplate).filter(
            PromptTemplate.id == template_id
        ).first()

    def get_prompt_template(self, template_id: int) -> Optional[PromptTemplate]:
        """Get a prompt template by ID (alias for get_prompt_template_by_id)"""
        return self.get_prompt_template_by_id(template_id)

    def get_prompt_template_by_name(self, name: str) -> Optional[PromptTemplate]:
        """Get the latest version of a prompt template by name"""
        return self.db.query(PromptTemplate).filter(
            PromptTemplate.name == name
        ).order_by(desc(PromptTemplate.version)).first()

    def get_prompt_template_version_by_id(
            self,
            template_id: int,
            version: int
    ) -> Optional[PromptTemplateVersion]:
        """Get a specific version of a prompt template by ID"""
        return self.db.query(PromptTemplateVersion).filter(
            PromptTemplateVersion.template_id == template_id,
            PromptTemplateVersion.version == version
        ).first()

    def get_prompt_template_version(
            self,
            template_id: int,
            version: int
    ) -> Optional[PromptTemplateVersion]:
        """Get a specific version of a prompt template (alias for get_prompt_template_version_by_id)"""
        return self.get_prompt_template_version_by_id(template_id, version)

    def list_prompt_templates(self) -> List[PromptTemplate]:
        """List all prompt templates"""
        return self.db.query(PromptTemplate).all()

    def list_template_versions_by_id(self, template_id: int) -> List[PromptTemplateVersion]:
        """List all versions of a template by ID"""
        return self.db.query(PromptTemplateVersion).filter(
            PromptTemplateVersion.template_id == template_id
        ).order_by(desc(PromptTemplateVersion.version)).all()

    def list_template_versions(self, template_id: int) -> List[PromptTemplateVersion]:
        """List all versions of a template (alias for list_template_versions_by_id)"""
        return self.list_template_versions_by_id(template_id)

    def delete_prompt_template_by_id(self, template_id: int) -> bool:
        """Delete a prompt template and all its versions by ID"""
        template = self.db.query(PromptTemplate).filter(
            PromptTemplate.id == template_id
        ).first()

        if not template:
            return False

        # Delete all versions
        self.db.query(PromptTemplateVersion).filter(
            PromptTemplateVersion.template_id == template_id
        ).delete()

        # Delete template
        self.db.delete(template)
        self.db.commit()

        return True

    def delete_prompt_template(self, template_id: int) -> bool:
        """Delete a prompt template and all its versions (alias for delete_prompt_template_by_id)"""
        return self.delete_prompt_template_by_id(template_id)

    def delete_template_by_name(self, name: str) -> bool:
        """Delete a prompt template and all its versions by name"""
        template = self.get_prompt_template_by_name(name)
        if not template:
            return False
        return self.delete_prompt_template_by_id(template.id)

    def get_latest_template(self, name: str) -> Optional[PromptTemplate]:
        """Get the latest version of a prompt template by name (alias for get_prompt_template_by_name)"""
        return self.get_prompt_template_by_name(name)

    def list_templates(self) -> List[PromptTemplate]:
        """List all prompt templates (alias for list_prompt_templates)"""
        return self.list_prompt_templates()

    def get_template_versions(self, name: str) -> List[PromptTemplateVersion]:
        """Get all versions of a template by name"""
        # First get the template by name to get its ID
        template = self.get_prompt_template_by_name(name)
        if not template:
            return []
        
        # Then get all versions
        return self.list_template_versions_by_id(template.id)

    def get_template_versions_by_id(self, template_id: int) -> List[PromptTemplateVersion]:
        """Get all versions of a template by ID (alias for list_template_versions_by_id)"""
        return self.list_template_versions_by_id(template_id)

    def get_template_by_name_and_version(self, name: str, version: int) -> Optional[PromptTemplateVersion]:
        """Get a specific version of a template by name and version number"""
        # First get the template by name to get its ID
        template = self.get_prompt_template_by_name(name)
        if not template:
            return None
        
        # Then get the specific version
        return self.get_prompt_template_version_by_id(template.id, version)