"""AdventureX Shit - A humorous commemoration of the legendary bathroom incident

This package provides utilities to commemorate the infamous AdventureX 2025 hackathon
bathroom incident that caused chaos and a 5000 yuan bounty hunt.
"""

__version__ = "1.0.0"
__author__ = "Anonymous Hackathon Participant"
__email__ = "mystery@adventurex.com"

from .toilet_detective import ToiletDetective
from .chaos_simulator import ChaosSimulator
from .bounty_hunter import BountyHunter
from .incident_reporter import IncidentReporter

__all__ = [
    "ToiletDetective",
    "ChaosSimulator", 
    "BountyHunter",
    "IncidentReporter",
    "get_incident_summary",
    "calculate_bounty_odds",
    "simulate_chaos_level"
]

def get_incident_summary():
    """获取AdventureX 2025厕所事件的官方摘要"""
    return {
        "event": "AdventureX 2025 Hackathon Bathroom Incident",
        "location": "Hackathon Venue Toilet",
        "incident": "Someone defecated in the toilet causing pregnant woman to vomit",
        "chaos_level": "Maximum",
        "bounty": "5000 CNY",
        "status": "Perpetrator still at large",
        "witnesses": "Traumatized pregnant woman and horrified attendees",
        "investigation": "Ongoing"
    }

def calculate_bounty_odds(participants_count=200):
    """计算获得悬赏的概率"""
    return {
        "total_bounty": 5000,
        "participants": participants_count,
        "odds_of_being_caught": f"1/{participants_count}",
        "odds_percentage": round(100/participants_count, 2),
        "risk_level": "High" if participants_count < 50 else "Medium" if participants_count < 150 else "Low"
    }

def simulate_chaos_level(pregnant_women_count=1, toilet_count=1, ventilation_quality="poor"):
    """模拟混乱程度"""
    base_chaos = 50
    chaos_multiplier = pregnant_women_count * 30
    toilet_factor = max(1, 10 - toilet_count)
    ventilation_factor = {"excellent": 0.5, "good": 0.7, "poor": 1.5, "terrible": 2.0}.get(ventilation_quality, 1.0)
    
    total_chaos = (base_chaos + chaos_multiplier + toilet_factor) * ventilation_factor
    
    return {
        "chaos_level": min(100, int(total_chaos)),
        "description": "MAXIMUM CHAOS ACHIEVED" if total_chaos >= 100 else 
                      "High chaos" if total_chaos >= 70 else
                      "Moderate chaos" if total_chaos >= 40 else
                      "Mild disturbance",
        "evacuation_recommended": total_chaos >= 80
    }