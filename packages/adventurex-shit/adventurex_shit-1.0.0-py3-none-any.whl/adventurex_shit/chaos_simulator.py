"""混乱模拟器 - 模拟AdventureX厕所事件引发的各种混乱场景"""

import random
import time
from typing import Dict, List

class ChaosSimulator:
    """混乱模拟器 - 重现和预测厕所事件的混乱程度"""
    
    def __init__(self):
        self.chaos_events = []
        self.chaos_level = 0
        self.affected_people = []
        self.emergency_responses = []
        
    def trigger_initial_incident(self):
        """触发初始事件"""
        print("💩 [事件触发] 某位黑客松参与者在厕所完成了'大作'...")
        time.sleep(1)
        print("😷 [连锁反应] 孕妇进入厕所...")
        time.sleep(1)
        print("🤮 [灾难爆发] 孕妇因恶臭开始呕吐！")
        
        self.chaos_level = 30
        self.chaos_events.append("厕所生化武器事件")
        return "初始混乱已触发"
    
    def simulate_crowd_reaction(self, crowd_size=200):
        """模拟人群反应"""
        reactions = [
            "惊恐逃离现场",
            "围观拍照发朋友圈", 
            "捂鼻子快速通过",
            "开始寻找真凶",
            "要求主办方解释",
            "讨论是否继续参赛",
            "组织临时清洁队",
            "开始传播小道消息"
        ]
        
        affected_count = min(crowd_size, random.randint(50, 150))
        self.affected_people = random.sample(reactions, min(len(reactions), affected_count//25))
        
        print(f"👥 [人群反应] {affected_count}人受到影响：")
        for reaction in self.affected_people:
            print(f"   - {reaction}")
            
        self.chaos_level += len(self.affected_people) * 5
        return self.affected_people
    
    def simulate_social_media_explosion(self):
        """模拟社交媒体爆炸"""
        posts = [
            "#AdventureX2025 厕所惊魂，现场一片混乱！",
            "黑客松变成了'黑客屎'，谁干的？！",
            "5000元悬赏找厕所真凶，我要当赏金猎人！",
            "孕妇在厕所吐了，这届黑客松太刺激了",
            "程序员的肠胃和代码一样不稳定",
            "厕所CSI现场，福尔摩斯都要退休了",
            "AdventureX官方：我们在找一个会拉屎的程序员"
        ]
        
        viral_posts = random.sample(posts, random.randint(3, 6))
        
        print("📱 [社交媒体爆炸]")
        for post in viral_posts:
            likes = random.randint(100, 5000)
            shares = random.randint(50, 1000)
            print(f"   {post} (👍{likes} 🔄{shares})")
            
        self.chaos_level += len(viral_posts) * 10
        return viral_posts
    
    def simulate_organizer_response(self):
        """模拟主办方应对"""
        responses = [
            "紧急关闭所有厕所进行消毒",
            "发布5000元悬赏公告",
            "召开紧急会议讨论对策", 
            "联系专业清洁公司",
            "向孕妇道歉并提供医疗支持",
            "加强厕所监控措施",
            "考虑是否继续举办活动",
            "准备危机公关声明"
        ]
        
        self.emergency_responses = random.sample(responses, random.randint(4, 7))
        
        print("🏢 [主办方应急响应]")
        for response in self.emergency_responses:
            print(f"   ✅ {response}")
            
        self.chaos_level += len(self.emergency_responses) * 3
        return self.emergency_responses
    
    def simulate_bounty_hunter_activity(self):
        """模拟赏金猎人活动"""
        hunter_activities = [
            "组建厕所调查小组",
            "分析所有参赛者的代码提交时间",
            "检查监控录像寻找线索",
            "访谈现场目击者",
            "分析厕所使用记录",
            "创建嫌疑人档案",
            "设置厕所陷阱等待真凶再次出现",
            "悬赏金额谈判"
        ]
        
        active_hunters = random.randint(10, 50)
        activities = random.sample(hunter_activities, random.randint(3, 6))
        
        print(f"🎯 [赏金猎人活动] {active_hunters}名猎人参与：")
        for activity in activities:
            print(f"   🔍 {activity}")
            
        self.chaos_level += active_hunters // 5
        return {"hunters": active_hunters, "activities": activities}
    
    def calculate_total_chaos(self):
        """计算总混乱度"""
        chaos_factors = {
            "初始事件": 30,
            "人群恐慌": len(self.affected_people) * 5,
            "社交媒体": len(self.chaos_events) * 10,
            "主办方应对": len(self.emergency_responses) * 3,
            "赏金猎人": 25
        }
        
        total = sum(chaos_factors.values())
        
        if total >= 100:
            level = "史无前例的混乱"
            description = "这已经不是黑客松了，这是生化危机现场！"
        elif total >= 80:
            level = "极度混乱"
            description = "整个会场陷入恐慌，建议立即疏散"
        elif total >= 60:
            level = "高度混乱"
            description = "情况严重，需要专业危机处理团队"
        elif total >= 40:
            level = "中度混乱"
            description = "可控范围内的混乱，但需要及时处理"
        else:
            level = "轻微混乱"
            description = "只是一个小插曲，很快就会过去"
            
        return {
            "总混乱度": total,
            "混乱等级": level,
            "描述": description,
            "混乱因子分析": chaos_factors,
            "建议措施": "增加厕所数量，改善通风系统，设置专门的程序员厕所"
        }
    
    def run_full_simulation(self):
        """运行完整的混乱模拟"""
        print("🎬 开始AdventureX厕所事件完整混乱模拟...\n")
        
        # 触发初始事件
        self.trigger_initial_incident()
        print()
        
        # 人群反应
        self.simulate_crowd_reaction()
        print()
        
        # 社交媒体爆炸
        self.simulate_social_media_explosion()
        print()
        
        # 主办方应对
        self.simulate_organizer_response()
        print()
        
        # 赏金猎人活动
        self.simulate_bounty_hunter_activity()
        print()
        
        # 计算总混乱度
        chaos_result = self.calculate_total_chaos()
        print("📊 [混乱度分析结果]")
        for key, value in chaos_result.items():
            print(f"   {key}: {value}")
            
        return chaos_result
    
    def predict_future_chaos(self, days_ahead=7):
        """预测未来混乱趋势"""
        predictions = []
        
        for day in range(1, days_ahead + 1):
            events = [
                "网络热度持续发酵",
                "更多赏金猎人加入", 
                "媒体开始报道此事件",
                "其他黑客松开始加强厕所管理",
                "出现模仿犯罪",
                "真凶主动自首",
                "悬赏金额增加",
                "事件逐渐平息"
            ]
            
            daily_event = random.choice(events)
            chaos_trend = random.choice(["上升", "下降", "持平"])
            
            predictions.append({
                "第{}天".format(day): daily_event,
                "混乱趋势": chaos_trend
            })
            
        return predictions