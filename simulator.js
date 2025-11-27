// White Elephant Gift Exchange Simulator in JavaScript
class WhiteElephantSimulator {
    constructor(config = {}) {
        // Apply configuration with defaults
        this.config = {
            numPlayers: config.numPlayers || 8,
            numGifts: config.numGifts || 8,
            lockThreshold: config.lockThreshold || 3,
            highValueThreshold: config.highValueThreshold || 75,
            mediumValueThreshold: config.mediumValueThreshold || 65,
            highStealChance: config.highStealChance !== undefined ? config.highStealChance : 0.8,
            mediumStealChance: config.mediumStealChance !== undefined ? config.mediumStealChance : 0.6,
            lowStealChance: config.lowStealChance !== undefined ? config.lowStealChance : 0.3,
            gifts: config.gifts || null
        };

        // Initialize gifts
        if (this.config.gifts && this.config.gifts.length === this.config.numGifts) {
            this.gifts = this.config.gifts.map((g, idx) => ({
                id: idx + 1,
                name: g.name,
                value: g.value,
                steals: 0,
                locked: false
            }));
        } else {
            this.gifts = this.generateDefaultGifts(this.config.numGifts);
        }

        // Initialize players
        this.players = [];
        for (let i = 1; i <= this.config.numPlayers; i++) {
            this.players.push(`P${i}`);
        }

        this.playerGifts = {};
        this.gameLog = [];
        this.actionStates = [];
        this.availableGiftIds = [];
        this.openedGifts = [];

        this.reset();
    }

    generateDefaultGifts(numGifts) {
        const giftNames = [
            "Bluetooth Speaker", "Luxury Candle Set", "Board Game Collection",
            "Electric Wine Opener", "Cozy Throw Blanket", "Gourmet Coffee Set",
            "Portable Phone Charger", "Kitchen Gadget Bundle", "Wireless Earbuds",
            "Smart LED Bulbs", "Cocktail Shaker Set", "Desk Organizer",
            "Plant Terrarium Kit", "Massage Gun", "Insulated Tumbler",
            "Photo Frame Set", "Scented Bath Bombs", "Puzzle Set",
            "Notebook & Pen Set", "Travel Mug"
        ];

        const gifts = [];
        for (let i = 0; i < numGifts; i++) {
            gifts.push({
                id: i + 1,
                name: giftNames[i % giftNames.length] + (i >= giftNames.length ? ` #${Math.floor(i / giftNames.length) + 1}` : ''),
                value: Math.floor(Math.random() * 50) + 50, // Random value 50-99
                steals: 0,
                locked: false
            });
        }
        return gifts;
    }
    
    reset() {
        // Reset all gifts
        this.gifts.forEach(gift => {
            gift.steals = 0;
            gift.locked = false;
        });

        // Reset player assignments
        this.playerGifts = {};
        this.players.forEach(player => {
            this.playerGifts[player] = null;
        });

        // Reset game state
        this.gameLog = [];
        this.actionStates = [];
        this.availableGiftIds = this.gifts.map(g => g.id);
        this.openedGifts = [];

        // Add initial state
        this.captureGameState("Initial State - All Gifts Wrapped", false);
    }
    
    getGiftById(giftId) {
        return this.gifts.find(g => g.id === giftId);
    }
    
    captureGameState(actionDescription, isTurnStart = false, changedGiftId = null, stealTransition = null) {
        const state = {
            action: actionDescription,
            isTurnStart: isTurnStart,
            changedGiftId: changedGiftId,
            stealTransition: stealTransition, // { from: "Player X", to: "Player Y" }
            gifts: {}
        };

        // Capture state for each gift
        this.gifts.forEach(gift => {
            let owner = null;

            // Find who owns this gift
            for (const [player, playerGift] of Object.entries(this.playerGifts)) {
                if (playerGift && playerGift.id === gift.id) {
                    owner = player;
                    break;
                }
            }

            state.gifts[gift.id] = {
                owner: owner,
                steals: gift.steals,
                locked: gift.locked,
                opened: owner !== null || gift.steals > 0
            };
        });

        this.actionStates.push(state);
        return state;
    }
    
    stealDecision(currentPlayer, availableGiftIds, openedGifts, justStolenGift = null) {
        if (openedGifts.length === 0) {
            return null; // Must pick new gift
        }

        // Find stealable gifts (not locked, not the one they just had stolen)
        const stealable = openedGifts.filter(g =>
            !g.locked &&
            g !== justStolenGift
        );

        if (stealable.length === 0 || availableGiftIds.length === 0) {
            if (stealable.length === 0) {
                return null; // No stealable gifts, must pick new
            }
            // No wrapped gifts left, must steal
            return stealable.reduce((best, current) =>
                current.value > best.value ? current : best
            );
        }

        // Strategy: weighted decision based on gift value
        const bestAvailable = stealable.reduce((best, current) =>
            current.value > best.value ? current : best
        );

        let stealChance;
        if (bestAvailable.value >= this.config.highValueThreshold) {
            stealChance = this.config.highStealChance;
        } else if (bestAvailable.value >= this.config.mediumValueThreshold) {
            stealChance = this.config.mediumStealChance;
        } else {
            stealChance = this.config.lowStealChance;
        }

        if (Math.random() < stealChance) {
            return bestAvailable;
        }
        return null;
    }
    
