from pydantic import BaseModel, EmailStr, ConfigDict
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from enum import Enum
from datetime import datetime

class NewSnapshotRequest(BaseModel):
    snapshot_id: int | None = None
    files: list[UploadFile] = File(...),
    webhook_url: str | None = None

class KnowledgeSnapshot(BaseModel):
    is_active: bool = False
    document_paths: list[str]
    index_id: str | None = None
    status: str = "pending"  # pending, processing, ready, failed




class KnowledgeSnapshotRead(KnowledgeSnapshot):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class KnowledgeSnapshotUpdate(BaseModel):
    is_active: bool | None = None
    document_paths: list[str] | None = None
    index_id: str | None = None 
    status: str | None = None

class KnowledgeSnapshotCreate(KnowledgeSnapshot):
    pass


class KnowledgeSnapshotFilter(BaseModel):
    id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    is_active: bool | None = None
    document_paths: list[str] | None = None
    index_id: str | None = None 
    status: str | None = None