import random
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np
import argparse
import os
from pathlib import Path


def run_simulation(output_dir="."):
    """Run the simulation and save outputs to the specified directory."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Set up the gifts with values (higher = more desirable)
    # Note: A gift cannot be immediately stolen back in the same steal chain
    gifts = [
        {"id": 1, "name": "Bluetooth Speaker", "value": 85, "steals": 0, "locked": False},
        {"id": 2, "name": "Luxury Candle Set", "value": 60, "steals": 0, "locked": False},
        {"id": 3, "name": "Board Game Collection", "value": 75, "steals": 0, "locked": False},
        {"id": 4, "name": "Electric Wine Opener", "value": 50, "steals": 0, "locked": False},
        {"id": 5, "name": "Cozy Throw Blanket", "value": 70, "steals": 0, "locked": False},
        {"id": 6, "name": "Gourmet Coffee Set", "value": 55, "steals": 0, "locked": False},
        {"id": 7, "name": "Portable Phone Charger", "value": 90, "steals": 0, "locked": False},
        {"id": 8, "name": "Kitchen Gadget Bundle", "value": 65, "steals": 0, "locked": False},
    ]

    # Players
    players = [f"Player {i+1}" for i in range(8)]
    player_gifts = {player: None for player in players}

    # Game log
    game_log = []
    turn_snapshots = []
    action_snapshots = []  # New: track state after each individual action

    def capture_game_state(action_description):
        """Capture the current state of all gifts and players"""
        state = {
            "action": action_description,
            "gifts": [],
            "players": {}
        }
        
        for gift in gifts:
            owner = None
            for p, g in player_gifts.items():
                if g == gift:
                    owner = p
                    break
            
            state["gifts"].append({
                "id": gift["id"],
                "name": gift["name"],
                "value": gift["value"],
                "owner": owner,
                "steals": gift["steals"],
                "locked": gift["locked"],
                "opened": owner is not None or gift["steals"] > 0
            })
        
        for player in players:
            gift = player_gifts[player]
            state["players"][player] = {
                "gift_name": gift["name"] if gift else None,
                "gift_id": gift["id"] if gift else None
            }
        
        return state

    def get_gift_by_id(gift_id):
        return next(g for g in gifts if g["id"] == gift_id)

    def steal_decision(current_player, available_gifts, opened_gifts, just_stolen_gift=None):
        """Decide whether to steal or pick new gift"""
        if not opened_gifts:
            return None  # Must pick new gift
        
        # Find stealable gifts (not locked, not the one they just had stolen, and not the gift just stolen from them)
        stealable = [g for g in opened_gifts if not g["locked"] and g != just_stolen_gift]
        
        if not stealable or not available_gifts:
            if not stealable:
                return None  # No stealable gifts, must pick new
            # No wrapped gifts left, must steal
            return max(stealable, key=lambda g: g["value"])
        
        # Strategy: 70% chance to steal if there's a significantly better gift available
        best_available = max(stealable, key=lambda g: g["value"])
        
        # Weighted decision based on gift value
        if best_available["value"] >= 75:  # High value gift
            steal_chance = 0.8
        elif best_available["value"] >= 65:  # Medium-high value
            steal_chance = 0.6
        else:  # Lower value
            steal_chance = 0.3
        
        if random.random() < steal_chance:
            return best_available
        return None

    def execute_turn(player_num, available_gift_ids, opened_gifts):
        """Execute a single player's turn, handling steal chains.
        CRITICAL: The turn-taker must END with a gift. If their gift is stolen during the chain,
        they must continue until they have a gift again."""
        current_player = players[player_num]
        turn_log = []
        turn_log.append(f"\n=== {current_player}'s Turn ===")
        
        # Capture initial state
        action_snapshots.append(capture_game_state(f"Start of {current_player}'s turn"))
        
        active_player = current_player
        chain_active = True
        just_stolen_gift = None  # Track the gift that was just stolen to prevent immediate steal-back
        
        while chain_active:
            # Decide: steal or pick new?
            steal_target = steal_decision(active_player, available_gift_ids, opened_gifts, just_stolen_gift)
            
            if steal_target is None:
                # Pick a new wrapped gift
                if available_gift_ids:
                    new_gift_id = random.choice(available_gift_ids)
                    new_gift = get_gift_by_id(new_gift_id)
                    available_gift_ids.remove(new_gift_id)
                    opened_gifts.append(new_gift)
                    player_gifts[active_player] = new_gift
                    action_desc = f"{active_player} unwraps Gift #{new_gift_id}: {new_gift['name']}"
                    turn_log.append(f"  {action_desc}")
                    action_snapshots.append(capture_game_state(action_desc))
                    chain_active = False  # Chain ends when someone picks wrapped gift
                    just_stolen_gift = None  # Reset for next turn
                else:
                    # No wrapped gifts left, must steal
                    stealable = [g for g in opened_gifts if not g["locked"] and player_gifts.get(active_player) != g and g != just_stolen_gift]
                    if stealable:
                        steal_target = max(stealable, key=lambda g: g["value"])
                    else:
                        turn_log.append(f"  {active_player} has no valid moves, keeps current gift")
                        chain_active = False
            
            if steal_target:
                # Execute steal
                victim = None
                for p, g in player_gifts.items():
                    if g == steal_target:
                        victim = p
                        break
                
                if victim:
                    # Update steals count and check for lock
                    steal_target["steals"] += 1
                    if steal_target["steals"] >= 3:
                        steal_target["locked"] = True
                    
                    # Transfer the gift
                    player_gifts[active_player] = steal_target
                    player_gifts[victim] = None
                    
                    action_desc = f"{active_player} steals Gift #{steal_target['id']}: {steal_target['name']} from {victim}"
                    turn_log.append(f"  {action_desc}")
                    action_snapshots.append(capture_game_state(action_desc))
                    
                    just_stolen_gift = steal_target  # Track this to prevent immediate steal-back
                    
                    if steal_target["locked"]:
                        turn_log.append(f"    Gift #{steal_target['id']} is now LOCKED (3 steals)")
                        chain_active = False  # Chain ends when gift is locked
                    else:
                        # Victim becomes the active player (must steal or pick)
                        active_player = victim
                        # Continue the chain with the victim as active player
                else:
                    turn_log.append(f"  Error: Could not find victim for {steal_target['name']}")
                    chain_active = False
        
        # Record turn summary
        current_gift = player_gifts.get(current_player)
        turn_summary = {
            "player": current_player,
            "actions": turn_log,
            "final_gift": current_gift["name"] if current_gift else "None"
        }
        turn_snapshots.append(turn_summary)
        game_log.extend(turn_log)
        
        return turn_log

    # Initialize gifts
    available_gift_ids = list(range(1, 9))  # Gift IDs 1-8
    opened_gifts = []

    # Execute turns
    for i in range(8):  # 8 players
        turn_result = execute_turn(i, available_gift_ids, opened_gifts)
        for line in turn_result:
            print(line)

    # Final state capture
    action_snapshots.append(capture_game_state("Final game state"))

    # Create a snapshot after each player's complete turn
    for i, player in enumerate(players):
        gift = player_gifts[player]
        locked_gifts = [g["name"] for g in gifts if g["locked"]]
        opened_gift_names = [g["name"] for g in opened_gifts]
        
        snapshot = {
            "player": player,
            "turn_number": i + 1,
            "current_gift": gift["name"] if gift else "None",
            "current_gift_id": gift["id"] if gift else None,
            "current_gift_value": gift["value"] if gift else 0,
            "current_gift_steals": gift["steals"] if gift else 0,
            "player_gifts": {p: (g["name"], g["value"]) if g else (None, 0) for p, g in player_gifts.items()},
            "opened_gifts": opened_gift_names,
            "locked_gifts": locked_gifts
        }
        turn_snapshots.append(snapshot)

    # Validate game state
    print("\n" + "=" * 50)
    print("GAME VALIDATION")
    print("=" * 50)

    players_without_gifts = [p for p, g in player_gifts.items() if g is None]
    unopened_gifts = [g for g in gifts if g["id"] in available_gift_ids]

    if players_without_gifts:
        print(f"ERROR: {len(players_without_gifts)} players have no gifts: {players_without_gifts}")
    else:
        print("✓ All players have gifts")

    if unopened_gifts:
        print(f"ERROR: {len(unopened_gifts)} gifts were never opened: {[g['name'] for g in unopened_gifts]}")
    else:
        print("✓ All gifts were opened")

    # Final results
    print("\n" + "=" * 50)
    print("FINAL RESULTS")
    print("=" * 50)
    for player, gift in player_gifts.items():
        if gift:
            status = "LOCKED" if gift["locked"] else "Available"
            print(f"{player}: {gift['name']} (value: {gift['value']}, stolen: {gift['steals']}x, {status})")

    print("\n" + "=" * 50)
    print("GIFT STATISTICS")
    print("=" * 50)
    for gift in sorted(gifts, key=lambda g: g["steals"], reverse=True):
        owner = "Unopened"
        for p, g in player_gifts.items():
            if g == gift:
                owner = p
                break
        status = "LOCKED" if gift["locked"] else "Available"
        print(f"Gift #{gift['id']}: {gift['name']} (value: {gift['value']}) - Stolen: {gift['steals']}x, {status}, Owner: {owner}")

    print("\nCreating visualizations...")

    # Create visualization
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(20, 16))

    # 1. Gift Values vs Final Steals
    gift_names = [g["name"].replace(" ", "\\n") for g in gifts]
    gift_values = [g["value"] for g in gifts]
    gift_steals = [g["steals"] for g in gifts]

    bars = ax1.bar(gift_names, gift_values, color='lightblue', alpha=0.7, label='Gift Value')
    ax1.set_title('Gift Values vs Steal Frequency', fontsize=16, fontweight='bold')
    ax1.set_ylabel('Gift Value', fontsize=12)
    ax1.tick_params(axis='x', rotation=45, labelsize=8)
    ax1.legend()

    # Add steal count as text on bars
    for i, (bar, steals) in enumerate(zip(bars, gift_steals)):
        height = bar.get_height()
        color = '#e74c3c' if steals >= 3 else '#f39c12' if steals >= 2 else '#27ae60' if steals >= 1 else '#3498db'
        ax1.text(bar.get_x() + bar.get_width()/2., height + 1, f'{steals}×', 
                ha='center', va='bottom', fontweight='bold', color=color, fontsize=10)

    # 2. Final Distribution (Player -> Gift Value)
    player_names = list(player_gifts.keys())
    player_values = [player_gifts[p]["value"] if player_gifts[p] else 0 for p in player_names]
    player_steals = [player_gifts[p]["steals"] if player_gifts[p] else 0 for p in player_names]

    bars2 = ax2.bar(player_names, player_values, color='lightgreen', alpha=0.7)
    ax2.set_title('Final Gift Distribution by Player', fontsize=16, fontweight='bold')
    ax2.set_ylabel('Gift Value', fontsize=12)
    ax2.tick_params(axis='x', rotation=45, labelsize=10)

    # Add gift names and steal counts
    for i, (bar, player) in enumerate(zip(bars2, player_names)):
        gift = player_gifts[player]
        if gift:
            height = bar.get_height()
            width_val = bar.get_width()
            
            # Gift name on bar
            ax2.text(bar.get_x() + bar.get_width()/2., height/2, 
                    gift["name"].replace(" ", "\\n"), ha='center', va='center', 
                    fontsize=7, fontweight='bold', color='white')
            
            # Steal count to the right
            steals = gift["steals"]
            ax2.text(width_val + 1, bar.get_y() + bar.get_height()/2, 
                    f'{steals}×', ha='left', va='center', fontsize=8, color='#c92a2a', fontweight='bold')

    plt.tight_layout()
    plt.savefig(output_path / 'white_elephant_simulation.png', dpi=300, bbox_inches='tight')
    print("\n✓ Visualization saved!")

    # Create round-by-round visualization
    print("Creating round-by-round visualization...")

    # Prepare data for round-by-round
    rounds_data = []
    for i, snapshot in enumerate(turn_snapshots):
        if 'turn_number' in snapshot:
            rounds_data.append({
                'round': snapshot['turn_number'],
                'player': snapshot['player'],
                'gifts_distribution': snapshot['player_gifts'],
                'locked_gifts': snapshot['locked_gifts']
            })

    # Create the round-by-round plot
    fig_rounds, (ax_gifts, ax_players) = plt.subplots(1, 2, figsize=(24, 12))

    # Left plot: Gift journey through rounds
    gift_positions = {}
    colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c', '#34495e', '#e67e22']
    
    for round_data in rounds_data:
        round_num = round_data['round']
        
        y_pos = len(rounds_data) - round_num + 1  # Reverse order (latest at top)
        
        for i, (player, gift_info) in enumerate(round_data['gifts_distribution'].items()):
            gift_name, gift_value = gift_info
            if gift_name:
                # Find gift ID
                gift_id = next((g["id"] for g in gifts if g["name"] == gift_name), None)
                if gift_id:
                    x_pos = i * 2.5
                    
                    # Draw gift box
                    is_locked = gift_name in round_data['locked_gifts']
                    color = '#ff6b6b' if is_locked else colors[gift_id % len(colors)]
                    
                    rect = plt.Rectangle((x_pos, y_pos-0.4), 2, 0.8, 
                                       facecolor=color, alpha=0.7, edgecolor='black')
                    ax_gifts.add_patch(rect)
                    
                    # Gift label
                    ax_gifts.text(x_pos + 1, y_pos, f'G{gift_id}\\n{gift_value}', 
                                ha='center', va='center', fontsize=8, fontweight='bold')
                    
                    if gift_id not in gift_positions:
                        gift_positions[gift_id] = []
                    gift_positions[gift_id].append((round_num, i))

    ax_gifts.set_xlim(-1, len(player_names) * 2.5)
    ax_gifts.set_ylim(0.5, len(rounds_data) + 1.5)
    ax_gifts.set_xlabel('Players', fontsize=12)
    ax_gifts.set_ylabel('Rounds (Latest at Top)', fontsize=12)
    ax_gifts.set_title('Gift Movement Through Rounds', fontsize=14, fontweight='bold')

    # Set player labels
    player_positions = [i * 2.5 + 1 for i in range(len(player_names))]
    ax_gifts.set_xticks(player_positions)
    ax_gifts.set_xticklabels([p.replace("Player ", "P") for p in player_names])

    # Right plot: Player summary
    y_pos = len(rounds_data)
    for round_data in rounds_data:
        round_num = round_data['round']
        player = round_data['player']
        
        ax_players.text(0, y_pos, f"Round {round_num}: {player}", fontsize=10, fontweight='bold')
        
        # Show current gifts
        x_pos = 3
        for p, gift_info in round_data['gifts_distribution'].items():
            gift_name, gift_value = gift_info
            if gift_name:
                gift_display = f"{p.replace('Player ', 'P')}: {gift_name} ({gift_value})"
            else:
                gift_display = f"{p.replace('Player ', 'P')}: No gift"
            
            ax_players.text(3, y_pos, gift_display, fontsize=6, va='center', style='italic')
            
            y_pos -= 0.6

    plt.savefig(output_path / 'white_elephant_round_by_round.png', dpi=150, bbox_inches='tight')
    print("✓ Round-by-round visualization saved!")

    # Also create a more compact version showing just the key moments (start of each turn + final)
    print("Creating compact turn summary...")

    fig_summary, ax_summary = plt.subplots(figsize=(20, 8))

    # Show gift state at start of each player's turn
    x_positions = []
    x_pos = 0

    for i, player in enumerate(players):
        x_positions.append(x_pos)
        
        # Title for this turn
        ax_summary.text(x_pos + 0.9, 7, f"{player}\\nStarts", ha='center', va='center', 
                      fontsize=10, fontweight='bold', bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue"))
        
        # Show what each player had at start of this turn
        y_pos = 6
        for j, other_player in enumerate(players):
            # Find what this player had at the start of turn i
            gift = None
            if i < len(turn_snapshots) and 'player_gifts' in turn_snapshots[i]:
                gift_info = turn_snapshots[i]['player_gifts'].get(other_player, (None, 0))
                if gift_info[0]:  # if gift name exists
                    gift_name, gift_value = gift_info
                    # Find the actual gift object
                    gift = next((g for g in gifts if g["name"] == gift_name), None)
            
            if gift:
                color = '#ff6b6b' if gift.get('locked', False) else '#95e1d3'
                rect = plt.Rectangle((x_pos, y_pos-0.2), 1.8, 0.4, 
                                   facecolor=color, alpha=0.7, edgecolor='black')
                ax_summary.add_patch(rect)
                
                ax_summary.text(x_pos + 0.9, y_pos, f"G{gift['id']}", ha='center', va='center', 
                              fontsize=8, fontweight='bold')
            else:
                ax_summary.text(x_pos + 0.9, y_pos, "—", ha='center', va='center', 
                              fontsize=8, color='gray')
            
            # Player label on left
            ax_summary.text(x_pos - 0.3, y_pos, other_player.replace("Player ", "P"), 
                          ha='right', va='center', fontsize=8)
            
            y_pos -= 0.6
        
        x_pos += 1.9

    plt.tight_layout()
    plt.savefig(output_path / 'white_elephant_turn_summary.png', dpi=200, bbox_inches='tight')
    print("✓ Turn summary visualization saved!")

    # Save game log to text file
    with open(output_path / 'game_log.txt', 'w') as f:
        f.write("WHITE ELEPHANT GIFT EXCHANGE - COMPLETE GAME LOG\n")
        f.write("=" * 60 + "\n\n")
        for entry in game_log:
            f.write(entry + "\n")
        
        f.write("\n" + "=" * 60 + "\n")
        f.write("FINAL RESULTS\n")
        f.write("=" * 60 + "\n")
        for player, gift in player_gifts.items():
            if gift:
                status = "LOCKED" if gift["locked"] else "Available"
                f.write(f"{player}: {gift['name']} (value: {gift['value']}, stolen: {gift['steals']}x, {status})\n")
        
        f.write("\n" + "=" * 60 + "\n")
        f.write("GIFT STATUS\n")
        f.write("=" * 60 + "\n")
        for gift in gifts:
            status = "LOCKED" if gift["locked"] else "Available"
            opened = "Opened" if gift["steals"] > 0 or any(p for p, g in player_gifts.items() if g == gift) else "Never opened"
            owner = "None"
            for p, g in player_gifts.items():
                if g == gift:
                    owner = p
                    break
            f.write(f"Gift #{gift['id']}: {gift['name']} (value: {gift['value']}) - {opened}, {status}, Owner: {owner}, Stolen: {gift['steals']} times\n")

    print("✓ Game log saved!")


def main():
    """Entry point for the white-elephant-sim command."""
    parser = argparse.ArgumentParser(
        description="Simulate a White Elephant gift exchange game"
    )
    parser.add_argument(
        "-o", "--output",
        default=".",
        help="Output directory for generated files (default: current directory)"
    )
    
    args = parser.parse_args()
    run_simulation(args.output)


if __name__ == "__main__":
    main()