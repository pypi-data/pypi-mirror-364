import secrets
import string
from sqlalchemy.ext.asyncio import AsyncSession
from src.modules.auth.repositories import ApiKeyRepository
from src.modules.auth.schemas import AuthenticatedUser, ApiKeyCreate, ApiKeyResponse
from src.shared.exceptions import AuthenticationException, ValidationException
from src.shared.logger import APILogger

logger = APILogger("auth_service")


class AuthService:
    """认证服务"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = ApiKeyRepository(db)

    def generate_api_key(self, length: int = 32) -> str:
        """生成API密钥"""
        # 使用安全的随机字符串生成器
        alphabet = string.ascii_letters + string.digits
        api_key = ''.join(secrets.choice(alphabet) for _ in range(length))
        return f"ak_{api_key}"  # 添加前缀便于识别

    async def validate_api_key(self, api_key: str) -> AuthenticatedUser:
        """验证API密钥"""
        if not api_key:
            logger.log_business_event("API密钥验证失败", reason="密钥为空")
            raise AuthenticationException("API密钥不能为空")

        # 查询API密钥
        api_key_obj = await self.repository.get_by_api_key(api_key)

        if not api_key_obj:
            logger.log_business_event("API密钥验证失败", reason="密钥不存在", api_key=api_key[:8] + "****")
            raise AuthenticationException("无效的API密钥")

        if not api_key_obj.is_active:
            logger.log_business_event("API密钥验证失败", reason="密钥已禁用", key_name=api_key_obj.key_name)
            raise AuthenticationException("API密钥已被禁用")

        # 更新最后使用时间
        await self.repository.update_last_used(api_key_obj.id)

        # 记录成功验证
        logger.log_business_event(
            "API密钥验证成功",
            key_name=api_key_obj.key_name,
            api_key_id=api_key_obj.id
        )

        return AuthenticatedUser(
            api_key_id=api_key_obj.id,
            key_name=api_key_obj.key_name,
            api_key=api_key[:8] + "****"  # 脱敏处理
        )

    async def create_api_key(self, api_key_create: ApiKeyCreate) -> ApiKeyResponse:
        """创建新的API密钥"""
        try:
            # 生成新的API密钥
            new_api_key = self.generate_api_key()

            # 准备数据
            api_key_data = {
                "key_name": api_key_create.key_name,
                "description": api_key_create.description,
                "api_key": new_api_key,
                "is_active": True
            }

            # 创建记录
            api_key_obj = await self.repository.create(api_key_data)

            logger.log_business_event(
                "API密钥创建成功",
                key_name=api_key_obj.key_name,
                api_key_id=api_key_obj.id
            )

            return ApiKeyResponse.model_validate(api_key_obj)

        except Exception as e:
            logger.log_business_event(
                "API密钥创建失败",
                key_name=api_key_create.key_name,
                error=str(e)
            )
            raise ValidationException("创建API密钥失败", str(e))

    async def check_api_key_exists(self, api_key: str) -> bool:
        """检查API密钥是否存在"""
        api_key_obj = await self.repository.get_by_api_key(api_key)
        return api_key_obj is not None and api_key_obj.is_active