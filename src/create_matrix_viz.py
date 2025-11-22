import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Rectangle
import numpy as np

# Read action snapshots from the simulation
# We'll reconstruct from the game log
action_states = []

# Initial state - all wrapped
initial_state = {
    'action': 'Initial State - All Gifts Wrapped',
    'gifts': {i: {'owner': None, 'steals': 0, 'locked': False} for i in range(1, 9)},
    'is_turn_start': False
}
action_states.append(initial_state)

# Parse game log to build states
with open('/mnt/user-data/outputs/game_log.txt', 'r') as f:
    lines = f.readlines()

current_state = {i: {'owner': None, 'steals': 0, 'locked': False} for i in range(1, 9)}
gift_names = {
    'Bluetooth Speaker': 1,
    'Luxury Candle Set': 2,
    'Board Game Collection': 3,
    'Electric Wine Opener': 4,
    'Cozy Throw Blanket': 5,
    'Gourmet Coffee Set': 6,
    'Portable Phone Charger': 7,
    'Kitchen Gadget Bundle': 8,
}

for line in lines:
    line = line.strip()
    
    # Check for turn start
    if '=== Player' in line and 'Turn ===' in line:
        player_num = line.split('Player ')[1].split("'")[0]
        action_states.append({
            'action': f'--- Start of Player {player_num} Turn ---',
            'gifts': {k: v.copy() for k, v in current_state.items()},
            'is_turn_start': True
        })
        continue
    
    # Check for unwrap
    if 'unwraps Gift #' in line:
        parts = line.split('unwraps Gift #')
        player = parts[0].strip()
        gift_num = int(parts[1].split(':')[0])
        gift_name = parts[1].split(':')[1].strip().split('(')[0].strip()
        
        current_state[gift_num]['owner'] = player
        
        action_states.append({
            'action': f'{player} unwraps Gift #{gift_num} ({gift_name})',
            'gifts': {k: v.copy() for k, v in current_state.items()},
            'is_turn_start': False,
            'changed_gift': gift_num  # Mark which gift changed
        })
        continue
    
    # Check for steal
    if 'steals' in line and 'from' in line and 'LOCKED' not in line and '->' not in line:
        parts = line.split('steals')
        player = parts[0].strip()
        gift_and_victim = parts[1].split('from')
        gift_name = gift_and_victim[0].strip().strip("'")
        victim = gift_and_victim[1].strip().strip('!')
        
        if gift_name in gift_names:
            gift_num = gift_names[gift_name]
            current_state[gift_num]['owner'] = player
            current_state[gift_num]['steals'] += 1
            
            action_states.append({
                'action': f'{player} steals Gift #{gift_num} from {victim}',
                'gifts': {k: v.copy() for k, v in current_state.items()},
                'is_turn_start': False,
                'changed_gift': gift_num  # Mark which gift changed
            })
        continue
    
    # Check for lock
    if 'LOCKED' in line and '->' in line:
        parts = line.split("'")
        if len(parts) >= 2:
            gift_name = parts[1]
            if gift_name in gift_names:
                gift_num = gift_names[gift_name]
                current_state[gift_num]['locked'] = True
                
                # For lock events, we need to ensure the gift that locked is marked as changed
                # even though owner didn't change
                action_states.append({
                    'action': f'Gift #{gift_num} LOCKED (3 steals)',
                    'gifts': {k: v.copy() for k, v in current_state.items()},
                    'is_turn_start': False,
                    'changed_gift': gift_num  # Mark which gift changed for highlighting
                })

# Create the matrix visualization
num_states = len(action_states)
cell_height = 1.2
cell_width = 2.0
action_text_width = 8

fig_width = 8 * cell_width + action_text_width + 2
fig_height = num_states * cell_height + 2

fig, ax = plt.subplots(figsize=(fig_width, fig_height))
ax.set_xlim(0, fig_width)
ax.set_ylim(-7, fig_height)  # Extended lower limit to include legend boxes
ax.axis('off')

# Title - SAME SIZE AS TURN LABELS
title_y = fig_height - 0.5
ax.text(fig_width / 2, title_y, 'White Elephant Gift Exchange - Round-by-Round State Matrix', 
        fontsize=28, fontweight='bold', ha='center')

# Draw each state row - with extra space below title
current_y = fig_height - 2.5
previous_state = None

