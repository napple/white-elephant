import random
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

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
                action_desc = f"{active_player} steals '{steal_target['name']}' from {victim}"
                turn_log.append(f"  {action_desc}!")
                player_gifts[active_player] = steal_target
                player_gifts[victim] = None
                steal_target["steals"] += 1
                action_snapshots.append(capture_game_state(action_desc))
                
                # Update just_stolen_gift to prevent immediate steal-back
                just_stolen_gift = steal_target
                
                # Check if gift is now locked
                if steal_target["steals"] >= 3:
                    steal_target["locked"] = True
                    lock_desc = f"'{steal_target['name']}' LOCKED (3 steals)"
                    turn_log.append(f"    -> {lock_desc}")
                    action_snapshots.append(capture_game_state(lock_desc))
                    # CRITICAL: Even though gift is locked, the victim still needs a gift!
                    # The chain continues with the victim as active player
                    active_player = victim
                    just_stolen_gift = None  # Reset since the locked gift can't be stolen back anyway
                    # Do NOT end the chain - victim must get a gift
                else:
                    # Victim becomes active player for next iteration
                    active_player = victim
            else:
                chain_active = False
    
    return turn_log

# Simulate the game
print("WHITE ELEPHANT GIFT EXCHANGE SIMULATION")
print("(With No Immediate Steal-Back Rule)")
print("=" * 50)

available_gift_ids = [g["id"] for g in gifts]
opened_gifts = []

for turn in range(8):
    turn_log = execute_turn(turn, available_gift_ids, opened_gifts)
    for log_entry in turn_log:
        print(log_entry)
        game_log.append(log_entry)
    
    # Take snapshot
    snapshot = {
        "turn": turn + 1,
        "player_gifts": {p: g["name"] if g else "None" for p, g in player_gifts.items()},
        "locked_gifts": [g["name"] for g in gifts if g["locked"]]
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

if len(available_gift_ids) > 0:
    print(f"ERROR: {len(available_gift_ids)} wrapped gifts remaining")
else:
    print("✓ All wrapped gifts were opened")

# Count gifts
gift_count = sum(1 for g in player_gifts.values() if g is not None)
print(f"\nGift distribution: {gift_count} gifts distributed to {len(players)} players")

# Final results
print("\n" + "=" * 50)
print("FINAL RESULTS")
print("=" * 50)
for i in range(8):
    player = players[i]
    gift = player_gifts[player]
    if gift:
        locked_status = " [LOCKED]" if gift["locked"] else ""
        print(f"{player}: {gift['name']} (value: {gift['value']}, stolen {gift['steals']} times){locked_status}")
    else:
        print(f"{player}: No gift")

print("\n" + "=" * 50)
print("GIFT STATUS")
print("=" * 50)
for gift in gifts:
    status = "LOCKED" if gift["locked"] else "Available"
    opened = "Opened" if gift["steals"] > 0 or any(p for p, g in player_gifts.items() if g == gift) else "Never opened"
    owner = "None"
    for p, g in player_gifts.items():
        if g == gift:
            owner = p
            break
    print(f"Gift #{gift['id']}: {gift['name']} (value: {gift['value']}) - {opened}, {status}, Owner: {owner}, Stolen: {gift['steals']} times")

# Create visualization
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 10))

# Left panel: Gift flow chart
ax1.set_xlim(0, 10)
ax1.set_ylim(0, 10)
ax1.axis('off')
ax1.set_title('Gift Distribution & Stealing History', fontsize=16, fontweight='bold', pad=20)