    executeTurn(playerIndex) {
        const currentPlayer = this.players[playerIndex];
        const turnLog = [];
        
        turnLog.push(`=== ${currentPlayer}'s Turn ===`);
        
        // Capture turn start state
        this.captureGameState(`${currentPlayer} Turn`, true);
        
        let activePlayer = currentPlayer;
        let chainActive = true;
        let justStolenGift = null;
        
        while (chainActive) {
            const stealTarget = this.stealDecision(
                activePlayer, 
                this.availableGiftIds, 
                this.openedGifts, 
                justStolenGift
            );
            
            if (stealTarget === null) {
                // Must pick a new wrapped gift (there's always one available per turn rules)
                const randomIndex = Math.floor(Math.random() * this.availableGiftIds.length);
                const newGiftId = this.availableGiftIds[randomIndex];
                const newGift = this.getGiftById(newGiftId);
                
                // Remove from available and add to opened
                this.availableGiftIds.splice(randomIndex, 1);
                this.openedGifts.push(newGift);
                this.playerGifts[activePlayer] = newGift;
                
                const actionDesc = `${activePlayer} unwraps G${newGiftId}: ${newGift.name}`;
                turnLog.push(`  ${actionDesc}`);
                
                this.captureGameState(actionDesc, false, newGiftId);
                
                // Turn ALWAYS ends when someone opens a wrapped gift
                chainActive = false;
            } else {
                // Execute steal - chain continues with victim unless gift is locked
                const victim = this.executeSteal(activePlayer, stealTarget, turnLog);
                if (victim) {
                    justStolenGift = stealTarget;
                    
                    if (stealTarget.locked) {
                        // Gift is locked, but victim still needs to get a gift
                        // So chain continues with victim having to open a new gift
                        activePlayer = victim;
                        justStolenGift = null; // Reset since locked gift can't be stolen back
                    } else {
                        activePlayer = victim;
                        // Victim must now steal or open - chain continues
                    }
                } else {
                    turnLog.push(`  Error: Could not find victim for ${stealTarget.name}`);
                    chainActive = false;
                }
            }
        }
        
        this.gameLog.push(...turnLog);
        return turnLog;
    }
    
    findGiftOwner(gift) {
        for (const [player, playerGift] of Object.entries(this.playerGifts)) {
            if (playerGift === gift) {
                return player;
            }
        }
        return null;
    }
    
    executeSteal(stealer, targetGift, turnLog) {
        const victim = this.findGiftOwner(targetGift);

        if (victim) {
            // Update steal count and lock status
            targetGift.steals += 1;
            if (targetGift.steals >= this.config.lockThreshold) {
                targetGift.locked = true;
            }

            // Transfer the gift
            this.playerGifts[stealer] = targetGift;
            this.playerGifts[victim] = null;

            const actionDesc = `${stealer} steals G${targetGift.id}: ${targetGift.name} from ${victim}`;
            turnLog.push(`  ${actionDesc}`);

            // Capture state with steal transition info
            const stealTransition = { from: victim, to: stealer };
            this.captureGameState(actionDesc, false, targetGift.id, stealTransition);

            if (targetGift.locked) {
                turnLog.push(`    G${targetGift.id} is now LOCKED (${this.config.lockThreshold} steals)`);
            }

            return victim; // Return the victim who now needs a gift
        }
        return null;
    }
    
    runFullSimulation() {
        this.reset();

        // Execute all player turns
        for (let i = 0; i < this.config.numPlayers; i++) {
            this.executeTurn(i);
        }
        
        // Final state - first add a turn-like separator, then the actual final state
        this.captureGameState("Final State", true);  // Blank separator row
        this.captureGameState("", false);  // Final state with empty action text
        
        return this.validateAndAnalyze();
    }
    
    validateAndAnalyze() {
        // Validation
        const playersWithoutGifts = this.players.filter(p => this.playerGifts[p] === null);
        const unopenedGifts = this.gifts.filter(g => this.availableGiftIds.includes(g.id));
        
        // Statistics
        const totalSteals = this.gifts.reduce((sum, g) => sum + g.steals, 0);
        const lockedGifts = this.gifts.filter(g => g.locked).length;
        const mostStolenGift = this.gifts.reduce((most, current) => 
            current.steals > most.steals ? current : most
        );
        
        return {
            valid: playersWithoutGifts.length === 0 && unopenedGifts.length === 0,
            playersWithoutGifts,
            unopenedGifts,
            stats: {
                totalActions: this.actionStates.length - 1, // Subtract initial state
                totalSteals,
                lockedGifts,
                mostStolenGift: mostStolenGift.steals > 0 ? 
                    `G${mostStolenGift.id} (${mostStolenGift.steals}x)` : 'None'
            }
        };
    }
}

