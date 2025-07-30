#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AdventureX Shit 示例脚本

这个脚本演示了如何使用 adventurex-shit 包的各种功能
来重现和调侃 AdventureX 2025 黑客松的传奇厕所事件。
"""

import time
from adventurex_shit import (
    ToiletDetective, 
    ChaosSimulator, 
    BountyHunter, 
    IncidentReporter,
    get_incident_summary,
    calculate_bounty_odds,
    simulate_chaos_level
)

def print_separator(title):
    """打印分隔符"""
    print("\n" + "="*60)
    print(f"🎭 {title}")
    print("="*60)

def demo_basic_functions():
    """演示基础功能"""
    print_separator("基础功能演示")
    
    # 获取事件摘要
    print("📰 AdventureX 厕所事件摘要:")
    summary = get_incident_summary()
    for key, value in summary.items():
        print(f"   {key}: {value}")
    
    print("\n💰 悬赏概率计算:")
    odds = calculate_bounty_odds(200)
    for key, value in odds.items():
        print(f"   {key}: {value}")
    
    print("\n🌪️ 混乱程度模拟:")
    chaos = simulate_chaos_level(1, 1, "poor")
    for key, value in chaos.items():
        print(f"   {key}: {value}")

def demo_toilet_detective():
    """演示厕所侦探功能"""
    print_separator("厕所侦探调查")
    
    detective = ToiletDetective("福尔摩斯·厕所")
    
    # 开始调查
    detective.start_investigation()
    print()
    
    # 收集证据
    print("🔍 收集证据中...")
    for i in range(3):
        detective.collect_evidence()
        time.sleep(0.5)
    print()
    
    # 访谈证人
    print("👥 证人访谈:")
    detective.interview_witness("匿名孕妇")
    detective.interview_witness("现场清洁工")
    print()
    
    # 分析嫌疑人
    print("🎯 嫌疑人分析:")
    detective.analyze_suspects()
    print()
    
    # 预测真凶
    print("🔮 真凶预测:")
    prediction = detective.predict_perpetrator()
    for key, value in prediction.items():
        print(f"   {key}: {value}")
    print()
    
    # 生成调查报告
    print("📋 调查报告:")
    report = detective.generate_investigation_report()
    for key, value in report.items():
        print(f"   {key}: {value}")

def demo_chaos_simulator():
    """演示混乱模拟器"""
    print_separator("混乱模拟器演示")
    
    simulator = ChaosSimulator()
    
    print("🎬 开始完整混乱模拟...\n")
    chaos_result = simulator.run_full_simulation()
    
    print("\n🔮 未来7天混乱趋势预测:")
    future_predictions = simulator.predict_future_chaos(7)
    for day_prediction in future_predictions:
        for key, value in day_prediction.items():
            print(f"   {key}: {value}")

def demo_bounty_hunter():
    """演示赏金猎人功能"""
    print_separator("赏金猎人任务")
    
    hunter = BountyHunter("赏金猎人小王", "厕所法医专家")
    
    print("🎯 开始赏金猎人完整任务...\n")
    final_report = hunter.start_hunting_mission()
    
    return final_report

def demo_incident_reporter():
    """演示事件报告员功能"""
    print_separator("事件报告生成")
    
    reporter = IncidentReporter("张记者", "科技日报")
    
    # 生成官方声明
    print("📢 官方声明:")
    official = reporter.generate_official_statement()
    print(f"标题: {official['标题']}")
    print(f"发布机构: {official['发布机构']}")
    print(f"悬赏金额: {official['悬赏信息']['金额']}")
    print()
    
    # 生成娱乐八卦报道
    print("🎪 娱乐八卦报道:")
    gossip = reporter.generate_news_report("娱乐八卦")
    print(f"标题: {gossip['标题']}")
    print(f"八卦指数: {gossip['八卦指数']}")
    print("网友评论:")
    for comment in gossip['网友评论'][:2]:
        print(f"   - {comment}")
    print()
    
    # 生成技术博客
    print("💻 技术博客:")
    tech_blog = reporter.generate_news_report("技术博客")
    print(f"标题: {tech_blog['标题']}")
    print(f"标签: {', '.join(tech_blog['标签'])}")
    print()
    
    # 生成调查报告
    print("🔍 调查报告:")
    investigation = reporter.generate_investigation_report()
    print(f"案件编号: {investigation['案件编号']}")
    print(f"悬赏金额: {investigation['悬赏信息']['金额']}")
    print(f"调查结论: {investigation['调查结论']}")
    print()
    
    # 生成时间线
    print("⏰ 事件时间线:")
    timeline = reporter.generate_timeline_report()
    print(f"时间线事件数: {len(timeline['时间线'])}")
    print("关键时间点:")
    for event in timeline['时间线'][:3]:
        print(f"   {event['时间']}: {event['事件']}")
    print("   ...")
    
    # 获取统计信息
    print("\n📊 报告统计:")
    stats = reporter.get_report_statistics()
    for key, value in stats.items():
        print(f"   {key}: {value}")

def interactive_demo():
    """交互式演示"""
    print_separator("交互式体验")
    
    print("🎮 欢迎来到 AdventureX 厕所事件互动体验！")
    print("\n请选择你想体验的角色:")
    print("1. 🕵️ 厕所侦探 - 调查真相")
    print("2. 🎯 赏金猎人 - 追捕真凶")
    print("3. 📰 事件记者 - 报道新闻")
    print("4. 🌪️ 混乱观察者 - 模拟现场")
    print("5. 🎲 随机体验 - 让命运决定")
    
    try:
        choice = input("\n请输入选择 (1-5): ").strip()
        
        if choice == "1":
            detective = ToiletDetective(input("请输入你的侦探名字: "))
            detective.start_investigation()
            detective.collect_evidence()
            detective.analyze_suspects()
            
        elif choice == "2":
            hunter_name = input("请输入你的猎人名字: ")
            hunter = BountyHunter(hunter_name)
            hunter.register_as_hunter()
            hunter.investigate_scene()
            
        elif choice == "3":
            reporter_name = input("请输入你的记者名字: ")
            reporter = IncidentReporter(reporter_name)
            reporter.generate_official_statement()
            
        elif choice == "4":
            simulator = ChaosSimulator()
            simulator.trigger_initial_incident()
            simulator.simulate_crowd_reaction()
            
        elif choice == "5":
            import random
            random_choice = random.choice(["1", "2", "3", "4"])
            print(f"🎲 命运选择了: {random_choice}")
            # 递归调用，但用选定的选择
            globals()[f"demo_{'toilet_detective' if random_choice == '1' else 'bounty_hunter' if random_choice == '2' else 'incident_reporter' if random_choice == '3' else 'chaos_simulator'}"]() 
            
        else:
            print("❌ 无效选择，请重新运行程序")
            
    except KeyboardInterrupt:
        print("\n\n👋 感谢体验 AdventureX 厕所事件模拟器！")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")

def main():
    """主函数"""
    print("🎭" + "="*58 + "🎭")
    print("🚽" + " "*20 + "AdventureX Shit Demo" + " "*20 + "🚽")
    print("💩" + " "*15 + "传奇厕所事件完整体验" + " "*15 + "💩")
    print("🎭" + "="*58 + "🎭")
    
    try:
        # 基础功能演示
        demo_basic_functions()
        time.sleep(2)
        
        # 厕所侦探演示
        demo_toilet_detective()
        time.sleep(2)
        
        # 混乱模拟器演示
        demo_chaos_simulator()
        time.sleep(2)
        
        # 赏金猎人演示
        demo_bounty_hunter()
        time.sleep(2)
        
        # 事件报告员演示
        demo_incident_reporter()
        time.sleep(2)
        
        # 交互式演示
        interactive_demo()
        
    except KeyboardInterrupt:
        print("\n\n👋 演示被用户中断")
    except Exception as e:
        print(f"\n❌ 演示过程中发生错误: {e}")
    finally:
        print_separator("演示结束")
        print("🎉 感谢使用 AdventureX Shit 包！")
        print("💡 记住：编程改变世界，但请不要在厕所里改变世界！")
        print("🔗 项目地址: https://github.com/adventurex/shit-incident")
        print("💰 悬赏线索: security@adventurex.com")

if __name__ == "__main__":
    main()