"""厕所侦探模块 - 专门调查AdventureX厕所事件的侦探工具"""

import random
import time
from datetime import datetime

class ToiletDetective:
    """厕所侦探 - 专业调查厕所犯罪现场"""
    
    def __init__(self, detective_name="福尔摩斯·厕所"):
        self.name = detective_name
        self.investigation_tools = [
            "放大镜", "气味分析仪", "DNA检测包", "监控录像", 
            "证人访谈记录", "厕纸纤维分析", "脚印石膏模型"
        ]
        self.suspects = []
        self.evidence = []
        self.investigation_started = False
        
    def start_investigation(self):
        """开始调查"""
        self.investigation_started = True
        print(f"🕵️ 侦探{self.name}开始调查AdventureX厕所事件！")
        print("🚽 案发现场：黑客松会场厕所")
        print("💰 悬赏金额：5000元")
        print("😷 受害者：一名孕妇（因恶臭呕吐）")
        return "调查已开始"
    
    def collect_evidence(self):
        """收集证据"""
        if not self.investigation_started:
            return "请先开始调查！"
            
        possible_evidence = [
            "厕所门把手上的指纹",
            "可疑的脚印痕迹", 
            "异常的气味分子",
            "监控录像中的模糊身影",
            "厕纸使用量异常记录",
            "洗手液使用痕迹",
            "马桶冲水时间记录",
            "现场遗留的程序员T恤纤维",
            "键盘手指茧痕迹",
            "咖啡因代谢物检测"
        ]
        
        new_evidence = random.choice(possible_evidence)
        if new_evidence not in self.evidence:
            self.evidence.append(new_evidence)
            print(f"🔍 发现新证据：{new_evidence}")
        else:
            print("🔍 重复搜索，未发现新证据")
            
        return self.evidence
    
    def interview_witness(self, witness_name="匿名孕妇"):
        """访谈证人"""
        testimonies = [
            "我当时正要进厕所，突然闻到一股前所未有的恶臭...",
            "那个味道简直像是代码bug和隔夜外卖的混合体",
            "我看到一个穿着黑客松T恤的身影匆忙离开",
            "听到有人在厕所里嘟囔着'这个bug终于解决了'",
            "那人走路的姿势很奇怪，像是憋了很久的样子",
            "我发誓我听到了键盘敲击的声音，在厕所里！",
            "现场还有笔记本电脑的风扇声"
        ]
        
        testimony = random.choice(testimonies)
        print(f"👥 证人{witness_name}证词：{testimony}")
        return testimony
    
    def analyze_suspects(self):
        """分析嫌疑人"""
        hackathon_participants = [
            "熬夜三天的全栈工程师",
            "只喝咖啡不吃饭的前端开发", 
            "调试到崩溃的后端程序员",
            "第一次参加黑客松的大学生",
            "连续编程36小时的架构师",
            "靠红牛续命的移动端开发",
            "压力山大的项目经理",
            "吃了太多外卖的数据科学家"
        ]
        
        self.suspects = random.sample(hackathon_participants, 3)
        print("🎯 主要嫌疑人列表：")
        for i, suspect in enumerate(self.suspects, 1):
            suspicion_level = random.randint(60, 95)
            print(f"   {i}. {suspect} (嫌疑度: {suspicion_level}%)")
            
        return self.suspects
    
    def generate_investigation_report(self):
        """生成调查报告"""
        if not self.investigation_started:
            return "调查尚未开始，无法生成报告"
            
        report = {
            "案件编号": f"AX2025-TOILET-{random.randint(1000, 9999)}",
            "调查员": self.name,
            "调查时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "案件状态": "调查中",
            "证据数量": len(self.evidence),
            "嫌疑人数量": len(self.suspects),
            "破案概率": f"{random.randint(15, 85)}%",
            "建议行动": "继续监控厕所，增加悬赏金额",
            "特别备注": "此案件已引起黑客松历史上最大规模的厕所恐慌"
        }
        
        return report
    
    def predict_perpetrator(self):
        """预测真凶"""
        if not self.suspects:
            self.analyze_suspects()
            
        predictions = [
            "根据代码提交时间分析，真凶很可能是在凌晨3点还在写bug的程序员",
            "气味分析显示，凶手最近食用了大量外卖和咖啡", 
            "脚印分析表明，此人长期久坐，腿部肌肉萎缩",
            "心理画像：压力巨大，急需释放，选择了最不合适的时机",
            "DNA分析显示，凶手体内咖啡因含量超标300%"
        ]
        
        main_suspect = self.suspects[0] if self.suspects else "未知嫌疑人"
        prediction = random.choice(predictions)
        
        return {
            "主要嫌疑人": main_suspect,
            "预测依据": prediction,
            "抓捕建议": "在下一次黑客松的厕所附近设置埋伏",
            "风险评估": "极高 - 可能再次作案"
        }