# Show final state with color coding
y_pos = 9
for i in range(8):
    player = players[i]
    gift = player_gifts[player]
    if gift:
        # Color based on number of steals
        if gift["locked"]:
            color = '#ff6b6b'  # Red for locked
            edge_color = '#c92a2a'
        elif gift["steals"] >= 2:
            color = '#ffd93d'  # Yellow for 2 steals
            edge_color = '#f08c00'
        elif gift["steals"] >= 1:
            color = '#a8dadc'  # Light blue for 1 steal
            edge_color = '#457b9d'
        else:
            color = '#95e1d3'  # Green for no steals
            edge_color = '#38b000'
        
        # Draw box
        box = FancyBboxPatch((0.5, y_pos - 0.3), 8, 0.5, 
                             boxstyle="round,pad=0.05", 
                             facecolor=color, 
                             edgecolor=edge_color, 
                             linewidth=2)
        ax1.add_patch(box)
        
        # Add text
        locked_text = " 🔒" if gift["locked"] else ""
        ax1.text(1, y_pos, f"{player}:", fontsize=11, fontweight='bold', va='center')
        ax1.text(5, y_pos, f"{gift['name']}{locked_text}", fontsize=10, va='center')
        ax1.text(8.5, y_pos, f"(×{gift['steals']})", fontsize=9, va='center', style='italic')
        
        y_pos -= 0.8
    else:
        # Show players with no gift
        box = FancyBboxPatch((0.5, y_pos - 0.3), 8, 0.5, 
                             boxstyle="round,pad=0.05", 
                             facecolor='#e0e0e0', 
                             edgecolor='#999999', 
                             linewidth=2,
                             linestyle='dashed')
        ax1.add_patch(box)
        ax1.text(1, y_pos, f"{player}:", fontsize=11, fontweight='bold', va='center')
        ax1.text(5, y_pos, "No gift", fontsize=10, va='center', style='italic', color='#666666')
        y_pos -= 0.8

# Add legend
legend_y = 1.5
ax1.text(0.5, legend_y, "Legend:", fontsize=10, fontweight='bold')
legend_items = [
    ('#95e1d3', "Never stolen"),
    ('#a8dadc', "Stolen once"),
    ('#ffd93d', "Stolen twice"),
    ('#ff6b6b', "Locked (3 steals)")
]
legend_x = 0.5
legend_y -= 0.5
for color, label in legend_items:
    box = FancyBboxPatch((legend_x, legend_y - 0.15), 0.4, 0.3,
                         boxstyle="round,pad=0.02",
                         facecolor=color, edgecolor='black', linewidth=1)
    ax1.add_patch(box)
    ax1.text(legend_x + 0.6, legend_y, label, fontsize=9, va='center')
    legend_x += 2.3

# Right panel: Gift value and popularity chart
gift_names = [g['name'] for g in gifts]
gift_values = [g['value'] for g in gifts]
gift_steals = [g['steals'] for g in gifts]

x = np.arange(len(gift_names))
width = 0.35

bars1 = ax2.barh(x - width/2, gift_values, width, label='Gift Value', color='#4a90e2', alpha=0.8)
bars2 = ax2.barh(x + width/2, [s * 30 for s in gift_steals], width, label='Times Stolen (×30)', color='#e74c3c', alpha=0.8)

ax2.set_yticks(x)
ax2.set_yticklabels(gift_names, fontsize=9)
ax2.set_xlabel('Value / Popularity', fontsize=11)
ax2.set_title('Gift Desirability vs. Actual Steals', fontsize=14, fontweight='bold')
ax2.legend(fontsize=10)
ax2.grid(axis='x', alpha=0.3)

# Add value labels on bars
for bar, value in zip(bars1, gift_values):
    width_val = bar.get_width()
    ax2.text(width_val + 1, bar.get_y() + bar.get_height()/2, 
             f'{value}', ha='left', va='center', fontsize=8)

for bar, steals in zip(bars2, gift_steals):
    width_val = bar.get_width()
    if steals > 0:
        ax2.text(width_val + 1, bar.get_y() + bar.get_height()/2, 
                 f'{steals}×', ha='left', va='center', fontsize=8, color='#c92a2a', fontweight='bold')

