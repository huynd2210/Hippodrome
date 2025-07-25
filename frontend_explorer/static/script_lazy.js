// Lazy-Loading Hippodrome Solution Explorer - Optimized JavaScript
class LazyHippodromeExplorer {
    constructor() {
        this.currentSolution = null;
        this.currentStep = 0;
        this.isPlaying = false;
        this.playbackTimer = null;
        this.playbackSpeed = 1000;
        
        // Target-related state
        this.availableTargets = [];
        this.currentTarget = 'top-row'; // Default
        this.statsLoaded = false;
        
        // Editor state
        this.editMode = false;
        this.selectedPiece = 'K';
        this.editorBoardState = 'xxxxxxxxxxxxxxxx';
        
        this.initializeElements();
        this.bindEventListeners();
        this.initializeBoard();
        // DO NOT load targets automatically - wait for user click
        
        this.updateSpeed();
    }

    initializeElements() {
        // Board
        this.board = document.getElementById('chess-board');
        
        // Target elements
        this.loadTargetsBtn = document.getElementById('load-targets-btn');
        this.targetsLoadingArea = document.getElementById('targets-loading-area');
        this.targetsLoadedArea = document.getElementById('targets-loaded-area');
        this.targetDropdown = document.getElementById('target-dropdown');
        this.targetDescription = document.getElementById('target-description');
        this.targetPositionsDisplay = document.getElementById('target-positions-display');
        this.targetSolutionsCount = document.getElementById('target-solutions-count');
        this.positionsGuide = document.getElementById('positions-guide');
        this.statsTargetInfo = document.getElementById('stats-target-info');
        
        // Controls
        this.playPauseBtn = document.getElementById('play-pause-btn');
        this.prevBtn = document.getElementById('prev-btn');
        this.nextBtn = document.getElementById('next-btn');
        this.firstBtn = document.getElementById('first-btn');
        this.lastBtn = document.getElementById('last-btn');
        this.speedSlider = document.getElementById('speed-slider');
        this.speedDisplay = document.getElementById('speed-display');
        this.progressFill = document.getElementById('progress-fill');
        
        // Search elements
        this.configIdInput = document.getElementById('config-id');
        this.searchBtn = document.getElementById('search-btn');
        this.randomBtn = document.getElementById('random-btn');
        
        // Editor elements
        this.editModeBtn = document.getElementById('edit-mode-btn');
        this.piecePalette = document.getElementById('piece-palette');
        this.pieceBtns = document.querySelectorAll('.piece-btn');
        this.clearBoardBtn = document.getElementById('clear-board-btn');
        this.searchBoardBtn = document.getElementById('search-board-btn');
        this.exitEditBtn = document.getElementById('exit-edit-btn');
        this.playbackSection = document.getElementById('playback-section');
        this.boardTitle = document.getElementById('board-title');
        this.boardModeIndicator = document.getElementById('board-mode-indicator');
        
        // Info displays
        this.currentId = document.getElementById('current-id');
        this.currentTargetDisplay = document.getElementById('current-target');
        this.currentMoves = document.getElementById('current-moves');
        this.currentStepDisplay = document.getElementById('current-step');
        this.statsContent = document.getElementById('stats-content');
        
        // Overlays
        this.loadingOverlay = document.getElementById('loading-overlay');
        this.errorMessage = document.getElementById('error-message');
        this.errorText = document.getElementById('error-text');
        this.closeError = document.getElementById('close-error');
    }

