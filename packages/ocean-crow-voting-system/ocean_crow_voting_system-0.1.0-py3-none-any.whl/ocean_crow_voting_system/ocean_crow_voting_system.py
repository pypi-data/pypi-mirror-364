# OceanCrow Voting System by Sheldon Kenny Salmon
# Purpose: In-game community feature voting system
# Version: 0.1.0
# License: MIT (see LICENSE in package)
# Note: Adaptable for gaming, finance, etc.; test in non-critical systems.

import pygame
import json
import time
import random
from typing import Dict, List
import os
import fcntl # For file locking on Unix-like systems

# The Aquifer (Core Foundations)
voting_file = "voting_data.json"
player_id = "player_001" # Placeholder; could be dynamic
MAX_IDEA_LENGTH = 200
ideas_list: List[Dict] = []

# The Water Works
def stream_cleanser(data_list: List) -> List:
    """Validate and purify idea data."""
    return [x.strip()[:MAX_IDEA_LENGTH] for x in data_list 
            if isinstance(x, str) and x.strip() and x is not None and "<script" not in x.lower()]

def aqua_forge(idea_text: str) -> Dict:
    """Transform raw idea into structured data."""
    return {
        "id": f"{player_id}_{int(time.time())}",
        "text": idea_text,
        "votes": 0,
        "timestamp": time.time()
    }

def aqua_mind(idea: Dict, context: Dict) -> Dict:
    """Prioritize popular ideas."""
    threshold = context.get("vote_threshold", 5)
    idea["priority"] = "high" if idea["votes"] >= threshold else "low"
    return idea

def tactic_weave(context: Dict) -> str:
    """Blend voting strategies."""
    strategies = {"default": ["count", "display"], "advanced": ["weight", "trend"]}
    return random.choice(strategies["default"]) + "_" + random.choice(strategies["advanced"])

def team_tide(player_count: int) -> Dict:
    """Adjust dynamics based on player count."""
    return {"update_interval": 5 if player_count < 10 else 2, "max_ideas": 10 if player_count < 10 else 20}

# The Current (Modular Code)
def save_ideas(ideas: List[Dict]):
    """Module 1: Save voting data with locking."""
    try:
        with open(voting_file, "r") as f:
            fcntl.flock(f, fcntl.LOCK_SH) # Read lock
            ideas_list = json.load(f) if os.path.getsize(voting_file) else []
    except (FileNotFoundError, json.JSONDecodeError):
        ideas_list = []
    finally:
        fcntl.flock(f, fcntl.LOCK_UN)

    ideas_list = ideas
    with open(voting_file, "w") as f:
        fcntl.flock(f, fcntl.LOCK_EX) # Write lock
        json.dump(ideas_list, f, indent=2)
    fcntl.flock(f, fcntl.LOCK_UN)

def process_vote(idea_id: str, vote: int):
    """Module 2: Process and tally votes."""
    with open(voting_file, "r") as f:
        fcntl.flock(f, fcntl.LOCK_SH)
        ideas_list = json.load(f) if os.path.getsize(voting_file) else []
    for idea in ideas_list:
        if idea["id"] == idea_id:
            idea["votes"] += vote
            idea = aqua_mind(idea, {"vote_threshold": 5})
            save_ideas(ideas_list)
            return idea
    return None

def display_ui(screen, clock):
    """Module 3: Interaction layer with Pygame UI."""
    font = pygame.font.Font(None, 36)
    input_active = False
    idea_text = ""
    ideas_list = []
    last_update = 0
    last_submit = 0
    vote_limit = {player_id: 0} # Simple vote tracking per session

    try:
        with open(voting_file, "r") as f:
            fcntl.flock(f, fcntl.LOCK_SH)
            ideas_list = json.load(f) if os.path.getsize(voting_file) else []
    except (FileNotFoundError, json.JSONDecodeError):
        ideas_list = []
    finally:
        fcntl.flock(f, fcntl.LOCK_UN)

    timeout = time.time() + 60 # 60-second timeout
    while time.time() < timeout:
        current_time = time.time()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                input_active = True
            if event.type == pygame.KEYDOWN and input_active:
                if event.key == pygame.K_RETURN and current_time - last_submit > 5: # 5s cooldown
                    if idea_text:
                        new_idea = aqua_forge(idea_text)
                        ideas_list.append(new_idea)
                        save_ideas(ideas_list)
                        idea_text = ""
                        input_active = False
                        last_submit = current_time
                elif event.key == pygame.K_BACKSPACE:
                    idea_text = idea_text[:-1]
                elif event.key == pygame.K_UP and vote_limit[player_id] < 1: # 1 vote limit
                    if ideas_list:
                        process_vote(ideas_list[0]["id"], 1)
                        vote_limit[player_id] += 1
                else:
                    idea_text += event.unicode

        if current_time - last_update > team_tide(1)["update_interval"]:
            last_update = current_time
            ideas_list.sort(key=lambda x: x["votes"], reverse=True)
            ideas_list = wave_morph_advanced(ideas_list, threshold=5, max_size=team_tide(1)["max_ideas"])

        screen.fill((0, 0, 0))
        text_surface = font.render(f"Idea: {idea_text} (Enter to submit, Up to vote)", True, (255, 255, 255))
        screen.blit(text_surface, (50, 50))
        y_offset = 100
        for idea in ideas_list[:5]: # Show top 5
            text = font.render(f"{idea['text']} (Votes: {idea['votes']})", True, (255, 255, 0))
            screen.blit(text, (50, y_offset))
            y_offset += 40
        pygame.display.flip()
        clock.tick(30)

# The Ocean Depths (Advanced Innovation)
def water_cool(func):
    """Optimize performance with timing."""
    import time
    def wrapper(*args):
        start = time.time()
        result = func(*args)
        print(f"Cooled in {time.time() - start}s")
        return result
    return wrapper

@water_cool
def wave_morph_advanced(data: List, threshold=5, max_size=20) -> List:
    """Filter low-vote ideas with size limit."""
    if len(data) > threshold:
        return sorted(data, key=lambda x: x["votes"], reverse=True)[:max_size]
    return data

# The Tide (Scalability & Standards)
@water_cool
def run_voting_system(player_count=1):
    """Main entry point with scalability."""
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("OceanCrow Voting System")
    clock = pygame.time.Clock()
    display_ui(screen, clock)
    pygame.quit()

if __name__ == "__main__":
    run_voting_system()