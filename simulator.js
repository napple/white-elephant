// White Elephant Gift Exchange Simulator in JavaScript
class WhiteElephantSimulator {
    constructor() {
        this.gifts = [
            { id: 1, name: "Bluetooth Speaker", value: 85, steals: 0, locked: false },
            { id: 2, name: "Luxury Candle Set", value: 60, steals: 0, locked: false },
            { id: 3, name: "Board Game Collection", value: 75, steals: 0, locked: false },
            { id: 4, name: "Electric Wine Opener", value: 50, steals: 0, locked: false },
            { id: 5, name: "Cozy Throw Blanket", value: 70, steals: 0, locked: false },
            { id: 6, name: "Gourmet Coffee Set", value: 55, steals: 0, locked: false },
            { id: 7, name: "Portable Phone Charger", value: 90, steals: 0, locked: false },
            { id: 8, name: "Kitchen Gadget Bundle", value: 65, steals: 0, locked: false },
        ];
        
        this.players = [];
        for (let i = 1; i <= 8; i++) {
            this.players.push(`P${i}`);
        }
        
        this.playerGifts = {};
        this.gameLog = [];
        this.actionStates = [];
        this.availableGiftIds = [];
        this.openedGifts = [];
        
        this.reset();
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
        this.availableGiftIds = [1, 2, 3, 4, 5, 6, 7, 8];
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
        for (let i = 1; i <= 8; i++) {
            const gift = this.getGiftById(i);
            let owner = null;
            
            // Find who owns this gift
            for (const [player, playerGift] of Object.entries(this.playerGifts)) {
                if (playerGift && playerGift.id === i) {
                    owner = player;
                    break;
                }
            }
            
            state.gifts[i] = {
                owner: owner,
                steals: gift.steals,
                locked: gift.locked,
                opened: owner !== null || gift.steals > 0
            };
        }
        
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
        if (bestAvailable.value >= 75) {
            stealChance = 0.8; // 80% chance for high value
        } else if (bestAvailable.value >= 65) {
            stealChance = 0.6; // 60% chance for medium-high value
        } else {
            stealChance = 0.3; // 30% chance for lower value
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
            if (targetGift.steals >= 3) {
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
                turnLog.push(`    G${targetGift.id} is now LOCKED (3 steals)`);
            }
            
            return victim; // Return the victim who now needs a gift
        }
        return null;
    }
    
    runFullSimulation() {
        this.reset();
        
        // Execute all 8 turns
        for (let i = 0; i < 8; i++) {
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
        this.simulator = new WhiteElephantSimulator();
        this.currentStateIndex = 0;
        this.isAutoPlaying = false;
        this.autoPlayInterval = null;
        
        this.initializeElements();
        this.bindEvents();
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
    }
    
    bindEvents() {
        this.simulateBtn.addEventListener('click', () => this.runSimulation());
        this.stepBtn.addEventListener('click', () => this.stepForward());
        this.autoPlayBtn.addEventListener('click', () => this.toggleAutoPlay());
        this.resetBtn.addEventListener('click', () => this.reset());
    }
    
    runSimulation() {
        const result = this.simulator.runFullSimulation();
        this.currentStateIndex = 0;
        
        this.updateGameLog(result);
        this.updateMatrix();
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
        
        this.autoPlayInterval = setInterval(() => {
            this.stepForward();
        }, 150);
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
        this.simulator.reset();
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
                for (let giftId = 1; giftId <= 8; giftId++) {
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
                }
            } else {
                // For turn start rows, create one cell that spans all gift columns
                const turnCell = document.createElement('td');
                turnCell.colSpan = 8;
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
}

// Initialize the application when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new UIController();
});