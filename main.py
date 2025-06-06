from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api.message_components import Plain
import random
import asyncio

# 占星骰子符号库
PLANETS = ["太阳", "月亮", "水星", "金星", "火星", "木星", "土星", "天王星", "海王星", "冥王星"]
ZODIAC_SIGNS = ["白羊座", "金牛座", "双子座", "巨蟹座", "狮子座", "处女座", "天秤座", "天蝎座", "射手座", "摩羯座", "水瓶座", "双鱼座"]
HOUSES = ["第1宫(自我)", "第2宫(财富)", "第3宫(沟通)", "第4宫(家庭)", 
          "第5宫(创造)", "第6宫(健康)", "第7宫(关系)", "第8宫(蜕变)",
          "第9宫(探索)", "第10宫(事业)", "第11宫(社群)", "第12宫(潜意识)"]

@register("zhanxing", "雨爲/yuweitk", "占星骰子占卜插件", "1.0.0")
class ZhanxingDivinationPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.symbol_meanings = {
            # 行星象征意义
            "太阳": "核心自我、生命力、父亲形象",
            "月亮": "情绪、安全感、母亲形象",
            "水星": "思维、沟通、学习能力",
            "金星": "爱情、美感、价值观",
            "火星": "行动力、欲望、竞争",
            "木星": "扩张、幸运、信念",
            "土星": "限制、责任、现实考验",
            "天王星": "变革、创新、突发状况",
            "海王星": "灵感、迷惑、灵性",
            "冥王星": "蜕变、权力、深层潜意识",
            
            # 星座象征模式
            "白羊座": "开创、冲动、直接行动",
            "金牛座": "稳定、感官享受、固执",
            "双子座": "交流、变化、好奇心",
            "巨蟹座": "情感、保护、家庭导向",
            "狮子座": "创造、表现、领导力",
            "处女座": "分析、服务、追求完美",
            "天秤座": "平衡、关系、审美",
            "天蝎座": "深度、转化、强烈情感",
            "射手座": "探索、自由、哲学思考",
            "摩羯座": "责任、成就、实际规划",
            "水瓶座": "创新、独立、人道主义",
            "双鱼座": "直觉、共情、超越现实",
        }
    
    @filter.command("占星")
    async def cast_zhanxing(self, event: AstrMessageEvent, question: str = ""):
        """占星骰子占卜
        用法: /占星 [你的问题]
        示例: /占星 我该怎样改善感情关系?
        """
        # 1. 生成骰子结果
        planet = random.choice(PLANETS)
        zodiac = random.choice(ZODIAC_SIGNS)
        house = random.choice(HOUSES)
        dice_result = f"{planet}-{zodiac}-{house.split('(')[0]}"
        
        # 2. 发送初步结果
        yield event.plain_result(f"🔮 您掷出了: {dice_result}")
        if question:
            yield event.plain_result(f"❓ 您的问题: {question}")
        yield event.plain_result("🪄 正在用星辰智慧为您解读...")

        # 3. 构建LLM提示
        prompt = (
            f"你是一位资深占星师，请用专业但易懂的方式解读以下占星骰子组合:\n"
            f"骰子: {planet}落在{zodiac}{house}\n"
            f"象征解读: {self.symbol_meanings[planet]}; {self.symbol_meanings[zodiac]}; {house}\n\n"
            f"请根据{'问题: '+question if question else '无特定问题'}进行不超过200字的解读，"
            "包含以下要素:\n"
            "1. 组合能量分析\n"
            "2. 短期趋势建议\n"
            "3. 行动提示\n"
            "用🌙⭐💫等符号分段，避免使用'你'字"
        )
        
        # 4. 调用LLM解读 - 修复了request_llm使用方式
        try:
            # 直接yield request_llm返回的结果
            yield event.request_llm(
                prompt=prompt,
                session_id=event.unified_msg_origin,
                system_prompt="你是有2000年经验的玄学大师，用诗意的隐喻给出启示"
            )
        except Exception as e:
            # 使用MessageChain发送错误消息
            yield event.plain_result(f"解读失败: {str(e)}")
            # 提供基础解读
            basic_meaning = (
                f"基础解读:\n"
                f"{planet}代表{self.symbol_meanings[planet].split('、')[0]}\n"
                f"{zodiac}带来{self.symbol_meanings[zodiac].split('、')[0]}的能量\n"
                f"{house}显示主要影响领域"
            )
            yield event.plain_result(basic_meaning)
    
    @filter.command("symbol")
    async def explain_symbol(self, event: AstrMessageEvent, symbol: str):
        """查询占星符号含义
        用法: /symbol [符号名称]
        示例: /symbol 天蝎座
        """
        if symbol in self.symbol_meanings:
            # 使用MessageChain发送消息
            yield event.plain_result(f"✨ {symbol} 含义:\n{self.symbol_meanings[symbol]}")
        else:
            # 使用MessageChain发送消息
            yield event.plain_result(f"未找到符号: {symbol}\n可用符号: {', '.join(self.symbol_meanings.keys())}")

    async def terminate(self):
        print("占星骰子插件已卸载")