// UI Controller
class UIController {
    constructor() {
        this.currentStateIndex = 0;
        this.isAutoPlaying = false;
        this.autoPlayInterval = null;

        this.initializeElements();
        this.bindEvents();
        this.initializeConfiguration();

        // Create simulator with default configuration
        this.simulator = new WhiteElephantSimulator(this.getConfiguration());

        this.clearVisualizationContents();
        this.updateMatrix();
    }

    initializeElements() {
        this.simulateBtn = document.getElementById('simulateBtn');
        this.stepBtn = document.getElementById('stepBtn');
        this.autoPlayBtn = document.getElementById('autoPlayBtn');
        this.resetBtn = document.getElementById('resetBtn');
        this.gameLog = document.getElementById('gameLog');
        this.matrixBody = document.getElementById('matrixBody');
        this.stats = document.getElementById('stats');
        this.totalActions = document.getElementById('totalActions');
        this.totalSteals = document.getElementById('totalSteals');
        this.lockedGifts = document.getElementById('lockedGifts');
        this.mostStolen = document.getElementById('mostStolen');
        this.visualizationPanel = document.getElementById('visualizationPanel');
        this.giftMovementContainer = document.getElementById('giftMovementContainer');
        this.movementTab = document.getElementById('movementTab');
        this.matrixTab = document.getElementById('matrixTab');
        this.movementTabContent = document.getElementById('movementTabContent');
        this.matrixTabContent = document.getElementById('matrixTabContent');

        // Configuration elements
        this.configBtn = document.getElementById('configBtn');
        this.closeConfigBtn = document.getElementById('closeConfigBtn');
        this.configPanel = document.getElementById('configPanel');
        this.numPlayers = document.getElementById('numPlayers');
        this.lockThreshold = document.getElementById('lockThreshold');
        this.autoPlaySpeed = document.getElementById('autoPlaySpeed');
        this.highValueThreshold = document.getElementById('highValueThreshold');
        this.mediumValueThreshold = document.getElementById('mediumValueThreshold');
        this.highStealChance = document.getElementById('highStealChance');
        this.mediumStealChance = document.getElementById('mediumStealChance');
        this.lowStealChance = document.getElementById('lowStealChance');
        this.generateGiftsBtn = document.getElementById('generateGiftsBtn');
        this.giftsList = document.getElementById('giftsList');
    }
    
    bindEvents() {
        this.simulateBtn.addEventListener('click', () => this.runSimulation());
        this.stepBtn.addEventListener('click', () => this.stepForward());
        this.autoPlayBtn.addEventListener('click', () => this.toggleAutoPlay());
        this.resetBtn.addEventListener('click', () => this.reset());
        this.movementTab.addEventListener('click', () => this.switchTab('movement'));
        this.matrixTab.addEventListener('click', () => this.switchTab('matrix'));
        window.addEventListener('resize', () => this.handleResize());

        // Configuration events
        this.configBtn.addEventListener('click', () => this.toggleConfiguration());
        this.closeConfigBtn.addEventListener('click', () => this.toggleConfiguration());
        this.generateGiftsBtn.addEventListener('click', () => this.generateRandomGifts());
        this.numPlayers.addEventListener('change', () => this.updateGiftsList());
    }
    
    runSimulation() {
        // Recreate simulator with current configuration
        this.simulator = new WhiteElephantSimulator(this.getConfiguration());

        const result = this.simulator.runFullSimulation();
        this.currentStateIndex = 0;

        this.updateGameLog(result);
        this.initializeGiftMovementView();
        this.updateMatrix();
        this.updateGiftMovementView();
        this.updateStats(result.stats);

        this.simulateBtn.disabled = true;
        this.stepBtn.disabled = false;
        this.autoPlayBtn.disabled = false;

        this.stats.classList.remove('hidden');
    }
    
    stepForward() {
        if (this.currentStateIndex < this.simulator.actionStates.length - 1) {
            this.currentStateIndex++;
            this.updateMatrix();
            this.updateGiftMovementView();
            this.scrollMatrixToBottom();
        }
        
        if (this.currentStateIndex >= this.simulator.actionStates.length - 1) {
            this.stepBtn.disabled = true;
            this.stopAutoPlay();
        }
    }
    
    toggleAutoPlay() {
        if (this.isAutoPlaying) {
            this.stopAutoPlay();
        } else {
            this.startAutoPlay();
        }
    }
    
