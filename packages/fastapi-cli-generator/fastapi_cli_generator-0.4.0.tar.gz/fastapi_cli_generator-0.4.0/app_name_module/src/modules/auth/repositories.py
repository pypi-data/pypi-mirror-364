from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from src.modules.auth.models import ApiKey
from src.shared.exceptions import DatabaseException
from src.shared.logger import APILogger

logger = APILogger("auth_repository")


class ApiKeyRepository:
    """API密钥数据访问层"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_api_key(self, api_key: str) -> Optional[ApiKey]:
        """根据API密钥获取记录"""
        try:
            stmt = select(ApiKey).where(ApiKey.api_key == api_key)
            result = await self.db.execute(stmt)
            api_key_obj = result.scalar_one_or_none()

            logger.log_database_operation(
                operation="select",
                table="api_keys",
                success=True,
                api_key=api_key[:8] + "****" if api_key else None
            )

            return api_key_obj

        except Exception as e:
            logger.log_database_operation(
                operation="select",
                table="api_keys",
                success=False,
                error=str(e)
            )
            raise DatabaseException("查询API密钥失败", str(e))

    async def get_by_id(self, api_key_id: int) -> Optional[ApiKey]:
        """根据ID获取API密钥"""
        try:
            stmt = select(ApiKey).where(ApiKey.id == api_key_id)
            result = await self.db.execute(stmt)
            api_key_obj = result.scalar_one_or_none()

            logger.log_database_operation(
                operation="select",
                table="api_keys",
                success=True,
                api_key_id=api_key_id
            )

            return api_key_obj

        except Exception as e:
            logger.log_database_operation(
                operation="select",
                table="api_keys",
                success=False,
                error=str(e)
            )
            raise DatabaseException("查询API密钥失败", str(e))

    async def update_last_used(self, api_key_id: int) -> bool:
        """更新最后使用时间"""
        try:
            stmt = update(ApiKey).where(ApiKey.id == api_key_id).values(
                last_used_at=datetime.now()
            )
            result = await self.db.execute(stmt)
            await self.db.commit()

            success = result.rowcount > 0
            logger.log_database_operation(
                operation="update",
                table="api_keys",
                success=success,
                api_key_id=api_key_id
            )

            return success

        except Exception as e:
            await self.db.rollback()
            logger.log_database_operation(
                operation="update",
                table="api_keys",
                success=False,
                error=str(e)
            )
            raise DatabaseException("更新API密钥使用时间失败", str(e))

    async def create(self, api_key_data: dict) -> ApiKey:
        """创建新的API密钥"""
        try:
            api_key_obj = ApiKey(**api_key_data)
            self.db.add(api_key_obj)
            await self.db.commit()
            await self.db.refresh(api_key_obj)

            logger.log_database_operation(
                operation="insert",
                table="api_keys",
                success=True,
                key_name=api_key_data.get("key_name")
            )

            return api_key_obj

        except Exception as e:
            await self.db.rollback()
            logger.log_database_operation(
                operation="insert",
                table="api_keys",
                success=False,
                error=str(e)
            )
            raise DatabaseException("创建API密钥失败", str(e))