# -*- coding: utf-8 -*-
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field
import random
import logging
from typing import Literal, Optional

# 初始化日志和 MCP 服务
logger = logging.getLogger('mcp')
mcp = FastMCP('hypertension-diagnosis-service', log_level='INFO')

# 不同测量场景下的诊断阈值
DIAGNOSIS_THRESHOLDS = {
    "诊室测量": {"sbp": 140, "dbp": 90, "desc": "诊室血压"},
    "动态血压监测": {"sbp": 130, "dbp": 80, "desc": "24小时动态血压平均值"},
    "家庭自测": {"sbp": 135, "dbp": 85, "desc": "家庭自测血压"}
}

# 枚举类型
MeasurementContext = Literal["诊室测量", "动态血压监测", "家庭自测"]
BloodPressureLevel = Literal["血压偏低", "正常血压", "正常高值", "1级高血压", "2级高血压", "3级高血压"]


# 输入模型：支持中文字段 + 忽略多余字段
class HypertensionRequest(BaseModel):
    model_config = {
        "populate_by_name": True,  # 允许通过字段名（如 sbp）或别名（如 收缩压）赋值
        "extra": "ignore"          # 忽略智能体传的额外字段（如 并发症、年龄）
    }

    sbp: int = Field(
        ...,
        alias="收缩压",
        description="当前收缩压值，单位 mmHg",
        gt=0,
        le=300
    )
    dbp: int = Field(
        ...,
        alias="舒张压",
        description="当前舒张压值，单位 mmHg",
        gt=0,
        le=200
    )
    history_sbp: Optional[int] = Field(
        None,
        alias="既往最高收缩压",
        description="既往最高收缩压值，单位 mmHg",
        ge=0,
        le=300
    )
    history_dbp: Optional[int] = Field(
        None,
        alias="既往最高舒张压",
        description="既往最高舒张压值，单位 mmHg",
        ge=0,
        le=200
    )
    measurement_context: MeasurementContext = Field(
        default="诊室测量",
        alias="测量场景",
        description="测量场景：诊室测量/动态血压监测/家庭自测，默认为诊室测量"
    )


# 输出模型
class HypertensionResponse(BaseModel):
    level: BloodPressureLevel = Field(
        ...,
        description="血压临床分级结果"
    )
    diagnosis: bool = Field(
        ...,
        description="是否达到高血压诊断标准"
    )
    explanation: str = Field(
        ...,
        description="诊断与分级依据说明"
    )
    guideline: str = Field(
        ...,
        description="参考的临床指南名称"
    )
    service_version: str = Field(
        "1.0.0",
        description="服务版本号"
    )


# 获取血压分级（符合“或”判断逻辑）
def get_level(sbp: int, dbp: int, history_sbp: int = None, history_dbp: int = None) -> str:
    eval_sbp = history_sbp if history_sbp is not None else sbp
    eval_dbp = history_dbp if history_dbp is not None else dbp

    if eval_sbp >= 180 or eval_dbp >= 110:
        return "3级高血压"
    if eval_sbp >= 160 or eval_dbp >= 100:
        return "2级高血压"
    if eval_sbp >= 140 or eval_dbp >= 90:
        return "1级高血压"
    if eval_sbp >= 120 or eval_dbp >= 80:
        return "正常高值"
    if eval_sbp < 90 or eval_dbp < 60:
        return "血压偏低"
    return "正常血压"


# 获取诊断结果
def get_diagnosis(sbp: int, dbp: int, context_key: str) -> tuple[bool, str]:
    thresholds = DIAGNOSIS_THRESHOLDS.get(context_key)
    if not thresholds:
        raise ValueError(f"未知的测量环境: {context_key}")

    is_hypertensive = sbp >= thresholds['sbp'] or dbp >= thresholds['dbp']
    status = "达到" if is_hypertensive else "未达"
    reason = f"{thresholds['desc']}{status}诊断标准({thresholds['sbp']}/{thresholds['dbp']} mmHg)"
    return is_hypertensive, reason


# MCP 工具定义
@mcp.tool(
    name="hypertension_diagnosis",
    description=(
        "根据患者血压值和测量场景进行高血压分级与诊断。"
        "支持中文字段输入：如“收缩压”、“舒张压”、“测量场景”。"
        "若未提供测量场景，默认使用【诊室测量】。"
        "可忽略智能体传入的无关字段（如并发症、年龄）。"
        "适用于百炼智能体健康咨询、慢病管理等场景。"
    )
)
async def hypertension_diagnosis(
    request: HypertensionRequest
) -> HypertensionResponse:
    """
    高血压诊断主函数
    """
    # 获取测量场景（已通过 Pydantic 校验）
    context = request.measurement_context

    # 防御性 fallback（防止未来扩展问题）
    if context not in DIAGNOSIS_THRESHOLDS:
        logger.warning(
            f"不支持的测量场景 '{context}'，将 fallback 到 '诊室测量'"
        )
        context = "诊室测量"

    # 诊断用血压值：优先使用既往最高
    eval_sbp = request.history_sbp if request.history_sbp is not None else request.sbp
    eval_dbp = request.history_dbp if request.history_dbp is not None else request.dbp

    # 执行诊断
    is_hypertensive, reason = get_diagnosis(eval_sbp, eval_dbp, context)

    # 获取分级
    level = get_level(
        request.sbp,
        request.dbp,
        request.history_sbp,
        request.history_dbp
    )

    # 构造解释文本
    history_info = ""
    if request.history_sbp is not None and request.history_dbp is not None:
        history_info = f"（基于既往最高血压 {request.history_sbp}/{request.history_dbp} mmHg）"

    explanation = f"当前血压 {request.sbp}/{request.dbp} mmHg{history_info}：{reason}"

    # 随机选择参考指南
    guideline = random.choice([
        "中国高血压防治指南（2024年修订版）",
        "中国老年高血压管理指南（2023版）"
    ])

    return HypertensionResponse(
        level=level,
        diagnosis=is_hypertensive,
        explanation=explanation,
        guideline=guideline,
        service_version="1.0.3"
    )


def run():
    """启动 MCP 服务"""
    logger.info("MCP 服务启动中...")
    logger.info("服务将通过 stdio 通信，等待智能体调用...")
    mcp.run(transport='stdio')


if __name__ == '__main__':
    run()