    startAutoPlay() {
        this.isAutoPlaying = true;
        this.autoPlayBtn.textContent = '⏸️  Pause';
        this.stepBtn.disabled = true;

        const speed = parseInt(this.autoPlaySpeed.value) || 150;
        this.autoPlayInterval = setInterval(() => {
            this.stepForward();
        }, speed);
    }
    
    stopAutoPlay() {
        this.isAutoPlaying = false;
        this.autoPlayBtn.textContent = '▶️  Auto Play';
        this.stepBtn.disabled = this.currentStateIndex >= this.simulator.actionStates.length - 1;
        
        if (this.autoPlayInterval) {
            clearInterval(this.autoPlayInterval);
            this.autoPlayInterval = null;
        }
    }
    
    reset() {
        this.stopAutoPlay();

        // Recreate simulator with current configuration
        this.simulator = new WhiteElephantSimulator(this.getConfiguration());

        this.currentStateIndex = 0;

        this.simulateBtn.disabled = false;
        this.stepBtn.disabled = true;
        this.autoPlayBtn.disabled = true;
        this.autoPlayBtn.textContent = '▶️  Auto Play';

        this.gameLog.innerHTML = `
            <div style="text-align: center; margin-top: 150px; color: #7f8c8d;">
                Click "Run New Simulation" to start a White Elephant game!
            </div>
        `;

        this.stats.classList.add('hidden');
        this.clearVisualizationContents();
        this.updateMatrix();
    }
    
    updateGameLog(result) {
        let html = '';
        
        this.simulator.gameLog.forEach(line => {
            if (line.includes('=== ') && line.includes('Turn ===')) {
                html += `<div class="turn-start">🎯 ${line}</div>`;
            } else if (line.trim().startsWith('Error:')) {
                html += `<div class="error">❌ ${line}</div>`;
            } else if (line.includes('unwraps')) {
                html += `<div class="action">🎁 ${line}</div>`;
            } else if (line.includes('steals')) {
                html += `<div class="action">🔄 ${line}</div>`;
            } else if (line.includes('LOCKED')) {
                html += `<div class="action">🔒 ${line}</div>`;
            } else if (line.trim() !== '') {
                html += `<div class="action">• ${line}</div>`;
            }
        });
        
        // Add validation results
        html += '<div class="validation">📊 === GAME VALIDATION ===</div>';
        if (result.valid) {
            html += '<div class="validation">🎉 GAME COMPLETED SUCCESSFULLY! 🎉</div>';
            html += '<div class="validation">✅ All 8 players have gifts</div>';
            html += '<div class="validation">✅ All 8 gifts were opened</div>';
            html += '<div class="validation">✅ Game rules properly enforced</div>';
        } else {
            html += '<div class="error">⚠️ GAME VALIDATION FAILED ⚠️</div>';
            if (result.playersWithoutGifts.length > 0) {
                html += `<div class="error">❌ Players without gifts (${result.playersWithoutGifts.length}): ${result.playersWithoutGifts.join(', ')}</div>`;
            }
            if (result.unopenedGifts.length > 0) {
                html += `<div class="error">❌ Unopened gifts (${result.unopenedGifts.length}): ${result.unopenedGifts.map(g => g.name).join(', ')}</div>`;
            }
        }
        
        // Add final results
        html += '<div class="final-results">🏆 === FINAL RESULTS ===</div>';
        this.simulator.players.forEach(player => {
            const gift = this.simulator.playerGifts[player];
            if (gift) {
                const status = gift.locked ? 'LOCKED' : 'Available';
                const icon = gift.locked ? '🔒' : '🎁';
                html += `<div class="final-results">${icon} ${player}: ${gift.name} (value: ${gift.value}, stolen: ${gift.steals}x, ${status})</div>`;
            }
        });
        
        this.gameLog.innerHTML = html;
        this.gameLog.scrollTop = this.gameLog.scrollHeight;
    }
    