    bindEventListeners() {
        // Load targets button
        this.loadTargetsBtn.addEventListener('click', () => this.loadTargets());
        
        // Target selection
        this.targetDropdown.addEventListener('change', () => this.onTargetChange());
        
        // Playback controls
        this.playPauseBtn.addEventListener('click', () => this.togglePlayback());
        this.prevBtn.addEventListener('click', () => this.previousStep());
        this.nextBtn.addEventListener('click', () => this.nextStep());
        this.firstBtn.addEventListener('click', () => this.goToFirstStep());
        this.lastBtn.addEventListener('click', () => this.goToLastStep());
        
        // Speed control
        this.speedSlider.addEventListener('input', () => this.updateSpeed());
        
        // Search controls
        this.searchBtn.addEventListener('click', () => this.searchById());
        this.configIdInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.searchById();
        });
        this.randomBtn.addEventListener('click', () => this.loadRandomSolution());
        
        // Editor controls
        this.editModeBtn.addEventListener('click', () => this.toggleEditMode());
        this.exitEditBtn.addEventListener('click', () => this.exitEditMode());
        this.clearBoardBtn.addEventListener('click', () => this.clearBoard());
        this.searchBoardBtn.addEventListener('click', () => this.searchByBoard());
        
        // Piece selection
        this.pieceBtns.forEach(btn => {
            btn.addEventListener('click', () => this.selectPiece(btn.dataset.piece));
        });
        
        // Error handling
        this.closeError.addEventListener('click', () => this.hideError());
    }

    async loadTargets() {
        // Show loading state
        this.loadTargetsBtn.textContent = '🔄 Loading Targets...';
        this.loadTargetsBtn.disabled = true;
        
        try {
            const response = await fetch('/api/targets');
            const data = await response.json();
            
            if (data.targets) {
                this.availableTargets = data.targets;
                this.populateTargetDropdown();
                
                // Hide loading area, show loaded area
                this.targetsLoadingArea.classList.add('hidden');
                this.targetsLoadedArea.classList.remove('hidden');
                
                // Set default target if available
                if (this.availableTargets.length > 0) {
                    const defaultTarget = this.availableTargets.find(t => t.name === 'first-column') || this.availableTargets[0];
                    this.currentTarget = defaultTarget.name;
                    this.targetDropdown.value = this.currentTarget;
                    this.updateTargetInfo();
                    // Don't load stats or solutions immediately - wait for user interaction
                }
            }
        } catch (error) {
            // Reset button on error
            this.loadTargetsBtn.textContent = '🎯 Load Targets';
            this.loadTargetsBtn.disabled = false;
            this.showError('Failed to load targets');
            console.error('Error loading targets:', error);
        }
    }

    populateTargetDropdown() {
        this.targetDropdown.innerHTML = '';
        
        this.availableTargets.forEach(target => {
            const option = document.createElement('option');
            option.value = target.name;
            option.textContent = `${target.name} (${target.total_solutions.toLocaleString()} solutions)`;
            this.targetDropdown.appendChild(option);
        });
    }

    onTargetChange() {
        this.currentTarget = this.targetDropdown.value;
        this.updateTargetInfo();
        this.statsLoaded = false; // Reset stats loading flag
        
        // Clear stats content to show it needs to be loaded
        this.statsContent.innerHTML = '<p class="loading-indicator">Click "Random Puzzle" to load statistics...</p>';
        
        // Clear current solution
        this.currentSolution = null;
        this.currentStep = 0;
        this.updateBoardDisplay('xxxxxxxxxxxxxxxx');
        this.updateSolutionInfo();
    }

    updateTargetInfo() {
        const target = this.availableTargets.find(t => t.name === this.currentTarget);
        if (!target) return;
        
        this.targetDescription.textContent = target.description;
        this.targetPositionsDisplay.textContent = `Positions: ${target.positions.join(', ')}`;
        this.targetSolutionsCount.textContent = `${target.total_solutions.toLocaleString()} solutions`;
        
        // Update position guide highlighting
        const guideElements = this.positionsGuide.querySelectorAll('div');
        guideElements.forEach((el, index) => {
            if (target.positions.includes(index)) {
                el.classList.add('target-highlight');
            } else {
                el.classList.remove('target-highlight');
            }
        });
        
        // Update board mode indicator
        this.boardModeIndicator.textContent = `Goal: ${target.description}`;
    }

    initializeBoard() {
        this.board.innerHTML = '';
        
        for (let i = 0; i < 16; i++) {
            const square = document.createElement('div');
            square.className = 'board-square';
            square.dataset.position = i;
            
            // Add chess board coloring
            const row = Math.floor(i / 4);
            const col = i % 4;
            square.classList.add((row + col) % 2 === 0 ? 'light-square' : 'dark-square');
            
            // Add click handler for editing
            square.addEventListener('click', () => this.onSquareClick(i));
            
            this.board.appendChild(square);
        }
    }

    highlightTargetSquares() {
        if (!this.currentTarget) return;
        
        const target = this.availableTargets.find(t => t.name === this.currentTarget);
        if (!target) return;
        
        // Remove existing target highlights
        this.board.querySelectorAll('.board-square').forEach(square => {
            square.classList.remove('target-square');
        });
        
        // Add target highlights
        target.positions.forEach(pos => {
            const square = this.board.querySelector(`[data-position="${pos}"]`);
            if (square) {
                square.classList.add('target-square');
            }
        });
    }

    updateBoardDisplay(boardState) {
        const pieces = {
            'K': '♔', 'Q': '♕', 'R': '♖', 'B': '♗', 'N': '♘', 'P': '♙',
            'k': '♚', 'q': '♛', 'r': '♜', 'b': '♝', 'n': '♞', 'p': '♟',
            'x': ''
        };

        for (let i = 0; i < 16; i++) {
            const square = this.board.children[i];
            const piece = boardState[i];
            square.textContent = pieces[piece] || '';
            
            // Add piece-specific classes
            square.classList.remove('piece-king', 'piece-queen', 'piece-rook', 'piece-bishop', 'piece-knight', 'piece-pawn', 'empty');
            
            if (piece && piece !== 'x') {
                square.classList.add(`piece-${this.getPieceType(piece)}`);
            } else {
                square.classList.add('empty');
            }
        }
        
        // Highlight target squares
        this.highlightTargetSquares();
    }

    getPieceType(piece) {
        const types = {
            'K': 'king', 'k': 'king',
            'Q': 'queen', 'q': 'queen', 
            'R': 'rook', 'r': 'rook',
            'B': 'bishop', 'b': 'bishop',
            'N': 'knight', 'n': 'knight',
            'P': 'pawn', 'p': 'pawn'
        };
        return types[piece] || 'empty';
    }

    async loadRandomSolution() {
        this.showLoading();
        try {
            const response = await fetch(`/api/random?target=${this.currentTarget}`);
            const data = await response.json();
            
            if (data.error) {
                this.showError(data.error);
                return;
            }
            
            this.currentSolution = data;
            this.currentStep = 0;
            this.displaySolution();
            
            // Load statistics on first random solution load
            if (!this.statsLoaded) {
                this.loadStatistics();
            }
            
        } catch (error) {
            this.showError('Failed to load random solution');
            console.error('Error:', error);
        } finally {
            this.hideLoading();
        }
    }

    async searchById(id = null) {
        const configId = id || parseInt(this.configIdInput.value);
        
        if (isNaN(configId) || configId < 0 || configId > 415800) {
            this.showError('Please enter a valid configuration ID (0-415800)');
            return;
        }
        
        this.showLoading();
        try {
            const response = await fetch(`/api/solution/${configId}?target=${this.currentTarget}`);
            const data = await response.json();
            
            if (data.error) {
                this.showError(data.error);
                return;
            }
            
            this.currentSolution = data;
            this.currentStep = 0;
            this.displaySolution();
            
            // Load statistics if not already loaded
            if (!this.statsLoaded) {
                this.loadStatistics();
            }
            
        } catch (error) {
            this.showError('Failed to load solution');
            console.error('Error:', error);
        } finally {
            this.hideLoading();
        }
    }

    displaySolution() {
        if (!this.currentSolution) return;
        
        this.updateSolutionInfo();
        
        // Update board
        if (this.currentSolution.solution_path && this.currentSolution.solution_path.length > 0) {
            const currentBoard = this.currentSolution.solution_path[this.currentStep];
            this.updateBoardDisplay(currentBoard);
        }
        
        // Update progress bar
        this.updateProgressBar();
        
        // Stop any current playback
        this.stopPlayback();
    }

    updateSolutionInfo() {
        if (this.currentSolution) {
            this.currentId.textContent = this.currentSolution.id;
            this.currentTargetDisplay.textContent = this.currentSolution.target_name || this.currentTarget;
            this.currentMoves.textContent = this.currentSolution.moves;
            this.currentStepDisplay.textContent = `${this.currentStep + 1} / ${this.currentSolution.total_steps}`;
        } else {
            this.currentId.textContent = '-';
            this.currentTargetDisplay.textContent = '-';
            this.currentMoves.textContent = '-';
            this.currentStepDisplay.textContent = '- / -';
        }
    }

    async loadStatistics() {
        if (this.statsLoaded) return; // Already loaded
        
        try {
            this.statsContent.innerHTML = '<p class="loading-indicator">Loading statistics...</p>';
            
            const response = await fetch(`/api/stats?target=${this.currentTarget}`);
            const data = await response.json();
            
            if (data.error) {
                this.statsContent.innerHTML = `<p>Error loading statistics: ${data.error}</p>`;
                return;
            }
            
            // Update target info display
            this.statsTargetInfo.innerHTML = `
                <strong>${data.target}</strong>: ${data.target_description}<br>
                Target positions: ${data.target_positions.join(', ')} | 
                Total solutions: ${data.total_solutions.toLocaleString()}
            `;
            
            // Update statistics display
            const html = `
                <div class="stats-grid">
                    <div class="stat-item">
                        <span class="stat-label">Total Solutions:</span>
                        <span class="stat-value">${data.total_solutions.toLocaleString()}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Move Range:</span>
                        <span class="stat-value">${data.move_stats.min} - ${data.move_stats.max}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Average Moves:</span>
                        <span class="stat-value">${data.move_stats.mean.toFixed(1)}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Median Moves:</span>
                        <span class="stat-value">${data.move_stats.median.toFixed(1)}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Avg Time:</span>
                        <span class="stat-value">${data.time_stats.mean.toFixed(2)}ms</span>
                    </div>
                </div>
            `;
            
            this.statsContent.innerHTML = html;
            this.statsLoaded = true;
            
        } catch (error) {
            this.statsContent.innerHTML = '<p>Error loading statistics</p>';
            console.error('Error loading statistics:', error);
        }
    }

    // Playback control methods
    togglePlayback() {
        if (this.isPlaying) {
            this.stopPlayback();
        } else {
            this.startPlayback();
        }
    }

    startPlayback() {
        if (!this.currentSolution || !this.currentSolution.solution_path) return;
        
        this.isPlaying = true;
        this.playPauseBtn.textContent = '⏸️';
        
        this.playbackTimer = setInterval(() => {
            if (this.currentStep < this.currentSolution.solution_path.length - 1) {
                this.nextStep();
            } else {
                this.stopPlayback();
            }
        }, this.playbackSpeed);
    }

    stopPlayback() {
        this.isPlaying = false;
        this.playPauseBtn.textContent = '▶️';
        
        if (this.playbackTimer) {
            clearInterval(this.playbackTimer);
            this.playbackTimer = null;
        }
    }

    nextStep() {
        if (!this.currentSolution || !this.currentSolution.solution_path) return;
        
        if (this.currentStep < this.currentSolution.solution_path.length - 1) {
            this.currentStep++;
            this.displaySolution();
        }
    }

    previousStep() {
        if (this.currentStep > 0) {
            this.currentStep--;
            this.displaySolution();
        }
    }

    goToFirstStep() {
        this.currentStep = 0;
        this.displaySolution();
    }

    goToLastStep() {
        if (this.currentSolution && this.currentSolution.solution_path) {
            this.currentStep = this.currentSolution.solution_path.length - 1;
            this.displaySolution();
        }
    }

    updateSpeed() {
        const sliderValue = parseInt(this.speedSlider.value);
        this.playbackSpeed = sliderValue;
        
        const speedMultiplier = (2500 - sliderValue) / 500;
        this.speedDisplay.textContent = `${(sliderValue / 1000).toFixed(2)}s (${speedMultiplier.toFixed(1)}x)`;
    }

    updateProgressBar() {
        if (!this.currentSolution || !this.currentSolution.solution_path) {
            this.progressFill.style.width = '0%';
            return;
        }
        
        const progress = ((this.currentStep + 1) / this.currentSolution.solution_path.length) * 100;
        this.progressFill.style.width = `${progress}%`;
    }

    // Editor methods (simplified)
    toggleEditMode() {
        this.editMode = !this.editMode;
        
        if (this.editMode) {
            this.enterEditMode();
        } else {
            this.exitEditMode();
        }
    }

    enterEditMode() {
        this.editMode = true;
        this.editModeBtn.textContent = '👁️ View Mode';
        this.piecePalette.classList.remove('hidden');
        this.playbackSection.classList.add('hidden');
        this.boardTitle.textContent = 'Board Editor';
        this.boardModeIndicator.textContent = 'Click squares to place pieces';
        
        // Initialize with current board or empty board
        if (this.currentSolution && this.currentSolution.solution_path) {
            this.editorBoardState = this.currentSolution.solution_path[this.currentStep];
        } else {
            this.editorBoardState = 'xxxxxxxxxxxxxxxx';
        }
        
        this.updateBoardDisplay(this.editorBoardState);
    }

    exitEditMode() {
        this.editMode = false;
        this.editModeBtn.textContent = '📝 Edit Board';
        this.piecePalette.classList.add('hidden');
        this.playbackSection.classList.remove('hidden');
        this.boardTitle.textContent = 'Hippodrome Puzzle Board';
        this.updateTargetInfo(); // Restore target info
        
        if (this.currentSolution) {
            this.displaySolution();
        }
    }

    selectPiece(piece) {
        this.selectedPiece = piece;
        
        this.pieceBtns.forEach(btn => {
            btn.classList.remove('active');
        });
        
        document.querySelector(`[data-piece="${piece}"]`).classList.add('active');
    }

    onSquareClick(position) {
        if (!this.editMode) return;
        
        this.editorBoardState = this.editorBoardState.substring(0, position) + 
                                this.selectedPiece + 
                                this.editorBoardState.substring(position + 1);
        
        this.updateBoardDisplay(this.editorBoardState);
    }

    clearBoard() {
        this.editorBoardState = 'xxxxxxxxxxxxxxxx';
        this.updateBoardDisplay(this.editorBoardState);
    }

    async searchByBoard() {
        if (!this.editMode) return;
        
        try {
            const response = await fetch('/api/search_by_board', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    board_state: this.editorBoardState,
                    target: this.currentTarget
                })
            });
            
            const data = await response.json();
            
            if (data.error) {
                this.showError(data.error);
                return;
            }
            
            if (data.results.length > 0) {
                // Load the first result
                this.searchById(data.results[0].id);
                this.exitEditMode();
            } else {
                this.showError(data.message || 'No solutions found for this board configuration');
            }
            
        } catch (error) {
            this.showError('Search failed');
            console.error('Error:', error);
        }
    }

    // Utility methods
    showLoading() {
        this.loadingOverlay.classList.remove('hidden');
    }

    hideLoading() {
        this.loadingOverlay.classList.add('hidden');
    }

    showError(message) {
        this.errorText.textContent = message;
        this.errorMessage.classList.remove('hidden');
        
        setTimeout(() => {
            this.hideError();
        }, 5000);
    }

    hideError() {
        this.errorMessage.classList.add('hidden');
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.explorer = new LazyHippodromeExplorer();
}); 