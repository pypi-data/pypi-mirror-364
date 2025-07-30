from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from src.shared.database import Base


class ApiKey(Base):
    """API密钥模型"""
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    key_name = Column(String(100), nullable=False, comment="密钥名称")
    api_key = Column(String(255), unique=True, index=True, nullable=False, comment="API密钥")
    description = Column(Text, nullable=True, comment="密钥描述")
    is_active = Column(Boolean, default=True, nullable=False, comment="是否激活")
    created_at = Column(DateTime, default=datetime.now, nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False, comment="更新时间")
    last_used_at = Column(DateTime, nullable=True, comment="最后使用时间")

    def __repr__(self):
        return f"<ApiKey(id={self.id}, key_name='{self.key_name}', is_active={self.is_active})>"