    updateMatrix() {
        // Update table headers dynamically
        const matrixTable = document.getElementById('matrixTable');
        const thead = matrixTable.querySelector('thead tr');
        thead.innerHTML = '<th style="min-width: 200px;">Action</th>';

        this.simulator.gifts.forEach(gift => {
            const th = document.createElement('th');
            th.textContent = `G${gift.id}`;
            thead.appendChild(th);
        });

        const tbody = this.matrixBody;
        tbody.innerHTML = '';

        // Show states up to current index
        for (let i = 0; i <= this.currentStateIndex; i++) {
            const state = this.simulator.actionStates[i];
            const row = document.createElement('tr');

            // Action cell
            const actionCell = document.createElement('td');
            actionCell.className = 'action-cell';
            if (state.isTurnStart) {
                actionCell.classList.add('turn-start');
            }
            actionCell.textContent = state.action;
            row.appendChild(actionCell);

            // Gift cells - only if not a turn start
            if (!state.isTurnStart) {
                this.simulator.gifts.forEach(gift => {
                    const giftId = gift.id;
                    const cell = document.createElement('td');
                    cell.className = 'gift-cell';

                    const giftState = state.gifts[giftId];

                    // Determine cell class based on state
                    if (!giftState.owner) {
                        cell.classList.add('gift-wrapped');
                    } else if (giftState.locked) {
                        cell.classList.add('gift-locked');
                    } else if (giftState.steals === 2) {
                        cell.classList.add('gift-stolen-twice');
                    } else if (giftState.steals === 1) {
                        cell.classList.add('gift-stolen-once');
                    } else {
                        cell.classList.add('gift-opened');
                    }

                    // Always highlight if this gift changed in this action
                    if (state.changedGiftId === giftId) {
                        cell.classList.add('gift-highlighted');
                    }

                    // Gift number
                    const giftNumber = document.createElement('div');
                    giftNumber.className = 'gift-number';
                    giftNumber.textContent = `G${giftId}`;
                    cell.appendChild(giftNumber);

                    // Owner - show steal transition if this is a steal action for this gift
                    const owner = document.createElement('div');
                    owner.className = 'gift-owner';

                    if (state.stealTransition && state.changedGiftId === giftId) {
                        // Show steal transition: P5 → P2 (already in PN format from players array)
                        const fromPlayer = state.stealTransition.from;
                        const toPlayer = state.stealTransition.to;
                        owner.textContent = `${fromPlayer} → ${toPlayer}`;
                    } else {
                        // Show normal owner (already in PN format)
                        owner.textContent = giftState.owner ? giftState.owner : '—';
                    }
                    cell.appendChild(owner);

                    // Steal count
                    if (giftState.steals > 0) {
                        const steals = document.createElement('div');
                        steals.className = 'gift-steals';
                        if (giftState.locked) {
                            steals.classList.add('locked');
                        }
                        steals.textContent = `×${giftState.steals}`;
                        cell.appendChild(steals);
                    }

                    row.appendChild(cell);
                });
            } else {
                // For turn start rows, create one cell that spans all gift columns
                const turnCell = document.createElement('td');
                turnCell.colSpan = this.simulator.gifts.length;
                turnCell.className = 'turn-start';
                turnCell.textContent = ''; // Empty content since action already shows the turn
                row.appendChild(turnCell);
            }

            tbody.appendChild(row);
        }
    }
    
    updateStats(stats) {
        this.totalActions.textContent = stats.totalActions;
        this.totalSteals.textContent = stats.totalSteals;
        this.lockedGifts.textContent = stats.lockedGifts;
        this.mostStolen.textContent = stats.mostStolenGift;
    }
    
    scrollMatrixToBottom() {
        const container = document.getElementById('matrixContainer');
        setTimeout(() => {
            container.scrollTop = container.scrollHeight;
        }, 100);
    }
    
    initializeGiftMovementView() {
        this.giftMovementContainer.innerHTML = '';

        // Create header with player names
        const header = document.createElement('div');
        header.className = 'movement-header';

        this.simulator.players.forEach(player => {
            const playerCell = document.createElement('div');
            playerCell.className = 'player-header-cell';
            playerCell.textContent = player;
            header.appendChild(playerCell);
        });

        this.giftMovementContainer.appendChild(header);
        
        // Create container for rows
        const rowsContainer = document.createElement('div');
        rowsContainer.className = 'movement-rows';
        rowsContainer.id = 'movementRows';
        
        // Create SVG for arrows
        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.id = 'movementArrowSvg';
        svg.setAttribute('class', 'movement-arrow-svg');
        
        // Add arrow marker definition
        const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
        const marker = document.createElementNS('http://www.w3.org/2000/svg', 'marker');
        marker.id = 'arrowhead';
        marker.setAttribute('markerWidth', '8');
        marker.setAttribute('markerHeight', '6');
        marker.setAttribute('refX', '7');
        marker.setAttribute('refY', '3');
        marker.setAttribute('orient', 'auto');
        
        const polygon = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
        polygon.setAttribute('points', '0 0, 8 3, 0 6');
        polygon.setAttribute('fill', '#c9182c');
        
        marker.appendChild(polygon);
        defs.appendChild(marker);
        svg.appendChild(defs);
        
        rowsContainer.appendChild(svg);
        this.giftMovementContainer.appendChild(rowsContainer);
    }
    
    updateGiftMovementView() {
        const rowsContainer = document.getElementById('movementRows');
        const svg = document.getElementById('movementArrowSvg');
        
        if (!rowsContainer || !svg) return;
        
        // Clear existing rows and separators (except SVG)
        const existingRows = rowsContainer.querySelectorAll('.movement-row, .turn-separator');
        existingRows.forEach(row => row.remove());
        
        // Show states up to current index
        for (let i = 0; i <= this.currentStateIndex; i++) {
            const state = this.simulator.actionStates[i];
            
            // Add turn separator for turn start states
            if (state.isTurnStart) {
                this.createTurnSeparator(state.action);
                continue;
            }
            
            this.createMovementRow(state, i);
        }
        
        // Create arrows for all steal transitions up to current state
        this.createAllStealArrows();
    }
    
