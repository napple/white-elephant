# White Elephant Simulation and Visualization Scripts

## Overview

This package contains Python scripts to simulate White Elephant gift exchange games and create comprehensive visualizations of the game flow.

## Files Included

1. **white_elephant_rules.md** - Complete game rules and strategy guide
2. **white_elephant_sim.py** - Main simulation script
3. **create_matrix_viz.py** - Creates the round-by-round matrix visualization
4. **create_gift_journeys.py** - Creates individual gift journey timelines

## Requirements

### Python Version
- Python 3.7 or higher

### Required Libraries
```bash
pip install matplotlib numpy
```

## How to Use

### 1. Run a Simulation

The simulation script generates a random game and creates several visualizations:

```bash
python white_elephant_sim.py
```

**What it creates:**
- `white_elephant_simulation.png` - Final results summary
- `white_elephant_turn_summary.png` - Compact turn-by-turn view
- `game_log.txt` - Complete text narrative of the game

**Output from simulation:**
- Console output showing each turn's actions
- Validation that all players have gifts and all gifts are opened
- Final results showing who ended with what

### 2. Create Matrix Visualization

After running the simulation, create the detailed round-by-round matrix:

```bash
python create_matrix_viz.py
```

**What it creates:**
- `white_elephant_matrix.png` - Complete round-by-round state matrix

**Features:**
- Shows state after every single action
- Purple highlights indicate which gift changed
- Steal transfers shown as "P1 → P3" (from → to)
- Color coding for steal frequency
- Large, readable text (size 28 for labels)
- Clear turn separators
- Comprehensive legend with color boxes

### 3. Create Gift Journeys

Optional - creates a timeline for each individual gift:

```bash
python create_gift_journeys.py
```

**What it creates:**
- `white_elephant_gift_journeys.png` - Individual timelines for all 8 gifts

## Script Details

### white_elephant_sim.py

**Purpose:** Simulates a complete White Elephant game with 8 players and 8 gifts.

**Key Features:**
- Randomized gift values (50-90)
- Strategic AI decision-making for steals vs unwraps
- No immediate steal-back rule enforced
- 3-steal lock rule enforced
- Guarantees all players end with exactly one gift
- Guarantees all gifts are opened

**Customization Options:**

You can modify these variables in the script:

```python
# Gift values and names (lines 9-18)
gifts = [
    {"id": 1, "name": "Bluetooth Speaker", "value": 85, ...},
    # Modify values and names as desired
]

# Steal decision thresholds (lines 48-54)
if best_available["value"] >= 75:  # High value gift
    steal_chance = 0.8  # 80% chance to steal
# Adjust these percentages for more/less aggressive stealing
```

**Output Files:**
- `white_elephant_simulation.png` - Bar charts and final distribution
- `white_elephant_turn_summary.png` - Turn-by-turn compact view
- `game_log.txt` - Text narrative

### create_matrix_viz.py

**Purpose:** Creates a detailed matrix showing game state after every action.

**Key Features:**
- One row per action (unwrap, steal, lock)
- 8 columns (one per gift)
- Purple highlights (6px thick) on changed cells
- Ownership transfer notation for steals (P1 → P3)
- Color coding based on steal frequency
- Large text (size 28) for readability
- Turn separators with extra spacing
- Complete legend with color indicators

**Customization Options:**

```python
# Font sizes (various lines)
fontsize=28  # For title, actions, turns, legend
fontsize=18  # For gift numbers
fontsize=16  # For owners
fontsize=14  # For steal transfers

# Colors (lines 174-188)
'#d3d3d3'  # Gray - Wrapped
'#95e1d3'  # Green - Opened (0 steals)
'#a8dadc'  # Light blue - Stolen once
'#ffd93d'  # Yellow - Stolen twice
'#ff6b6b'  # Red - Locked (3 steals)
'#8B008B'  # Purple - Changed cell highlight

# Cell dimensions (lines 101-102)
cell_height = 1.2
cell_width = 2.0
```

**Output Files:**
- `white_elephant_matrix.png` - Complete matrix (can be very tall!)

### create_gift_journeys.py

