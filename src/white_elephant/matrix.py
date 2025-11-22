import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Rectangle
import numpy as np
import argparse
from pathlib import Path


def create_matrix_visualization(output_dir=".", game_log_path=None):
    """Create matrix visualization and save to specified directory."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    if game_log_path is None:
        game_log_path = output_path / 'game_log.txt'
    else:
        game_log_path = Path(game_log_path)
    
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
    with open(game_log_path, 'r') as f:
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
                'action': f'{player} unwraps Gift #{gift_num}: {gift_name}',
                'gifts': {k: v.copy() for k, v in current_state.items()},
                'is_turn_start': False
            })
        
        # Check for steal
        if 'steals Gift #' in line:
            parts = line.split('steals Gift #')
            player = parts[0].strip()
            gift_num = int(parts[1].split(':')[0])
            gift_name = parts[1].split(':')[1].strip().split('from')[0].strip()
            victim = parts[1].split('from ')[1].strip()
            
            current_state[gift_num]['owner'] = player
            current_state[gift_num]['steals'] += 1
            
            if current_state[gift_num]['steals'] >= 3:
                current_state[gift_num]['locked'] = True
            
            action_states.append({
                'action': f'{player} steals Gift #{gift_num}: {gift_name} from {victim}',
                'gifts': {k: v.copy() for k, v in current_state.items()},
                'is_turn_start': False
            })

    # Create visualization
    num_states = len(action_states)
    num_gifts = 8

    # Calculate figure dimensions
    cell_height = 1.2
    cell_width = 2.0
    fig_height = num_states * cell_height + 4  # Extra space for title and legend
    fig_width = num_gifts * cell_width + 2

    fig, ax = plt.subplots(figsize=(fig_width, fig_height))

    # Remove axes
    ax.set_xlim(0, num_gifts * cell_width)
    ax.set_ylim(0, num_states * cell_height + 2)
    ax.axis('off')

    # Title
    ax.text(fig_width/2, fig_height-0.5, 'White Elephant Game Matrix - Round by Round View', 
           ha='center', va='center', fontsize=32, fontweight='bold')

    # Column headers (Gift numbers)
    for i in range(num_gifts):
        x = i * cell_width + cell_width/2
        y = num_states * cell_height + 1
        ax.text(x, y, f'G{i+1}', ha='center', va='center', fontsize=28, fontweight='bold')

    # Fill in the matrix
    for row, state in enumerate(reversed(action_states)):  # Reverse to have latest at top
        y = row * cell_height
        
        # Action label on the left
        action_text = state['action']
        if state.get('is_turn_start', False):
            # Make turn starts more prominent
            action_y = y + cell_height/2
            ax.text(-0.5, action_y, action_text, ha='right', va='center', 
                   fontsize=28, fontweight='bold', color='#2E86AB')
        else:
            action_y = y + cell_height/2
            ax.text(-0.5, action_y, action_text, ha='right', va='center', 
                   fontsize=18, style='italic')
        
        # Gift cells
        for gift_id in range(1, 9):
            x = (gift_id - 1) * cell_width
            
            gift_state = state['gifts'][gift_id]
            owner = gift_state['owner']
            steals = gift_state['steals']
            locked = gift_state['locked']
            
            # Determine cell color based on state
            if owner is None:
                color = '#d3d3d3'  # Gray for wrapped
            elif locked:
                color = '#ff6b6b'  # Red for locked
            elif steals == 2:
                color = '#ffd93d'  # Yellow for 2 steals
            elif steals == 1:
                color = '#a8dadc'  # Light blue for 1 steal
            else:
                color = '#95e1d3'  # Light green for opened, no steals
            
            # Draw cell
            rect = Rectangle((x, y), cell_width, cell_height, 
                           facecolor=color, edgecolor='black', linewidth=1)
            ax.add_patch(rect)
            
            # Gift number at top
            ax.text(x + cell_width/2, y + cell_height*0.8, f'G{gift_id}', 
                   ha='center', va='center', fontsize=18, fontweight='bold')
            
            # Owner in middle
            if owner:
                ax.text(x + cell_width/2, y + cell_height/2, owner.replace('Player ', 'P'), 
                       ha='center', va='center', fontsize=16)
            else:
                ax.text(x + cell_width/2, y + cell_height/2, '—', 
                       ha='center', va='center', fontsize=16)
            
            # Steal count in corner
            if steals > 0:
                ax.text(x + cell_width*0.9, y + cell_height*0.1, f'×{steals}', 
                       ha='right', va='bottom', fontsize=12, fontweight='bold')

    # Add legend
    legend_items = [
        ('#d3d3d3', 'Wrapped'),
        ('#95e1d3', 'Opened (0 steals)'),
        ('#a8dadc', 'Stolen once'),
        ('#ffd93d', 'Stolen twice'),
        ('#ff6b6b', 'Locked (3 steals)')
    ]

    legend_x = 0
    legend_y = -1.5
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
    plt.savefig(output_path / 'white_elephant_matrix.png', dpi=150, bbox_inches='tight')
    print(f"✓ Matrix visualization created with {num_states} states!")
    print(f"  Dimensions: {fig_width:.1f} × {fig_height:.1f}")


def main():
    """Entry point for the white-elephant-matrix command."""
    parser = argparse.ArgumentParser(
        description="Create matrix visualization for White Elephant game"
    )
    parser.add_argument(
        "-o", "--output",
        default=".",
        help="Output directory for generated files (default: current directory)"
    )
    parser.add_argument(
        "--game-log",
        help="Path to game log file (default: look in output directory)"
    )
    
    args = parser.parse_args()
    create_matrix_visualization(args.output, args.game_log)


if __name__ == "__main__":
    main()