    createMovementRow(state, stateIndex) {
        const rowsContainer = document.getElementById('movementRows');
        const svg = document.getElementById('movementArrowSvg');

        const row = document.createElement('div');
        row.className = 'movement-row';
        row.id = `movement-row-${stateIndex}`;

        // Action label
        const actionLabel = document.createElement('div');
        actionLabel.className = 'action-label';
        actionLabel.textContent = this.getActionDescription(state.action);
        row.appendChild(actionLabel);

        // Gift positions container
        const positions = document.createElement('div');
        positions.className = 'gift-positions';

        // Create position cells (one for each player)
        this.simulator.players.forEach((player, playerIndex) => {
            const cell = document.createElement('div');
            cell.className = 'position-cell';
            cell.id = `row-${stateIndex}-player-${playerIndex + 1}`;

            // Find all gifts owned by this player in this state
            const playerGifts = [];
            this.simulator.gifts.forEach(gift => {
                const giftState = state.gifts[gift.id];
                if (giftState.owner === player) {
                    playerGifts.push({ id: gift.id, ...giftState });
                }
            });

            // Add gift tokens for this player
            playerGifts.forEach(gift => {
                const token = document.createElement('div');
                token.className = 'gift-token';
                token.id = `row-${stateIndex}-gift-${gift.id}`;
                token.textContent = `G${gift.id}`;

                // Apply styling based on steal count
                if (gift.locked) {
                    token.classList.add('locked');
                } else if (gift.steals === 2) {
                    token.classList.add('stolen-twice');
                } else if (gift.steals === 1) {
                    token.classList.add('stolen-once');
                }

                // Highlight if this is the changed gift
                if (state.changedGiftId === gift.id) {
                    token.classList.add('highlighted');
                }

                cell.appendChild(token);
            });

            positions.appendChild(cell);
        });

        row.appendChild(positions);

        // Insert before the SVG
        rowsContainer.insertBefore(row, svg);
    }
    
    createTurnSeparator(actionText) {
        const rowsContainer = document.getElementById('movementRows');
        const svg = document.getElementById('movementArrowSvg');
        
        const separator = document.createElement('div');
        separator.className = 'turn-separator';
        
        // Insert before the SVG
        rowsContainer.insertBefore(separator, svg);
    }
    
    createAllStealArrows() {
        const svg = document.getElementById('movementArrowSvg');
        const rowsContainer = document.getElementById('movementRows');
        
        // Clear existing arrows
        const existingArrows = svg.querySelectorAll('.steal-arrow, .arrow-label');
        existingArrows.forEach(arrow => arrow.remove());
        
        // Create arrows for all steal transitions up to current state
        setTimeout(() => {
            for (let i = 1; i <= this.currentStateIndex; i++) {
                const state = this.simulator.actionStates[i];
                
                if (state.stealTransition && state.changedGiftId && !state.isTurnStart) {
                    this.createStealArrowForState(state, i);
                }
            }
        }, 150);
    }
    