**Purpose:** Creates timeline visualizations for each gift's journey through the game.

**Key Features:**
- 8 separate panels (one per gift)
- Shows every unwrap and steal event
- Green boxes for unwraps
- Orange/red boxes for steals
- Indicates final owner
- Shows total steal count

**Output Files:**
- `white_elephant_gift_journeys.png` - All gift journeys in one image

## Understanding the Visualizations

### Matrix Visualization

**Reading the Matrix:**
- **Rows**: Each row shows the state after one action
- **Columns**: Each column represents one gift (G1-G8)
- **Cell Contents**: 
  - Top: Gift number (G1, G2, etc.)
  - Middle: Owner (P1-P8) or "—" for wrapped
  - For steals: Shows "P1 → P3" (from player → to player)
  - Corner: Steal count (×1, ×2, ×3)

**Color Coding:**
- Gray: Wrapped (not yet opened)
- Green: Opened, never stolen
- Light Blue: Stolen once
- Yellow: Stolen twice
- Red: Locked (3 steals)
- Purple outline: Gift changed in this action

**Turn Separators:**
- Yellow banners mark the start of each player's turn
- Extra spacing between turns for clarity

### Gift Journeys Visualization

**Reading the Journeys:**
- Each panel shows one gift's complete story
- Read from top to bottom (chronological)
- Green = Unwrap event
- Orange/Red = Steal event (red if 3rd steal)
- Blue = Final owner

## Troubleshooting

### Common Issues

**"ModuleNotFoundError: No module named 'matplotlib'"**
```bash
pip install matplotlib numpy
```

**"FileNotFoundError: game_log.txt not found"**
- Run `white_elephant_sim.py` first
- The matrix visualization script reads the game log

**Matrix image is too large to view**
- The matrix can be very tall (30+ rows)
- Open in an image viewer that supports zooming
- Or use image editing software to view sections

**Text is too small/large**
- Edit the `fontsize` parameters in the scripts
- Increase for larger text, decrease for smaller

### Performance Notes

- Simulation runs in < 1 second
- Matrix visualization takes 2-5 seconds depending on game length
- Gift journeys visualization takes 1-2 seconds

## Advanced Usage

### Running Multiple Simulations

To compare different games:

```bash
# Run simulation 1
python white_elephant_sim.py
mv white_elephant_matrix.png game1_matrix.png

# Run simulation 2
python white_elephant_sim.py
mv white_elephant_matrix.png game2_matrix.png

# Compare the results
```

### Customizing Gift Values

Edit the `gifts` array in `white_elephant_sim.py`:

```python
gifts = [
    {"id": 1, "name": "Your Gift Name", "value": 75, "steals": 0, "locked": False},
    # Add your 8 gifts here with values 0-100
]
```

### Adjusting Steal Probability

In `white_elephant_sim.py`, modify the steal decision logic:

```python
def steal_decision(current_player, available_gifts, opened_gifts, just_stolen_gift=None):
    # Change these thresholds to make stealing more/less likely
    if best_available["value"] >= 75:
        steal_chance = 0.8  # 80% chance to steal high-value
    elif best_available["value"] >= 65:
        steal_chance = 0.6  # 60% chance to steal medium-value
    else:
        steal_chance = 0.3  # 30% chance to steal low-value
```

## Tips for Best Results

### For Game Night

1. **Print the rules**: Use `white_elephant_rules.md`
2. **Project the matrix**: Use `white_elephant_matrix.png` on a screen to track the game live
3. **Keep it as a souvenir**: Save all visualizations after the game

### For Analysis

1. Run multiple simulations to see different outcomes
2. Compare steal patterns across games
3. Analyze which gift values tend to lock most often

### For Presentations

1. Use `white_elephant_simulation.png` for summary slides
2. Use `white_elephant_turn_summary.png` for quick overview
3. Use `white_elephant_matrix.png` for detailed analysis

## License

These scripts are provided for personal use. Feel free to modify and adapt for your own White Elephant games!

## Support

For issues or questions:
1. Check this README first
2. Review the game rules in `white_elephant_rules.md`
3. Examine the script comments for detailed explanations

Enjoy your White Elephant game! 🎁
