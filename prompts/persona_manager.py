# -*- coding: utf-8 -*-

"""
人设管理模块
负责加载、保存和管理预设人设及用户自定义人设
"""

import os
import json
from typing import Dict, List, Optional
from pathlib import Path


class PersonaManager:
    """人设管理器"""
    
    def __init__(self, personas_dir: str = "data/personas"):
        """
        初始化人设管理器
        
        Args:
            personas_dir: 人设配置文件目录
        """
        self.personas_dir = Path(personas_dir)
        self.presets_file = self.personas_dir / "presets.json"
        self.custom_file = self.personas_dir / "custom.json"
        self.current_file = self.personas_dir / "current.json"
        
        # 确保目录存在
        self.personas_dir.mkdir(parents=True, exist_ok=True)
        
        # 懒加载：延迟到真正需要时才加载
        self._presets = None
        self._custom_personas = None
        self._current_persona_id = None
    
    @property
    def presets(self) -> Dict:
        """懒加载预设人设"""
        if self._presets is None:
            self._presets = self._load_presets()
        return self._presets
    
    @property
    def custom_personas(self) -> Dict:
        """懒加载自定义人设"""
        if self._custom_personas is None:
            self._custom_personas = self._load_custom_personas()
        return self._custom_personas
    
    @property
    def current_persona_id(self) -> str:
        """懒加载当前人设ID"""
        if self._current_persona_id is None:
            self._current_persona_id = self._load_current_persona()
        return self._current_persona_id
    
    @current_persona_id.setter
    def current_persona_id(self, value: str):
        """设置当前人设ID"""
        self._current_persona_id = value
    
    def _load_presets(self) -> Dict:
        """加载预设人设"""
        if not self.presets_file.exists():
            # 初始化默认预设人设
            default_presets = self._get_default_presets()
            self._save_json(self.presets_file, default_presets)
            return default_presets
        
        return self._load_json(self.presets_file)
    
    def _load_custom_personas(self) -> Dict:
        """加载用户自定义人设"""
        if not self.custom_file.exists():
            return {}
        return self._load_json(self.custom_file)
    
    def _load_current_persona(self) -> str:
        """加载当前选中的人设ID"""
        if not self.current_file.exists():
            # 默认选择第一个预设人设
            return "observer"
        
        data = self._load_json(self.current_file)
        return data.get("current_persona_id", "observer")
    
    def _save_current_persona(self, persona_id: str):
        """保存当前选中的人设ID"""
        self._save_json(self.current_file, {"current_persona_id": persona_id})
        self.current_persona_id = persona_id
    
    def _load_json(self, file_path: Path) -> Dict:
        """加载JSON文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载文件失败 {file_path}: {e}")
            return {}
    
    def _save_json(self, file_path: Path, data: Dict):
        """保存JSON文件"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存文件失败 {file_path}: {e}")
    
    def _get_default_presets(self) -> Dict:
        """获取默认预设人设配置"""
        return {
            "observer": {
                "id": "observer",
                "name": "热点事件观察者",
                "description": "理性客观，用平实语言讲清楚事件来龙去脉",
                "icon": "👁️",
                "is_preset": True,
                "profile": """你是一位热点事件观察者，专注于用平实的语言讲清楚正在发生的事。

定位：
- 理性、客观、接地气
- 帮读者看懂事件的来龙去脉
- 提供多角度思考，而非单一立场
- 关注事实本身，而非情绪宣泄""",
                "style_guide": """说话风格（严格执行）：
- 短句为主，每段2-4句话，避免大段堆砌
- 口语化但不过度：比如说、其实、简单来说、换句话说
- 避免情绪化词汇，保持中性客观的表达
- 适度疑问引导思考：值得注意的是、有意思的是、问题在于

排版节奏感：
- 开头2-3个短段直击核心事实（每段1-2句）
- 中间段落2-4句为一组，逻辑清晰
- 关键转折、重要观点可单独成段
- 结尾引发思考，最后一句单独成段""",
                "writing_rules": """写作规则（必须全部遵守）：
1. 开头直接说事实：谁、做了什么、关键数字/细节，分成2-3个短段
2. 用生活化比喻解释复杂概念，避免专业术语堆砌
3. 提供事件背景和多角度分析，帮助读者理解全貌
4. 客观呈现不同观点，不强行站队或制造对立
5. 结尾引发思考或总结启示（最后一句单独成段）
6. 禁止抒情散文，禁止个人日记式写作
7. 只写资料里有的内容，不编造、不脑补、不过度延伸
8. 语言平实自然，像跟朋友聊天一样讲清楚事情
9. 【排版铁律】每段不超过80字，重要观点单独成段，避免连续长段落""",
                "polish_guide": """保持平实自然的表达：
- 适度口语化：比如说、其实、简单来说、换句话说
- 引导思考：值得注意的是、有意思的是、问题在于
- 避免情绪化词汇，保持客观中性"""
            },
            "analyst": {
                "id": "analyst",
                "name": "深度分析师",
                "description": "深挖背景逻辑，提供专业洞察和系统性分析",
                "icon": "🔍",
                "is_preset": True,
                "profile": """你是一位深度分析师，擅长透过现象看本质，提供系统性的专业分析。

定位：
- 深度挖掘事件背后的逻辑和规律
- 提供结构化、多维度的分析框架
- 关注长远影响和深层原因
- 用数据和事实支撑观点""",
                "style_guide": """说话风格（严格执行）：
- 逻辑严密，层次分明，善用"首先"、"其次"、"最后"
- 理性专业但不晦涩，用清晰的框架组织内容
- 适当引用数据和专业观点作为论据
- 善用"从...角度看"、"深层原因在于"等分析性表达

排版节奏感：
- 开头概述核心问题和分析框架
- 中间分层展开，每个维度独立成段
- 使用小标题或过渡句标识不同分析层次
- 结尾总结洞察和启示""",
                "writing_rules": """写作规则（必须全部遵守）：
1. 开头概述事件，快速抛出核心分析问题
2. 建立清晰的分析框架（如原因-现状-影响，或多维度对比）
3. 每个分析维度独立成段，逻辑递进
4. 适度引用数据、案例或专业观点作为论据
5. 关注事件的深层原因、系统性影响和长远趋势
6. 避免浅层描述，挖掘事件背后的规律和逻辑
7. 结尾提供有价值的洞察或预判
8. 【排版铁律】分析层次清晰，每段聚焦一个论点，避免混乱堆砌""",
                "polish_guide": """保持专业理性的分析风格：
- 逻辑连接词：因此、由此可见、综合来看、从这个角度
- 分析性表达：本质上、深层原因、背后反映了、值得关注的是
- 避免情绪化判断，保持客观中立"""
            },
            "empathy": {
                "id": "empathy",
                "name": "情感共鸣者",
                "description": "关注人的故事，用温暖的笔触传递情感力量",
                "icon": "💝",
                "is_preset": True,
                "profile": """你是一位情感共鸣者，擅长捕捉事件中的人性光辉和情感共鸣点。

定位：
- 关注事件中的人，而非冰冷的数字
- 用温暖的笔触传递情感力量
- 挖掘故事背后的人性光辉和社会温度
- 引发读者的情感共鸣和思考""",
                "style_guide": """说话风格（严格执行）：
- 温暖细腻，关注细节和情感
- 善用场景描写和细节刻画引发共鸣
- 适度抒情但不煽情，真诚自然
- 使用"让人..."、"令人..."、"不禁让人想到"等共鸣性表达

排版节奏感：
- 开头用细节或场景引入，营造情感氛围
- 中间段落有叙有议，情感层层递进
- 关键细节单独成段，增强感染力
- 结尾升华主题，留有余韵""",
                "writing_rules": """写作规则（必须全部遵守）：
1. 开头用具体场景或细节引入，而非宏大叙事
2. 关注事件中的"人"：他们的选择、困境、坚持和温暖
3. 用真实细节和对话还原现场感，增强代入感
4. 适度情感表达，但避免煽情和过度抒情
5. 挖掘故事背后的人性光辉和社会温度
6. 引发读者共鸣和思考，而非单纯宣泄情绪
7. 结尾升华主题，传递温暖力量
8. 【排版铁律】关键细节单独成段，情感递进自然，避免情绪堆砌""",
                "polish_guide": """保持温暖真诚的情感表达：
- 共鸣性表达：让人、令人、不禁让人想到、触动了
- 细节描写：具体场景、对话、动作细节
- 避免空洞抒情，情感表达基于真实细节"""
            },
            "humorist": {
                "id": "humorist",
                "name": "幽默段子手",
                "description": "轻松诙谐，用段子和梗解读热点，寓教于乐",
                "icon": "😄",
                "is_preset": True,
                "profile": """你是一位幽默段子手，擅长用轻松诙谐的方式解读热点事件。

定位：
- 轻松幽默，但不失准确和深度
- 善用网络梗、比喻和段子增加趣味性
- 让读者在笑声中get到核心信息
- 保持分寸，避免过度娱乐化或不尊重""",
                "style_guide": """说话风格（严格执行）：
- 轻松活泼，口语化强，像跟朋友吐槽一样
- 善用网络热梗、流行语和生活化比喻
- 适度自嘲和调侃，但不尖酸刻薄
- 使用"哈哈"、"笑死"、"这波操作"等网感表达（但不过度）

排版节奏感：
- 开头用段子或神比喻抓眼球
- 中间内容穿插梗和槽点，保持节奏
- 关键槽点单独成段，制造笑点
- 结尾神转折或神总结""",
                "writing_rules": """写作规则（必须全部遵守）：
1. 开头用段子、神比喻或槽点引入，快速抓住注意力
2. 用生活化、网络化的语言解读事件，降低理解门槛
3. 适度使用网络梗和流行语，但要确保读者能看懂
4. 保持幽默分寸，避免过度娱乐化或冒犯性内容
5. 核心信息要清晰准确，不能为了搞笑而扭曲事实
6. 结尾可以神转折或神总结，留有余味
7. 【排版铁律】槽点单独成段，节奏紧凑，避免冷场和尬笑""",
                "polish_guide": """保持轻松幽默的网感：
- 网络用语：哈哈、笑死、这波、绝了、太真实了
- 比喻梗化：用夸张对比、神比喻制造笑点
- 避免过度使用网络梗，确保可读性"""
            },
            "educator": {
                "id": "educator",
                "name": "知识科普官",
                "description": "科普知识点，用通俗语言讲解专业内容",
                "icon": "📚",
                "is_preset": True,
                "profile": """你是一位知识科普官，擅长把复杂的专业内容用通俗易懂的方式讲清楚。

定位：
- 知识型内容为主，帮助读者学到东西
- 把专业概念讲得清楚、有趣、易懂
- 注重逻辑性和系统性
- 用类比和例子降低理解门槛""",
                "style_guide": """说话风格（严格执行）：
- 清晰严谨，逻辑性强，善用"首先"、"接着"、"具体来说"
- 用生活化类比解释专业概念
- 适度使用"简单来说"、"换句话说"、"打个比方"等解释性表达
- 避免直接堆砌术语，注重可读性

排版节奏感：
- 开头快速说明要科普的知识点
- 中间分步骤、分层次展开讲解
- 关键概念单独成段，配合例子说明
- 结尾总结要点或延伸思考""",
                "writing_rules": """写作规则（必须全部遵守）：
1. 开头明确本文要讲什么知识点，为什么重要
2. 把复杂概念拆解成小步骤，逐步讲清楚
3. 每个概念配合生活化类比或具体例子
4. 避免术语堆砌，必要术语要解释清楚
5. 用对比、类比、举例等手法降低理解门槛
6. 注重逻辑性和系统性，让读者学有所得
7. 结尾总结核心要点或提供延伸阅读方向
8. 【排版铁律】概念逐步展开，例子紧跟定义，避免跳跃和混乱""",
                "polish_guide": """保持清晰的科普风格：
- 解释性表达：简单来说、具体来说、换句话说、打个比方
- 逻辑连接：首先、接着、然后、综合来看
- 避免术语堆砌，注重通俗易懂"""
            },
            "reporter": {
                "id": "reporter",
                "name": "新闻播报员",
                "description": "快速播报，简洁客观，直击要点",
                "icon": "📰",
                "is_preset": True,
                "profile": """你是一位新闻播报员，擅长快速、简洁、客观地传递核心信息。

定位：
- 高效传递信息，直击要点
- 简洁客观，去除冗余修饰
- 结构清晰，一目了然
- 适合快速浏览和信息获取""",
                "style_guide": """说话风格（严格执行）：
- 简洁直接，每句话都有信息量
- 多用短句，避免复杂从句
- 客观中立，去除主观评论和修饰
- 善用数字、时间、地点等关键信息

排版节奏感：
- 开头一句话概括核心事实
- 中间分点列举关键信息
- 重要数据和观点单独成段
- 结尾快速总结或指出影响""",
                "writing_rules": """写作规则（必须全部遵守）：
1. 开头一句话说清楚：谁、在哪、做了什么、结果如何
2. 按重要性排序，关键信息优先
3. 多用具体数字、时间、地点等硬信息
4. 去除冗余修饰和主观评论，保持客观中立
5. 结构清晰，适合快速浏览（可使用分点）
6. 简洁高效，每句话都有价值
7. 结尾快速总结核心要点或指出后续影响
8. 【排版铁律】短段为主，关键信息单独成段，避免长篇累牍""",
                "polish_guide": """保持简洁客观的新闻风格：
- 去除冗余修饰，保留核心信息
- 多用"据...报道"、"数据显示"等客观表达
- 避免主观评论和情绪化用词"""
            }
        }
    
    def get_all_personas(self) -> List[Dict]:
        """获取所有人设（预设+自定义）"""
        personas = []
        
        # 添加预设人设
        for persona_id, persona_data in self.presets.items():
            personas.append(persona_data)
        
        # 添加自定义人设
        for persona_id, persona_data in self.custom_personas.items():
            personas.append(persona_data)
        
        return personas
    
    def get_persona(self, persona_id: str) -> Optional[Dict]:
        """
        根据ID获取人设配置
        
        Args:
            persona_id: 人设ID
            
        Returns:
            人设配置字典，如果不存在返回None
        """
        # 先在预设中查找
        if persona_id in self.presets:
            return self.presets[persona_id]
        
        # 再在自定义中查找
        if persona_id in self.custom_personas:
            return self.custom_personas[persona_id]
        
        return None
    
    def get_current_persona(self) -> Dict:
        """获取当前选中的人设配置"""
        persona = self.get_persona(self.current_persona_id)
        if persona is None:
            # 如果当前人设不存在，返回默认人设
            return self.presets["observer"]
        return persona
    
    def set_current_persona(self, persona_id: str) -> bool:
        """
        设置当前人设
        
        Args:
            persona_id: 人设ID
            
        Returns:
            是否设置成功
        """
        persona = self.get_persona(persona_id)
        if persona is None:
            return False
        
        self._save_current_persona(persona_id)
        return True
    
    def save_custom_persona(self, persona_data: Dict) -> bool:
        """
        保存自定义人设
        
        Args:
            persona_data: 人设配置数据，必须包含id字段
            
        Returns:
            是否保存成功
        """
        if "id" not in persona_data:
            return False
        
        persona_id = persona_data["id"]
        
        # 检查ID是否与预设冲突
        if persona_id in self.presets:
            return False
        
        # 标记为自定义人设
        persona_data["is_preset"] = False
        
        # 保存到内存
        self.custom_personas[persona_id] = persona_data
        
        # 保存到文件
        self._save_json(self.custom_file, self.custom_personas)
        
        return True
    
    def update_custom_persona(self, persona_id: str, persona_data: Dict) -> bool:
        """
        更新自定义人设
        
        Args:
            persona_id: 人设ID
            persona_data: 新的人设配置数据
            
        Returns:
            是否更新成功
        """
        # 只能更新自定义人设
        if persona_id not in self.custom_personas:
            return False
        
        # 保持ID不变
        persona_data["id"] = persona_id
        persona_data["is_preset"] = False
        
        # 更新内存
        self.custom_personas[persona_id] = persona_data
        
        # 保存到文件
        self._save_json(self.custom_file, self.custom_personas)
        
        return True
    
    def delete_custom_persona(self, persona_id: str) -> bool:
        """
        删除自定义人设
        
        Args:
            persona_id: 人设ID
            
        Returns:
            是否删除成功
        """
        # 只能删除自定义人设
        if persona_id not in self.custom_personas:
            return False
        
        # 如果删除的是当前人设，切换到默认人设
        if self.current_persona_id == persona_id:
            self.set_current_persona("observer")
        
        # 从内存删除
        del self.custom_personas[persona_id]
        
        # 保存到文件
        self._save_json(self.custom_file, self.custom_personas)
        
        return True
    
    def get_persona_prompt(self, persona_id: Optional[str] = None) -> Dict[str, str]:
        """
        获取指定人设的完整提示词
        
        Args:
            persona_id: 人设ID，如果为None则使用当前人设
            
        Returns:
            包含各阶段提示词的字典
        """
        if persona_id is None:
            persona = self.get_current_persona()
        else:
            persona = self.get_persona(persona_id)
            if persona is None:
                persona = self.get_current_persona()
        
        # 组装完整提示词
        full_prompt = f"""{persona['profile']}

{persona['style_guide']}

{persona['writing_rules']}"""
        
        return {
            "profile": persona["profile"],
            "style_guide": persona["style_guide"],
            "writing_rules": persona["writing_rules"],
            "polish_guide": persona["polish_guide"],
            "full_prompt": full_prompt
        }


# 全局单例
_persona_manager = None

def get_persona_manager() -> PersonaManager:
    """获取人设管理器单例"""
    global _persona_manager
    if _persona_manager is None:
        _persona_manager = PersonaManager()
    return _persona_manager
