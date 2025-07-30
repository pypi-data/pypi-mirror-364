# AdventureX Shit 💩

一个幽默的Python模块，用于纪念AdventureX 2025黑客松史上最传奇的厕所事件。

## 事件背景 📰

在AdventureX 2025黑客松现场，发生了一起震惊整个技术圈的厕所事件：
- 🚽 某位神秘程序员在厕所"释放"了超越人类极限的"作品"
- 🤰 一名孕妇参赛者不幸中招，当场呕吐不止
- 😱 现场一片混乱，活动几乎中断
- 💰 主办方紧急悬赏5000元寻找"真凶"
- 🕵️ 无数赏金猎人开始了史上最离奇的调查

## 安装 📦

```bash
pip install adventurex-shit
```

## 快速开始 🚀

```python
import adventurex_shit as axs

# 获取事件摘要
summary = axs.get_incident_summary()
print(summary)

# 计算获得悬赏的概率
odds = axs.calculate_bounty_odds(participants_count=200)
print(f"获得悬赏的概率: {odds['odds_percentage']}%")

# 模拟混乱程度
chaos = axs.simulate_chaos_level(pregnant_women_count=1, toilet_count=1)
print(f"混乱等级: {chaos['chaos_level']}/100")
```

## 主要功能 ✨

### 🕵️ 厕所侦探 (ToiletDetective)

专业调查厕所犯罪现场的侦探工具：

```python
from adventurex_shit import ToiletDetective

# 创建侦探
detective = ToiletDetective("福尔摩斯·厕所")

# 开始调查
detective.start_investigation()

# 收集证据
evidence = detective.collect_evidence()

# 访谈证人
testimony = detective.interview_witness("匿名孕妇")

# 分析嫌疑人
suspects = detective.analyze_suspects()

# 生成调查报告
report = detective.generate_investigation_report()

# 预测真凶
prediction = detective.predict_perpetrator()
```

### 🌪️ 混乱模拟器 (ChaosSimulator)

重现和预测厕所事件的混乱程度：

```python
from adventurex_shit import ChaosSimulator

# 创建混乱模拟器
simulator = ChaosSimulator()

# 运行完整模拟
chaos_result = simulator.run_full_simulation()

# 预测未来混乱趋势
future_chaos = simulator.predict_future_chaos(days_ahead=7)

# 模拟社交媒体爆炸
viral_posts = simulator.simulate_social_media_explosion()
```

### 🎯 赏金猎人 (BountyHunter)

为了5000元悬赏而战的勇士系统：

```python
from adventurex_shit import BountyHunter

# 创建赏金猎人
hunter = BountyHunter("赏金猎人小王", "厕所法医专家")

# 开始完整的猎人任务
final_report = hunter.start_hunting_mission()

# 或者分步执行
hunter.register_as_hunter()
hunter.acquire_equipment()
hunter.investigate_scene()
hunter.set_trap()
claim_result = hunter.submit_bounty_claim()
```

### 📰 事件报告员 (IncidentReporter)

生成各种官方和非官方报告：

```python
from adventurex_shit import IncidentReporter

# 创建报告员
reporter = IncidentReporter("张记者", "科技日报")

# 生成官方声明
official_statement = reporter.generate_official_statement()

# 生成不同风格的新闻报道
formal_news = reporter.generate_news_report("正式新闻")
gossip_news = reporter.generate_news_report("娱乐八卦")
tech_blog = reporter.generate_news_report("技术博客")

# 生成调查报告
investigation = reporter.generate_investigation_report()

# 生成事件时间线
timeline = reporter.generate_timeline_report()

# 导出所有报告
all_reports = reporter.export_all_reports(format="json")
```

## 使用场景 🎭

### 1. 团队建设活动
```python
# 在团队聚会上使用，增加欢乐气氛
detective = ToiletDetective("团队侦探")
detective.start_investigation()
```

### 2. 黑客松娱乐
```python
# 在真实黑客松中使用，缓解紧张气氛
simulator = ChaosSimulator()
chaos = simulator.run_full_simulation()
```

### 3. 编程教学
```python
# 用有趣的例子教授Python编程
hunter = BountyHunter("学生猎人")
report = hunter.generate_hunter_report()
```

### 4. 压力测试
```python
# 测试你的应用在"混乱"情况下的表现
for i in range(100):
    chaos_level = simulate_chaos_level()
    if chaos_level['chaos_level'] > 90:
        print("系统即将崩溃！")
```

## API 参考 📚

### 全局函数

- `get_incident_summary()` - 获取事件摘要
- `calculate_bounty_odds(participants_count)` - 计算悬赏概率
- `simulate_chaos_level(pregnant_women_count, toilet_count, ventilation_quality)` - 模拟混乱程度

### 类方法

详细的API文档请参考各个模块的docstring。

## 贡献指南 🤝

我们欢迎所有形式的贡献！无论是：
- 🐛 报告bug
- 💡 提出新功能
- 📝 改进文档
- 🎨 优化代码
- 😂 增加更多幽默元素

### 开发环境设置

```bash
git clone https://github.com/adventurex/shit-incident.git
cd shit-incident
pip install -e .
```

### 运行测试

```bash
python -m pytest tests/
```

## 免责声明 ⚠️

本项目纯属娱乐和教育目的，不鼓励任何不当的厕所使用行为。请在使用公共设施时保持基本的文明和礼貌。

## 许可证 📄

MIT License - 详见 [LICENSE](LICENSE) 文件

## 致谢 🙏

- 感谢AdventureX 2025黑客松为我们提供了如此"丰富"的素材
- 感谢那位匿名的"真凶"，没有你就没有这个项目
- 感谢受影响的孕妇参赛者，希望你已经完全康复
- 感谢所有的赏金猎人，让这个事件变得更加有趣

## 联系我们 📧

- 项目主页: https://github.com/adventurex/shit-incident
- 问题反馈: https://github.com/adventurex/shit-incident/issues
- 悬赏线索: security@adventurex.com
- 紧急联系: 400-ADVENTURE

---

**记住：编程改变世界，但请不要在厕所里改变世界！** 💻🚽

*"在代码的世界里，我们追求完美；在现实的世界里，我们追求文明。"* - AdventureX格言