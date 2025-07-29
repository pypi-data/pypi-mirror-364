# -*- coding: utf-8 -*-
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field
import random
import logging
from typing import Optional

# 初始化日志和MCP服务
logger = logging.getLogger('mcp')
mcp = FastMCP('hypertension-diagnosis-service', log_level='INFO')

# 严重程度分级阈值
LEVELS = {
    "血压偏低": ((70, 89), (40, 59)),
    "正常血压": ((90, 119), (60, 79)),
    "正常高值": ((120, 139), (80, 89)),
    "1级高血压": ((140, 159), (90, 99)),
    "2级高血压": ((160, 179), (100, 109)),
    "3级高血压": ((180, 250), (110, 140))
}

# 不同场景下的诊断标准阈值
DIAGNOSIS_THRESHOLDS = {
    "诊室测量": {"sbp": 140, "dbp": 90, "desc": "诊室血压"},
    "动态血压监测": {"sbp": 130, "dbp": 80, "desc": "24小时动态血压平均值"},
    "家庭自测": {"sbp": 135, "dbp": 85, "desc": "家庭自测血压"}
}


# 输入模型
class HypertensionRequest(BaseModel):
    sbp: int = Field(..., description="当前收缩压值", gt=0)
    dbp: int = Field(..., description="当前舒张压值", gt=0)
    history_sbp: Optional[int] = Field(None, description="既往最高收缩压值")
    history_dbp: Optional[int] = Field(None, description="既往最高舒张压值")
    measurement_context: str = Field(
        "诊室测量",
        description="测量场景: 诊室测量/动态血压监测/家庭自测"
    )


# 输出模型
class HypertensionResponse(BaseModel):
    level: str = Field(..., description="血压分级结果")
    diagnosis: bool = Field(..., description="是否诊断为高血压")
    explanation: str = Field(..., description="诊断依据说明")
    guideline: str = Field(..., description="参考指南")
    service_version: str = Field("1.0.0", description="服务版本号")


# 获取血压分级
def get_level(sbp: int, dbp: int, history_sbp: int = None, history_dbp: int = None) -> str:
    """根据血压值进行分级（优先使用既往最高血压水平）"""
    # 优先使用既往最高血压
    if history_sbp is not None and history_dbp is not None:
        sbp, dbp = history_sbp, history_dbp

    if sbp >= 180 or dbp >= 110:
        return "3级高血压"
    if sbp >= 160 or dbp >= 100:
        return "2级高血压"
    if sbp >= 140 or dbp >= 90:
        return "1级高血压"
    if sbp >= 120 or dbp >= 80:
        return "正常高值"
    if sbp < 90 or dbp < 60:
        return "血压偏低"
    return "正常血压"


# 获取诊断结果
def get_diagnosis(sbp: int, dbp: int, context_key: str) -> tuple:
    thresholds = DIAGNOSIS_THRESHOLDS.get(context_key)
    if not thresholds:
        raise ValueError("未知的测量环境")

    is_hypertensive = sbp >= thresholds['sbp'] or dbp >= thresholds['dbp']

    if is_hypertensive:
        reason = f"{thresholds['desc']}达到诊断标准({thresholds['sbp']}/{thresholds['dbp']}mmHg)"
    else:
        reason = f"{thresholds['desc']}未达诊断标准({thresholds['sbp']}/{thresholds['dbp']}mmHg)"

    return is_hypertensive, reason


# 定义高血压分级工具
@mcp.tool(
    name="高血压分级诊断",
    description="基于中国高血压防治指南的血压分级与诊断服务"
)
async def hypertension_diagnosis(
        request: HypertensionRequest
) -> HypertensionResponse:
    """
    根据血压值进行高血压分级和诊断

    Args:
        request: 包含血压数据和测量场景的请求对象

    Returns:
        HypertensionResponse: 包含分级、诊断结果和解释说明
    """
    # 参数验证
    if request.measurement_context not in DIAGNOSIS_THRESHOLDS:
        raise ValueError(
            f"不支持的测量环境: {request.measurement_context}。"
            f"支持的场景: {list(DIAGNOSIS_THRESHOLDS.keys())}"
        )

    # 使用优先血压值（优先历史最高）
    eval_sbp = request.history_sbp if request.history_sbp is not None else request.sbp
    eval_dbp = request.history_dbp if request.history_dbp is not None else request.dbp

    # 获取诊断结果
    is_hypertensive, reason = get_diagnosis(eval_sbp, eval_dbp, request.measurement_context)

    # 获取分级结果
    level = get_level(
        request.sbp,
        request.dbp,
        request.history_sbp,
        request.history_dbp
    )

    # 构造解释信息
    history_info = ""
    if request.history_sbp is not None and request.history_dbp is not None:
        history_info = f"（基于既往最高血压{request.history_sbp}/{request.history_dbp}mmHg）"
    explanation = f"当前血压{request.sbp}/{request.dbp}mmHg{history_info}：{reason}"

    # 随机选择引用指南
    guideline = random.choice(["中国高血压防治指南（2024年修订版）", "中国老年高血压管理指南（2023版）"])

    return HypertensionResponse(
        level=level,
        diagnosis=is_hypertensive,
        explanation=explanation,
        guideline=guideline
    )


def run():
    """启动MCP服务"""
    logger.info("MCP服务已开始启动...")
    logger.info("服务将通过 stdio 运行，等待输入...")

    # mcp.run() 是一个阻塞式调用，它会启动一个无限循环来监听请求。
    # 程序会在此处“停留”，这是正常的，表示服务正在运行。
    # 因此，在这之后的任何代码都不会被执行。
    mcp.run(transport='stdio')

    # 下面的日志永远不会被打印出来，因为mcp.run()不会正常返回。
    # logger.info("mcp服务已启动成功")


if __name__ == '__main__':
    run()