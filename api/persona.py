# -*- coding: utf-8 -*-

"""
人设管理 API
提供人设的增删改查和切换功能
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from prompts.persona_manager import get_persona_manager

router = APIRouter()


class PersonaData(BaseModel):
    """人设数据模型"""
    id: Optional[str] = None
    name: str
    description: str
    icon: str = "✨"
    profile: str
    style_guide: str
    writing_rules: str
    polish_guide: str


class SelectPersonaRequest(BaseModel):
    """选择人设请求模型"""
    persona_id: str


@router.get("/personas")
async def get_all_personas():
    """
    获取所有人设（预设+自定义）
    
    Returns:
        {
            "personas": [...],
            "current_persona_id": "observer"
        }
    """
    try:
        manager = get_persona_manager()
        personas = manager.get_all_personas()
        current_persona_id = manager.current_persona_id
        
        return {
            "personas": personas,
            "current_persona_id": current_persona_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取人设列表失败: {str(e)}")


@router.get("/personas/current")
async def get_current_persona():
    """
    获取当前选中的人设
    
    Returns:
        当前人设的完整配置
    """
    try:
        manager = get_persona_manager()
        persona = manager.get_current_persona()
        return persona
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取当前人设失败: {str(e)}")


@router.get("/personas/{persona_id}")
async def get_persona(persona_id: str):
    """
    根据ID获取指定人设
    
    Args:
        persona_id: 人设ID
        
    Returns:
        人设配置
    """
    try:
        manager = get_persona_manager()
        persona = manager.get_persona(persona_id)
        
        if persona is None:
            raise HTTPException(status_code=404, detail=f"人设不存在: {persona_id}")
        
        return persona
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取人设失败: {str(e)}")


@router.post("/personas")
async def create_persona(persona_data: PersonaData):
    """
    创建自定义人设
    
    Args:
        persona_data: 人设配置数据
        
    Returns:
        创建成功的人设配置
    """
    try:
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"收到创建人设请求: {persona_data}")
        
        manager = get_persona_manager()
        
        # 生成唯一ID（如果未提供）
        if not persona_data.id:
            import time
            persona_data.id = f"custom_{int(time.time())}"
        
        # 转换为字典
        persona_dict = persona_data.model_dump()
        logger.info(f"人设数据转换成功: {persona_dict}")
        
        # 保存
        success = manager.save_custom_persona(persona_dict)
        
        if not success:
            raise HTTPException(status_code=400, detail="保存人设失败，可能ID已存在或为预设人设ID")
        
        return {
            "message": "人设创建成功",
            "persona": persona_dict
        }
    except HTTPException:
        raise
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"创建人设失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"创建人设失败: {str(e)}")


@router.put("/personas/{persona_id}")
async def update_persona(persona_id: str, persona_data: PersonaData):
    """
    更新自定义人设
    
    Args:
        persona_id: 人设ID
        persona_data: 新的人设配置数据
        
    Returns:
        更新后的人设配置
    """
    try:
        manager = get_persona_manager()
        
        # 转换为字典
        persona_dict = persona_data.model_dump()
        persona_dict["id"] = persona_id  # 确保ID一致
        
        # 更新
        success = manager.update_custom_persona(persona_id, persona_dict)
        
        if not success:
            raise HTTPException(
                status_code=400, 
                detail="更新人设失败，只能更新自定义人设"
            )
        
        return {
            "message": "人设更新成功",
            "persona": persona_dict
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新人设失败: {str(e)}")


@router.delete("/personas/{persona_id}")
async def delete_persona(persona_id: str):
    """
    删除自定义人设
    
    Args:
        persona_id: 人设ID
        
    Returns:
        删除结果
    """
    try:
        manager = get_persona_manager()
        
        success = manager.delete_custom_persona(persona_id)
        
        if not success:
            raise HTTPException(
                status_code=400, 
                detail="删除人设失败，只能删除自定义人设"
            )
        
        return {
            "message": "人设删除成功",
            "persona_id": persona_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除人设失败: {str(e)}")


@router.post("/personas/select")
async def select_persona(request: SelectPersonaRequest):
    """
    设置当前使用的人设
    
    Args:
        request: 包含persona_id的请求
        
    Returns:
        切换结果
    """
    try:
        manager = get_persona_manager()
        
        success = manager.set_current_persona(request.persona_id)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"人设不存在: {request.persona_id}")
        
        return {
            "message": "人设切换成功",
            "current_persona_id": request.persona_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"切换人设失败: {str(e)}")
