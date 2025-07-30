"""赏金猎人模块 - 专门追踪AdventureX厕所事件真凶的赏金猎人系统"""

import random
import time
from datetime import datetime, timedelta

class BountyHunter:
    """赏金猎人 - 为了5000元悬赏而战的勇士"""
    
    def __init__(self, hunter_name="匿名猎人", specialty="厕所犯罪调查"):
        self.name = hunter_name
        self.specialty = specialty
        self.bounty_amount = 5000
        self.investigation_points = 0
        self.leads_found = []
        self.equipment = []
        self.reputation = 0
        self.cases_solved = 0
        
    def register_as_hunter(self):
        """注册成为赏金猎人"""
        hunter_types = [
            "厕所法医专家",
            "气味追踪专家", 
            "监控录像分析师",
            "心理侧写师",
            "数字取证专家",
            "现场重建专家",
            "证人访谈专家"
        ]
        
        if self.specialty == "厕所犯罪调查":
            self.specialty = random.choice(hunter_types)
            
        print(f"🎯 {self.name}已注册为{self.specialty}")
        print(f"💰 目标悬赏：{self.bounty_amount}元")
        print(f"🏆 当前声望：{self.reputation}")
        
        return f"猎人{self.name}注册成功"
    
    def acquire_equipment(self):
        """获取调查装备"""
        available_equipment = [
            "专业气味检测仪",
            "高清夜视摄像头",
            "DNA采样工具包",
            "指纹提取套装",
            "心理分析软件",
            "监控破解工具",
            "证人测谎仪",
            "厕所隐蔽摄像头",
            "气味分子分析仪",
            "脚印石膏模具"
        ]
        
        new_equipment = random.sample(available_equipment, random.randint(2, 4))
        self.equipment.extend(new_equipment)
        
        print(f"🔧 {self.name}获得新装备：")
        for item in new_equipment:
            print(f"   - {item}")
            
        return new_equipment
    
    def investigate_scene(self):
        """调查犯罪现场"""
        investigation_results = [
            "发现可疑的脚印痕迹",
            "检测到异常的化学成分",
            "找到遗留的程序员专用纸巾",
            "监控录像显示可疑身影",
            "气味分析指向特定食物来源",
            "发现键盘使用痕迹",
            "检测到咖啡因残留",
            "找到代码调试相关的纸条"
        ]
        
        findings = random.sample(investigation_results, random.randint(1, 3))
        self.leads_found.extend(findings)
        self.investigation_points += len(findings) * 10
        
        print(f"🔍 {self.name}现场调查结果：")
        for finding in findings:
            print(f"   ✅ {finding}")
            
        print(f"📈 调查积分：+{len(findings) * 10} (总计: {self.investigation_points})")
        
        return findings
    
    def analyze_suspects(self):
        """分析嫌疑人"""
        suspect_profiles = [
            {
                "姓名": "张全栈",
                "职业": "全栈工程师", 
                "嫌疑度": random.randint(60, 90),
                "特征": "连续编程72小时，只靠外卖和咖啡维生",
                "动机": "压力过大，急需释放"
            },
            {
                "姓名": "李前端",
                "职业": "前端开发",
                "嫌疑度": random.randint(50, 85),
                "特征": "完美主义者，无法容忍任何bug",
                "动机": "代码出现致命错误，情绪失控"
            },
            {
                "姓名": "王后端",
                "职业": "后端工程师",
                "嫌疑度": random.randint(70, 95),
                "特征": "喜欢在厕所里思考架构问题",
                "动机": "灵感突然来临，忘记了基本礼仪"
            },
            {
                "姓名": "赵数据",
                "职业": "数据科学家",
                "嫌疑度": random.randint(40, 80),
                "特征": "习惯用数据分析一切，包括生理需求",
                "动机": "正在进行肠道微生物实验"
            }
        ]
        
        analyzed_suspects = random.sample(suspect_profiles, random.randint(2, 4))
        
        print(f"👤 {self.name}嫌疑人分析报告：")
        for suspect in analyzed_suspects:
            print(f"   🎯 {suspect['姓名']} ({suspect['职业']})")
            print(f"      嫌疑度: {suspect['嫌疑度']}%")
            print(f"      特征: {suspect['特征']}")
            print(f"      动机: {suspect['动机']}")
            print()
            
        self.investigation_points += len(analyzed_suspects) * 15
        return analyzed_suspects
    
    def set_trap(self):
        """设置陷阱抓捕真凶"""
        trap_types = [
            "在厕所安装隐蔽摄像头",
            "使用气味诱饵引诱真凶",
            "伪装成清洁工进行监控",
            "在厕所门口设置指纹采集器",
            "使用心理战术诱导自首",
            "分析代码提交时间设置埋伏",
            "在咖啡机附近监控可疑人员"
        ]
        
        chosen_trap = random.choice(trap_types)
        success_rate = random.randint(20, 80)
        
        print(f"🪤 {self.name}设置陷阱：{chosen_trap}")
        print(f"📊 预计成功率：{success_rate}%")
        
        if success_rate > 60:
            print("✅ 陷阱设置成功，等待真凶上钩...")
            self.investigation_points += 25
        else:
            print("❌ 陷阱被发现，真凶更加警觉了")
            self.investigation_points += 5
            
        return {"trap": chosen_trap, "success_rate": success_rate}
    
    def submit_bounty_claim(self):
        """提交悬赏申请"""
        if self.investigation_points < 50:
            return "调查积分不足，无法提交悬赏申请"
            
        evidence_strength = min(100, self.investigation_points)
        claim_success_rate = evidence_strength * 0.8
        
        claim_result = {
            "申请人": self.name,
            "专业领域": self.specialty,
            "调查积分": self.investigation_points,
            "证据强度": f"{evidence_strength}%",
            "成功率": f"{claim_success_rate:.1f}%",
            "线索数量": len(self.leads_found),
            "装备价值": len(self.equipment) * 500
        }
        
        if claim_success_rate > 70:
            claim_result["状态"] = "申请通过，等待最终确认"
            claim_result["预计奖金"] = f"{self.bounty_amount}元"
            self.reputation += 50
        elif claim_success_rate > 40:
            claim_result["状态"] = "申请待审核，需要更多证据"
            claim_result["预计奖金"] = f"{self.bounty_amount // 2}元"
            self.reputation += 20
        else:
            claim_result["状态"] = "申请被拒绝，证据不足"
            claim_result["预计奖金"] = "0元"
            self.reputation += 5
            
        return claim_result
    
    def compete_with_other_hunters(self, other_hunters_count=10):
        """与其他赏金猎人竞争"""
        competition_events = [
            "抢夺关键证据",
            "争夺最佳调查位置",
            "竞争证人访谈权",
            "监控录像分析竞赛",
            "嫌疑人追踪大赛",
            "装备升级竞拍"
        ]
        
        my_score = self.investigation_points + self.reputation
        competitor_scores = [random.randint(50, 200) for _ in range(other_hunters_count)]
        
        my_rank = sum(1 for score in competitor_scores if score > my_score) + 1
        
        competition_result = {
            "参赛猎人数量": other_hunters_count + 1,
            "我的排名": f"{my_rank}/{other_hunters_count + 1}",
            "我的得分": my_score,
            "竞争激烈程度": "极高" if other_hunters_count > 20 else "高" if other_hunters_count > 10 else "中等",
            "获胜概率": f"{max(0, 100 - my_rank * 10)}%"
        }
        
        if my_rank <= 3:
            competition_result["奖励"] = "获得额外调查资源"
            self.investigation_points += 20
        
        return competition_result
    
    def generate_hunter_report(self):
        """生成猎人报告"""
        report = {
            "猎人姓名": self.name,
            "专业领域": self.specialty,
            "注册时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "调查积分": self.investigation_points,
            "声望等级": self.reputation,
            "发现线索": len(self.leads_found),
            "装备数量": len(self.equipment),
            "成功案例": self.cases_solved,
            "专业评级": self._calculate_professional_rating(),
            "下一步行动": self._suggest_next_action()
        }
        
        return report
    
    def _calculate_professional_rating(self):
        """计算专业评级"""
        total_score = self.investigation_points + self.reputation + len(self.leads_found) * 5
        
        if total_score >= 200:
            return "传奇猎人 🏆"
        elif total_score >= 150:
            return "专家级猎人 🥇"
        elif total_score >= 100:
            return "高级猎人 🥈"
        elif total_score >= 50:
            return "中级猎人 🥉"
        else:
            return "新手猎人 🔰"
    
    def _suggest_next_action(self):
        """建议下一步行动"""
        if self.investigation_points < 30:
            return "建议继续收集证据和线索"
        elif len(self.equipment) < 3:
            return "建议升级调查装备"
        elif len(self.leads_found) < 5:
            return "建议深入分析现有线索"
        else:
            return "建议提交悬赏申请或设置陷阱"
    
    def start_hunting_mission(self):
        """开始完整的猎人任务"""
        print(f"🎯 {self.name}开始AdventureX厕所事件赏金猎人任务！\n")
        
        # 注册
        self.register_as_hunter()
        print()
        
        # 获取装备
        self.acquire_equipment()
        print()
        
        # 调查现场
        self.investigate_scene()
        print()
        
        # 分析嫌疑人
        self.analyze_suspects()
        print()
        
        # 设置陷阱
        self.set_trap()
        print()
        
        # 与其他猎人竞争
        competition = self.compete_with_other_hunters()
        print("🏁 竞争结果：")
        for key, value in competition.items():
            print(f"   {key}: {value}")
        print()
        
        # 提交悬赏申请
        claim = self.submit_bounty_claim()
        print("📋 悬赏申请结果：")
        for key, value in claim.items():
            print(f"   {key}: {value}")
        print()
        
        # 生成最终报告
        final_report = self.generate_hunter_report()
        print("📊 最终猎人报告：")
        for key, value in final_report.items():
            print(f"   {key}: {value}")
            
        return final_report