    createStealArrowForState(state, stateIndex) {
        const svg = document.getElementById('movementArrowSvg');
        const rowsContainer = document.getElementById('movementRows');
        const fromPlayerNum = parseInt(state.stealTransition.from.replace('P', ''));
        const toPlayerNum = parseInt(state.stealTransition.to.replace('P', ''));
        const giftId = state.changedGiftId;
        
        try {
            const containerRect = rowsContainer.getBoundingClientRect();
            
            // Find the previous action's row (the row before this steal)
            let previousActionIndex = stateIndex - 1;
            while (previousActionIndex >= 0 && this.simulator.actionStates[previousActionIndex].isTurnStart) {
                previousActionIndex--;
            }
            
            if (previousActionIndex < 0) return;
            
            // Get the rows
            const currentRow = document.getElementById(`movement-row-${stateIndex}`);
            const previousRow = document.getElementById(`movement-row-${previousActionIndex}`);
            
            if (!currentRow || !previousRow) return;
            
            // Get position of gift in previous row
            const fromCell = previousRow.querySelector(`#row-${previousActionIndex}-player-${fromPlayerNum}`);
            const fromToken = fromCell ? fromCell.querySelector(`[id*="gift-${giftId}"]`) : null;
            
            // Get position of gift in current row
            const toCell = currentRow.querySelector(`#row-${stateIndex}-player-${toPlayerNum}`);
            const toToken = toCell ? toCell.querySelector(`[id*="gift-${giftId}"]`) : null;
            
            if (!fromToken || !toToken) return;
            
            const fromRect = fromToken.getBoundingClientRect();
            const toRect = toToken.getBoundingClientRect();
            
            // Calculate centers
            const fromCenterX = fromRect.left - containerRect.left + fromRect.width / 2;
            const fromCenterY = fromRect.top - containerRect.top + fromRect.height / 2;
            const toCenterX = toRect.left - containerRect.left + toRect.width / 2;
            const toCenterY = toRect.top - containerRect.top + toRect.height / 2;
            
            // Calculate arrow direction and shorten by moving endpoints inward
            const dx = toCenterX - fromCenterX;
            const dy = toCenterY - fromCenterY;
            const length = Math.sqrt(dx * dx + dy * dy);
            
            if (length === 0) return; // Same position, no arrow needed
            
            // Shorten arrow by 20 pixels on each end
            const shortenBy = 20;
            const unitX = dx / length;
            const unitY = dy / length;
            
            const fromX = fromCenterX + unitX * shortenBy;
            const fromY = fromCenterY + unitY * shortenBy;
            const toX = toCenterX - unitX * shortenBy;
            const toY = toCenterY - unitY * shortenBy;
            
            // Create straight arrow path
            const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
            const pathData = `M ${fromX} ${fromY} L ${toX} ${toY}`;
            
            path.setAttribute('d', pathData);
            path.setAttribute('class', 'steal-arrow');
            path.setAttribute('data-state', stateIndex);
            
            svg.appendChild(path);
            
            // Add label at the midpoint of the shortened arrow
            const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            text.setAttribute('x', (fromX + toX) / 2 + 8);
            text.setAttribute('y', (fromY + toY) / 2 - 2);
            text.setAttribute('class', 'arrow-label');
            text.setAttribute('data-state', stateIndex);
            text.textContent = `G${giftId}`;
            
            svg.appendChild(text);
        } catch (error) {
            console.warn('Error creating steal arrow for state', stateIndex, ':', error);
        }
    }
    
    getRowIndexFromId(rowId) {
        return parseInt(rowId.replace('movement-row-', ''));
    }
    
    getActionDescription(actionText) {
        if (!actionText || actionText === '') return '';
        
        if (actionText.includes('unwraps')) {
            // Extract player and gift info
            const match = actionText.match(/(\w+) unwraps (G\d+)/);
            if (match) {
                return `${match[1]} opens ${match[2]}`;
            }
        } else if (actionText.includes('steals')) {
            // Extract stealer and gift info
            const match = actionText.match(/(\w+) steals (G\d+)/);
            if (match) {
                return `${match[1]} steals ${match[2]}`;
            }
        } else if (actionText.includes('Initial State')) {
            return 'Start';
        }
        
        // Fallback: return first few words
        return actionText.split(' ').slice(0, 2).join(' ');
    }
    
    switchTab(tabName) {
        // Remove active class from all tabs and content
        this.movementTab.classList.remove('active');
        this.matrixTab.classList.remove('active');
        this.movementTabContent.classList.remove('active');
        this.matrixTabContent.classList.remove('active');
        
        // Add active class to selected tab and content
        if (tabName === 'movement') {
            this.movementTab.classList.add('active');
            this.movementTabContent.classList.add('active');
        } else if (tabName === 'matrix') {
            this.matrixTab.classList.add('active');
            this.matrixTabContent.classList.add('active');
        }
    }
    
    clearVisualizationContents() {
        // Clear movement visualization
        if (this.giftMovementContainer) {
            this.giftMovementContainer.innerHTML = `
                <div style="text-align: center; margin-top: 100px; color: #7f8c8d; font-size: 1.1rem;">
                    🎁 Click "Run New Simulation" to see gift movements!
                </div>
            `;
        }

        // Clear matrix content (matrix body will be cleared by updateMatrix)
        const matrixBody = document.getElementById('matrixBody');
        if (matrixBody) {
            matrixBody.innerHTML = `
                <tr>
                    <td colspan="9" style="text-align: center; padding: 40px; color: #7f8c8d; font-size: 1.1rem;">
                        📋 Matrix will appear here after running a simulation
                    </td>
                </tr>
            `;
        }
    }

    // Configuration methods
    initializeConfiguration() {
        // Start with configuration hidden
        this.configPanel.classList.remove('visible');

        // Initialize gifts list with default 8 gifts
        this.updateGiftsList();
    }

    toggleConfiguration() {
        this.configPanel.classList.toggle('visible');
    }