plt.tight_layout()
plt.savefig('/mnt/user-data/outputs/white_elephant_simulation.png', dpi=300, bbox_inches='tight')
print("\n✓ Visualization saved!")

# Create round-by-round visualization
print("Creating round-by-round visualization...")

# Create a comprehensive timeline visualization
num_actions = len(action_snapshots)
fig_height = max(12, num_actions * 0.4)
fig = plt.figure(figsize=(18, fig_height))

# Create grid for subplots
gs = fig.add_gridspec(num_actions, 2, width_ratios=[2, 1], hspace=0.3, wspace=0.2)

for idx, snapshot in enumerate(action_snapshots):
    # Left side: Gift status
    ax_gifts = fig.add_subplot(gs[idx, 0])
    ax_gifts.set_xlim(0, 10)
    ax_gifts.set_ylim(0, 9)
    ax_gifts.axis('off')
    
    # Title
    action_text = snapshot["action"]
    ax_gifts.text(5, 8.5, action_text, fontsize=9, fontweight='bold', ha='center', 
                  bbox=dict(boxstyle='round,pad=0.5', facecolor='lightblue', alpha=0.7))
    
    # Draw gifts
    y_pos = 7.5
    for gift in snapshot["gifts"]:
        # Determine color based on status
        if not gift["opened"]:
            color = '#d3d3d3'  # Gray for wrapped
            edge_color = '#999999'
            status_icon = "🎁"
        elif gift["locked"]:
            color = '#ff6b6b'  # Red for locked
            edge_color = '#c92a2a'
            status_icon = "🔒"
        elif gift["steals"] >= 2:
            color = '#ffd93d'  # Yellow for 2 steals
            edge_color = '#f08c00'
            status_icon = "⚠️"
        elif gift["steals"] >= 1:
            color = '#a8dadc'  # Light blue for 1 steal
            edge_color = '#457b9d'
            status_icon = "↔️"
        else:
            color = '#95e1d3'  # Green for opened but not stolen
            edge_color = '#38b000'
            status_icon = "✓"
        
        # Draw box
        box = FancyBboxPatch((0.1, y_pos - 0.25), 9.8, 0.4, 
                             boxstyle="round,pad=0.02", 
                             facecolor=color, 
                             edgecolor=edge_color, 
                             linewidth=1.5)
        ax_gifts.add_patch(box)
        
        # Gift info
        gift_text = f"#{gift['id']}: {gift['name']}"
        owner_text = gift["owner"] if gift["owner"] else "Wrapped"
        steals_text = f"×{gift['steals']}" if gift['steals'] > 0 else ""
        
        ax_gifts.text(0.3, y_pos, gift_text, fontsize=7, va='center', fontweight='bold')
        ax_gifts.text(5, y_pos, owner_text, fontsize=7, va='center', style='italic')
        ax_gifts.text(9.5, y_pos, steals_text, fontsize=7, va='center', ha='right', 
                     fontweight='bold' if gift['steals'] > 0 else 'normal')
        
        y_pos -= 0.6
    
    # Right side: Player status
    ax_players = fig.add_subplot(gs[idx, 1])
    ax_players.set_xlim(0, 5)
    ax_players.set_ylim(0, 9)
    ax_players.axis('off')
    
    # Title
    ax_players.text(2.5, 8.5, "Players", fontsize=9, fontweight='bold', ha='center')
    
    # Draw players
    y_pos = 7.5
    for i, player in enumerate(players):
        player_info = snapshot["players"][player]
        has_gift = player_info["gift_name"] is not None
        
        if has_gift:
            color = '#90EE90'  # Light green
            edge_color = '#228B22'
            gift_display = player_info["gift_name"][:20]  # Truncate if too long
        else:
            color = '#FFB6C6'  # Light red
            edge_color = '#DC143C'
            gift_display = "No gift"
        
        # Draw box
        box = FancyBboxPatch((0.1, y_pos - 0.25), 4.8, 0.4, 
                             boxstyle="round,pad=0.02", 
                             facecolor=color, 
                             edgecolor=edge_color, 
                             linewidth=1.5)
        ax_players.add_patch(box)
        
        # Player info
        ax_players.text(0.3, y_pos, player, fontsize=7, va='center', fontweight='bold')
        ax_players.text(3, y_pos, gift_display, fontsize=6, va='center', style='italic')
        
        y_pos -= 0.6

