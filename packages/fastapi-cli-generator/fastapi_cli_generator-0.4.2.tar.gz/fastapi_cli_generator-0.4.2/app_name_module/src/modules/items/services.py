from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from src.modules.items.repositories import EnterpriseRepository
from src.modules.items.schemas import (
    EnterpriseQueryRequest,
    EnterpriseQueryResponse,
    BasicInfo,
    BusinessStatus,
    RiskInfo
)
from src.shared.exceptions import NotFoundException, ValidationException
from src.shared.logger import APILogger

logger = APILogger("enterprise_service")


class EnterpriseService:
    """企业信息查询服务"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = EnterpriseRepository(db)

    async def query_enterprise_info(self, request: EnterpriseQueryRequest) -> List[EnterpriseQueryResponse]:
        """查询企业信息"""
        try:
            # 验证查询参数
            if not request.enterprise_name and not request.credit_code:
                raise ValidationException("企业名称和统一社会信用代码至少提供一个")

            # 查询企业数据
            enterprises = await self.repository.query_enterprises(
                enterprise_name=request.enterprise_name,
                credit_code=request.credit_code,
                region=request.region,
                industry=request.industry
            )

            if not enterprises:
                logger.log_business_event(
                    "企业信息查询",
                    success=False,
                    reason="未找到匹配的企业",
                    enterprise_name=request.enterprise_name,
                    credit_code=request.credit_code[:8] + "****" if request.credit_code else None
                )
                raise NotFoundException("未找到匹配的企业信息")

            # 构建响应数据
            responses = []
            for enterprise in enterprises:
                response_data = {
                    "enterprise_name": enterprise.enterprise_name,
                    "credit_code": enterprise.credit_code
                }

                # 根据请求的字段构建响应
                if "basic_info" in request.query_fields:
                    response_data["basic_info"] = BasicInfo(
                        legal_person=enterprise.legal_person,
                        register_capital=enterprise.register_capital,
                        establish_date=enterprise.establish_date,
                        business_scope=enterprise.business_scope
                    )

                if "business_status" in request.query_fields:
                    response_data["business_status"] = BusinessStatus(
                        status=enterprise.status,
                        annual_revenue=enterprise.annual_revenue,
                        employee_count=enterprise.employee_count
                    )

                if "risk_info" in request.query_fields:
                    response_data["risk_info"] = RiskInfo(
                        risk_level=enterprise.risk_level,
                        lawsuit_count=enterprise.lawsuit_count,
                        penalty_count=enterprise.penalty_count
                    )

                responses.append(EnterpriseQueryResponse(**response_data))

            # 记录成功查询
            logger.log_business_event(
                "企业信息查询",
                success=True,
                count=len(responses),
                enterprise_name=request.enterprise_name,
                credit_code=request.credit_code[:8] + "****" if request.credit_code else None,
                query_fields=request.query_fields
            )

            return responses

        except (NotFoundException, ValidationException):
            # 重新抛出业务异常
            raise
        except Exception as e:
            logger.log_business_event(
                "企业信息查询",
                success=False,
                error=str(e),
                enterprise_name=request.enterprise_name,
                credit_code=request.credit_code[:8] + "****" if request.credit_code else None
            )
            raise ValidationException("查询企业信息失败", str(e))