    getConfiguration() {
        const numPlayers = parseInt(this.numPlayers.value) || 8;

        // Read gifts from the gifts list
        const giftInputs = this.giftsList.querySelectorAll('.gift-item');
        const gifts = [];
        giftInputs.forEach((item, index) => {
            const nameInput = item.querySelector('input[type="text"]');
            const valueInput = item.querySelector('input[type="number"]');
            if (nameInput && valueInput) {
                gifts.push({
                    name: nameInput.value || `Gift ${index + 1}`,
                    value: parseInt(valueInput.value) || 50
                });
            }
        });

        return {
            numPlayers: numPlayers,
            numGifts: numPlayers, // Always equal to number of players
            lockThreshold: parseInt(this.lockThreshold.value) || 3,
            highValueThreshold: parseInt(this.highValueThreshold.value) || 75,
            mediumValueThreshold: parseInt(this.mediumValueThreshold.value) || 65,
            highStealChance: parseFloat(this.highStealChance.value) || 0.8,
            mediumStealChance: parseFloat(this.mediumStealChance.value) || 0.6,
            lowStealChance: parseFloat(this.lowStealChance.value) || 0.3,
            gifts: gifts.length === numPlayers ? gifts : null
        };
    }

    updateGiftsList() {
        const numPlayers = parseInt(this.numPlayers.value) || 8;

        // Get existing gift values if any
        const existingGifts = [];
        const giftInputs = this.giftsList.querySelectorAll('.gift-item');
        giftInputs.forEach(item => {
            const nameInput = item.querySelector('input[type="text"]');
            const valueInput = item.querySelector('input[type="number"]');
            if (nameInput && valueInput) {
                existingGifts.push({
                    name: nameInput.value,
                    value: parseInt(valueInput.value)
                });
            }
        });

        // Clear and repopulate
        this.giftsList.innerHTML = '';

        // Create default gift names
        const defaultGiftNames = [
            "Bluetooth Speaker", "Luxury Candle Set", "Board Game Collection",
            "Electric Wine Opener", "Cozy Throw Blanket", "Gourmet Coffee Set",
            "Portable Phone Charger", "Kitchen Gadget Bundle", "Wireless Earbuds",
            "Smart LED Bulbs", "Cocktail Shaker Set", "Desk Organizer",
            "Plant Terrarium Kit", "Massage Gun", "Insulated Tumbler",
            "Photo Frame Set", "Scented Bath Bombs", "Puzzle Set",
            "Notebook & Pen Set", "Travel Mug"
        ];

        for (let i = 0; i < numPlayers; i++) {
            const giftItem = document.createElement('div');
            giftItem.className = 'gift-item';

            const name = existingGifts[i]?.name || defaultGiftNames[i % defaultGiftNames.length];
            const value = existingGifts[i]?.value || (Math.floor(Math.random() * 50) + 50);

            giftItem.innerHTML = `
                <input type="text" placeholder="Gift Name" value="${name}">
                <input type="number" placeholder="Value" min="1" max="1000" value="${value}">
                <span style="color: #666; font-size: 0.8rem;">G${i + 1}</span>
            `;

            this.giftsList.appendChild(giftItem);
        }
    }

    generateRandomGifts() {
        const numPlayers = parseInt(this.numPlayers.value) || 8;

        // Clear and repopulate with random values
        this.giftsList.innerHTML = '';

        const defaultGiftNames = [
            "Bluetooth Speaker", "Luxury Candle Set", "Board Game Collection",
            "Electric Wine Opener", "Cozy Throw Blanket", "Gourmet Coffee Set",
            "Portable Phone Charger", "Kitchen Gadget Bundle", "Wireless Earbuds",
            "Smart LED Bulbs", "Cocktail Shaker Set", "Desk Organizer",
            "Plant Terrarium Kit", "Massage Gun", "Insulated Tumbler",
            "Photo Frame Set", "Scented Bath Bombs", "Puzzle Set",
            "Notebook & Pen Set", "Travel Mug"
        ];

        for (let i = 0; i < numPlayers; i++) {
            const giftItem = document.createElement('div');
            giftItem.className = 'gift-item';

            const name = defaultGiftNames[i % defaultGiftNames.length] + (i >= defaultGiftNames.length ? ` #${Math.floor(i / defaultGiftNames.length) + 1}` : '');
            const value = Math.floor(Math.random() * 50) + 50; // Random value 50-99

            giftItem.innerHTML = `
                <input type="text" placeholder="Gift Name" value="${name}">
                <input type="number" placeholder="Value" min="1" max="1000" value="${value}">
                <span style="color: #666; font-size: 0.8rem;">G${i + 1}</span>
            `;

            this.giftsList.appendChild(giftItem);
        }
    }
    
    handleResize() {
        // Only redraw arrows if we have simulation data and are on the movement tab
        if (this.simulator.actionStates.length > 0 && this.movementTabContent.classList.contains('active')) {
            // Use timeout to allow DOM to settle after resize
            clearTimeout(this.resizeTimeout);
            this.resizeTimeout = setTimeout(() => {
                this.createAllStealArrows();
            }, 100);
        }
    }
}

// Initialize the application when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new UIController();
});