plt.savefig('/mnt/user-data/outputs/white_elephant_round_by_round.png', dpi=150, bbox_inches='tight')
print("✓ Round-by-round visualization saved!")

# Also create a more compact version showing just the key moments (start of each turn + final)
print("Creating compact turn summary...")

turn_indices = [0]  # Start
for i, snapshot in enumerate(action_snapshots):
    if "Start of Player" in snapshot["action"]:
        turn_indices.append(i)
turn_indices.append(len(action_snapshots) - 1)  # Final state
turn_indices = list(set(turn_indices))  # Remove duplicates
turn_indices.sort()

num_key_moments = len(turn_indices)
fig, axes = plt.subplots(num_key_moments, 1, figsize=(16, num_key_moments * 2))
if num_key_moments == 1:
    axes = [axes]

for plot_idx, snap_idx in enumerate(turn_indices):
    snapshot = action_snapshots[snap_idx]
    ax = axes[plot_idx]
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 2)
    ax.axis('off')
    
    # Title
    ax.text(8, 1.7, snapshot["action"], fontsize=11, fontweight='bold', ha='center',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='lightblue', alpha=0.8))
    
    # Draw all gifts in a row
    x_pos = 0.5
    for gift in snapshot["gifts"]:
        # Determine color
        if not gift["opened"]:
            color = '#d3d3d3'
        elif gift["locked"]:
            color = '#ff6b6b'
        elif gift["steals"] >= 2:
            color = '#ffd93d'
        elif gift["steals"] >= 1:
            color = '#a8dadc'
        else:
            color = '#95e1d3'
        
        # Draw box
        box = FancyBboxPatch((x_pos, 0.2), 1.7, 1.2, 
                             boxstyle="round,pad=0.05", 
                             facecolor=color, 
                             edgecolor='black', 
                             linewidth=1)
        ax.add_patch(box)
        
        # Gift info
        ax.text(x_pos + 0.85, 1.1, f"#{gift['id']}", fontsize=8, ha='center', fontweight='bold')
        owner_display = gift["owner"][-1] if gift["owner"] else "—"  # Just player number
        ax.text(x_pos + 0.85, 0.7, owner_display, fontsize=9, ha='center', 
                fontweight='bold', color='darkblue' if gift["owner"] else 'gray')
        if gift['steals'] > 0:
            ax.text(x_pos + 0.85, 0.3, f"×{gift['steals']}", fontsize=7, ha='center', 
                   style='italic', fontweight='bold')
        
        x_pos += 1.9

plt.tight_layout()
plt.savefig('/mnt/user-data/outputs/white_elephant_turn_summary.png', dpi=200, bbox_inches='tight')
print("✓ Turn summary visualization saved!")

# Save game log to text file
with open('/mnt/user-data/outputs/game_log.txt', 'w') as f:
    f.write("WHITE ELEPHANT GIFT EXCHANGE - COMPLETE GAME LOG\n")
    f.write("=" * 60 + "\n\n")
    for entry in game_log:
        f.write(entry + "\n")
    f.write("\n" + "=" * 60 + "\n")
    f.write("FINAL RESULTS\n")
    f.write("=" * 60 + "\n")
    for i in range(8):
        player = players[i]
        gift = player_gifts[player]
        if gift:
            locked_status = " [LOCKED]" if gift["locked"] else ""
            f.write(f"{player}: {gift['name']} (value: {gift['value']}, stolen {gift['steals']} times){locked_status}\n")
        else:
            f.write(f"{player}: No gift\n")
    
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