for state_idx, state in enumerate(action_states):
    is_turn_start = state.get('is_turn_start', False)
    
    # If it's a turn start, draw a separator line
    if is_turn_start:
        # Add extra space before turn start
        current_y -= 0.5  # Extra space between last action and turn separator
        
        ax.plot([0.5, fig_width - 0.5], [current_y + cell_height - 0.1, current_y + cell_height - 0.1], 
                'k--', linewidth=2, alpha=0.5)
        
        # Draw turn start label across the full width - DOUBLED FONT SIZE
        turn_label_y = current_y + cell_height / 2
        ax.text(fig_width / 2, turn_label_y, state['action'], 
                fontsize=28, fontweight='bold', ha='center', style='italic',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow', alpha=0.8))
        
        current_y -= cell_height
        # Don't update previous_state for turn starts - they don't represent actual game actions
        continue
    
    # Draw each gift cell
    for gift_num in range(1, 9):
        x = 1 + (gift_num - 1) * cell_width
        y = current_y
        
        gift_state = state['gifts'][gift_num]
        owner = gift_state['owner']
        steals = gift_state['steals']
        locked = gift_state['locked']
        
        # Check if this cell changed from previous state
        cell_changed = False
        
        # First check if this gift is marked as the changed gift in the state
        if 'changed_gift' in state and state['changed_gift'] == gift_num:
            cell_changed = True
        # Otherwise, check for changes from previous state
        elif previous_state and not previous_state.get('is_turn_start', False):
            prev_gift = previous_state['gifts'][gift_num]
            # Purple outline for: new gift opened (None -> owner) OR any owner change (steal)
            if prev_gift['owner'] != owner:
                cell_changed = True
            # Also check for steals count or locked status changes
            elif prev_gift['steals'] != steals or prev_gift['locked'] != locked:
                cell_changed = True
        
        # Determine color based on state
        if owner is None:
            color = '#d3d3d3'  # Gray for wrapped
            edge_color = '#999999'
        elif locked:
            color = '#ff6b6b'  # Red for locked
            edge_color = '#c92a2a'
        elif steals >= 2:
            color = '#ffd93d'  # Yellow for 2 steals
            edge_color = '#f08c00'
        elif steals >= 1:
            color = '#a8dadc'  # Light blue for 1 steal
            edge_color = '#457b9d'
        else:
            color = '#95e1d3'  # Green for opened but not stolen
            edge_color = '#38b000'
        
        # Override edge color and width if cell changed
        if cell_changed:
            edge_color = '#8B008B'  # Dark purple/magenta
            edge_width = 6  # Thicker purple outline
        else:
            edge_width = 2
        
        # Draw cell box
        box = Rectangle((x, y), cell_width - 0.1, cell_height - 0.1,
                       facecolor=color, edgecolor=edge_color, linewidth=edge_width)
        ax.add_patch(box)
        
        # Draw gift number - MUCH LARGER
        ax.text(x + cell_width / 2, y + cell_height * 0.68, f'G{gift_num}', 
                fontsize=18, fontweight='bold', ha='center', va='center')
        
        # Draw owner - MUCH LARGER
        # Check if this is a steal (owner changed from previous state)
        owner_display = ""
        if owner:
            owner_short = owner.replace('Player ', 'P')
            
            # Check if this was a steal by comparing to previous NON-turn-start state
            is_steal = False
            prev_owner = None
            if previous_state and not previous_state.get('is_turn_start', False):
                prev_gift = previous_state['gifts'][gift_num]
                prev_owner_full = prev_gift['owner']
                if prev_owner_full and prev_owner_full != owner:
                    # This is a steal!
                    is_steal = True
                    prev_owner = prev_owner_full.replace('Player ', 'P')
            
            # Display format based on whether it's a steal
            if is_steal and prev_owner:
                owner_display = f"{prev_owner} → {owner_short}"
                font_size = 14  # Slightly smaller to fit arrow notation
            else:
                owner_display = owner_short
                font_size = 16
            
            ax.text(x + cell_width / 2, y + cell_height * 0.32, owner_display, 
                    fontsize=font_size, ha='center', va='center', color='darkblue', fontweight='bold')
        else:
            ax.text(x + cell_width / 2, y + cell_height * 0.32, '—', 
                    fontsize=16, ha='center', va='center', color='gray')
        
        # Draw steal count if > 0 - LARGER
        if steals > 0:
            ax.text(x + cell_width - 0.25, y + cell_height - 0.25, f'×{steals}', 
                    fontsize=12, ha='right', va='top', fontweight='bold',
                    color='red' if locked else 'darkorange')
    
    # Draw action description - SAME SIZE AS TURN LABELS
    action_x = 1 + 8 * cell_width + 0.3
    action_text = state['action']
    
    # Shorten action text if too long
    if len(action_text) > 50:
        action_text = action_text[:47] + '...'
    
    ax.text(action_x, current_y + cell_height / 2, action_text, 
            fontsize=28, ha='left', va='center',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8, edgecolor='gray'))
    
    current_y -= cell_height
    previous_state = state  # Update previous state for next iteration

# Add legend at the bottom with much more space to avoid overlap
legend_y = -5.0  # Moving much further below to completely avoid overlap
legend_x = 1
ax.text(legend_x, legend_y + 0.5, 'Legend:', fontsize=28, fontweight='bold')

legend_items = [
    ('#d3d3d3', 'Wrapped'),
    ('#95e1d3', 'Opened'),
    ('#a8dadc', 'Stolen once'),
    ('#ffd93d', 'Stolen twice'),
    ('#ff6b6b', 'Locked (3 steals)')
]

legend_y_pos = legend_y - 0.5
for i, (color, label) in enumerate(legend_items):
    x = legend_x + i * 4.5
    # Draw colored box
    box = Rectangle((x, legend_y_pos), 0.8, 0.6,
                   facecolor=color, edgecolor='black', linewidth=2)
    ax.add_patch(box)
    # Draw label text at same size as action notes
    ax.text(x + 1.0, legend_y_pos + 0.3, label, fontsize=28, va='center')

plt.tight_layout(pad=0.5)
plt.savefig('/mnt/user-data/outputs/white_elephant_matrix.png', dpi=150, bbox_inches='tight')
print(f"✓ Matrix visualization created with {num_states} states!")
print(f"  Dimensions: {fig_width:.1f} × {fig_height:.1f}")
