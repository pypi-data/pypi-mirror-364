from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ApiKeyBase(BaseModel):
    """API密钥基础模型"""
    key_name: str = Field(..., description="密钥名称", max_length=100)
    description: Optional[str] = Field(None, description="密钥描述")


class ApiKeyCreate(ApiKeyBase):
    """创建API密钥请求模型"""
    pass


class ApiKeyResponse(ApiKeyBase):
    """API密钥响应模型"""
    id: int
    api_key: str = Field(..., description="API密钥")
    is_active: bool = Field(..., description="是否激活")
    created_at: datetime = Field(..., description="创建时间")
    last_used_at: Optional[datetime] = Field(None, description="最后使用时间")

    class Config:
        from_attributes = True


class ApiKeyValidateRequest(BaseModel):
    """API密钥验证请求模型"""
    api_key: str = Field(..., description="要验证的API密钥")


class ApiKeyValidateResponse(BaseModel):
    """API密钥验证响应模型"""
    valid: bool = Field(..., description="密钥是否有效")
    key_name: Optional[str] = Field(None, description="密钥名称")
    message: str = Field(..., description="验证结果消息")


class AuthenticatedUser(BaseModel):
    """认证用户信息模型"""
    api_key_id: int = Field(..., description="API密钥ID")
    key_name: str = Field(..., description="密钥名称")
    api_key: str = Field(..., description="API密钥（脱敏）")