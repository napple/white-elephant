# White Elephant Simulation and Visualization Scripts

## Overview

This package contains Python scripts to simulate White Elephant gift exchange games and create comprehensive visualizations of the game flow.

## Files Included

This package provides:
- **White Elephant simulation** - Complete game simulation with AI players
- **Matrix visualization** - Round-by-round game state visualization
- **Command-line tools** - Easy-to-use scripts via pip install

## Installation

### Requirements
- Python 3.8 or higher
- pip (Python package manager)

### Install from Source
```bash
# Clone the repository
git clone <repository-url>
cd white-elephant

# Install the package with dependencies
pip install -e .

# Or install with development tools
pip install -e ".[dev]"
```

## How to Use

### 1. Run a Simulation

The simulation script generates a random game and creates several visualizations:

```bash
# Run in current directory
white-elephant-sim

# Specify output directory
white-elephant-sim -o /path/to/output
white-elephant-sim --output ./results
```

**Alternative:** You can also run it directly with Python:
```bash
python -m white_elephant.simulation
python -m white_elephant.simulation -o /path/to/output
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
# Use game log from current directory
white-elephant-matrix

# Specify output directory
white-elephant-matrix -o /path/to/output

# Use specific game log file
white-elephant-matrix --game-log /path/to/game_log.txt -o ./visualizations
```

**Alternative:** You can also run it directly with Python:
```bash
python -m white_elephant.matrix
python -m white_elephant.matrix -o /path/to/output
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

## Command Line Options

Both commands support flexible output directory specification:

### white-elephant-sim Options
```bash
white-elephant-sim --help
```

- `-o, --output DIR`: Output directory for generated files (default: current directory)

**Examples:**
```bash
# Basic usage - files saved to current directory
white-elephant-sim

# Save to specific directory
white-elephant-sim -o ./game-results
white-elephant-sim --output /tmp/white-elephant

# Directory will be created if it doesn't exist
white-elephant-sim -o ~/Documents/games/session-$(date +%Y%m%d)
```

### white-elephant-matrix Options  
```bash
white-elephant-matrix --help
```

- `-o, --output DIR`: Output directory for generated files (default: current directory)
- `--game-log FILE`: Path to game log file (default: look in output directory for game_log.txt)

**Examples:**
```bash
# Use game_log.txt from current directory
white-elephant-matrix

# Use game log from specific location, save matrix to current directory  
white-elephant-matrix --game-log /path/to/game_log.txt

# Use specific game log and save to specific directory
white-elephant-matrix --game-log ~/games/session1/game_log.txt -o ~/games/session1

# Process existing game log and save visualization elsewhere
white-elephant-matrix --game-log ./old-games/game_log.txt -o ./analysis
```

## Package Details

### Simulation Module (`white_elephant.simulation`)

**Purpose:** Simulates a complete White Elephant game with 8 players and 8 gifts.

**Key Features:**
- Randomized gift values (50-90)
- Strategic AI decision-making for steals vs unwraps
- No immediate steal-back rule enforced
- 3-steal lock rule enforced
- Guarantees all players end with exactly one gift
- Guarantees all gifts are opened

**Customization Options:**

**Customization:** You can modify the gift values and steal probabilities by editing `src/white_elephant/simulation.py`:

```python
# Gift values and names
gifts = [
    {"id": 1, "name": "Bluetooth Speaker", "value": 85, ...},
    # Modify values and names as desired
]

# Steal decision thresholds
if best_available["value"] >= 75:  # High value gift
    steal_chance = 0.8  # 80% chance to steal
# Adjust these percentages for more/less aggressive stealing
```

**Output Files:**
- `white_elephant_simulation.png` - Bar charts and final distribution
- `white_elephant_turn_summary.png` - Turn-by-turn compact view
- `game_log.txt` - Text narrative

### Matrix Visualization Module (`white_elephant.matrix`)

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

**Customization:** You can modify fonts, colors, and layout by editing `src/white_elephant/matrix.py`:

```python
# Font sizes
fontsize=28  # For title, actions, turns, legend
fontsize=18  # For gift numbers
fontsize=16  # For owners

# Colors
'#d3d3d3'  # Gray - Wrapped
'#95e1d3'  # Green - Opened (0 steals)
'#a8dadc'  # Light blue - Stolen once
'#ffd93d'  # Yellow - Stolen twice
'#ff6b6b'  # Red - Locked (3 steals)

# Cell dimensions
cell_height = 1.2
cell_width = 2.0
```

**Output Files:**
- `white_elephant_matrix.png` - Complete matrix (can be very tall!)

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

## Troubleshooting

### Common Issues

**"ModuleNotFoundError: No module named 'matplotlib'"**
```bash
pip install -e .
```

Or if you haven't installed the package:
```bash
pip install matplotlib numpy
```

**"FileNotFoundError: game_log.txt not found"**
- Run `white-elephant-sim` first to generate the game log
- If the game log is in a different directory, use `--game-log` option:
  ```bash
  white-elephant-matrix --game-log /path/to/game_log.txt
  ```
- Make sure the file path is correct and accessible

**Matrix image is too large to view**
- The matrix can be very tall (30+ rows)
- Open in an image viewer that supports zooming
- Or use image editing software to view sections
- Consider organizing outputs: `white-elephant-sim -o ./session1 && white-elephant-matrix -o ./session1`

**Text is too small/large**
- Edit the `fontsize` parameters in `src/white_elephant/matrix.py`
- Increase for larger text, decrease for smaller

### Performance Notes

- Simulation runs in < 1 second
- Matrix visualization takes 2-5 seconds depending on game length
- Gift journeys visualization takes 1-2 seconds

## Advanced Usage

### Running Multiple Simulations

To compare different games using output directories:

```bash
# Method 1: Separate directories
white-elephant-sim -o ./game1
white-elephant-matrix -o ./game1

white-elephant-sim -o ./game2  
white-elephant-matrix -o ./game2

# Method 2: Timestamped directories
white-elephant-sim -o "./session-$(date +%H%M)"
white-elephant-matrix -o "./session-$(date +%H%M)"

# Method 3: Sequential in same directory (old approach)
white-elephant-sim
white-elephant-matrix
mv white_elephant_matrix.png game1_matrix.png
mv white_elephant_simulation.png game1_simulation.png
mv game_log.txt game1_log.txt

white-elephant-sim
white-elephant-matrix
# Compare the results
```

### Customizing Gift Values

Edit the `gifts` array in `src/white_elephant/simulation.py`:

```python
gifts = [
    {"id": 1, "name": "Your Gift Name", "value": 75, "steals": 0, "locked": False},
    # Add your 8 gifts here with values 0-100
]
```

### Adjusting Steal Probability

In `src/white_elephant/simulation.py`, modify the steal decision logic:

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

## Development

If you installed with development dependencies (`pip install -e ".[dev]"`), you have access to:

- **black**: Code formatting
- **isort**: Import sorting  
- **flake8**: Code linting
- **pytest**: Testing framework

### Code Formatting
```bash
black src/
isort src/
```

### Linting
```bash
flake8 src/
```

### Building the Package
```bash
pip install build
python -m build
```

## License

These scripts are provided for personal use. Feel free to modify and adapt for your own White Elephant games!

## Support

For issues or questions:
1. Check this README first
2. Review the game rules in `white_elephant_rules.md`
3. Examine the script comments for detailed explanations

Enjoy your White Elephant game! 🎁
