// Hippodrome Solution Explorer - Enhanced Original JavaScript
class HippodromeExplorer {
    constructor() {
        this.currentSolution = null;
        this.currentStep = 0;
        this.isPlaying = false;
        this.playbackTimer = null;
        this.playbackSpeed = 1000; // milliseconds
        this.currentTarget = 'top-row'; // Default target
        this.availableTargets = [];
        
        // Editor state
        this.editMode = false;
        this.selectedPiece = 'K'; // Default to King
        this.editorBoardState = 'xxxxxxxxxxxxxxxx'; // Empty board (16 x's)
        
        this.initializeElements();
        this.bindEventListeners();
        this.initializeBoard();
        
        // Load everything in parallel for good UX
        this.loadTargets();
        this.loadStatistics();
        this.loadRandomSolution(); // Start with a random solution
        
        // Initialize speed display
        this.updateSpeed();
    }

    initializeElements() {
        // Board
        this.board = document.getElementById('chess-board');
        
        // Target elements
        this.targetSelect = document.getElementById('target-select');
        
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
        
        // UI elements
        this.currentId = document.getElementById('current-id');
        this.currentMoves = document.getElementById('current-moves');
        this.currentStepDisplay = document.getElementById('current-step');
        this.boardModeText = document.getElementById('board-mode-text');
        this.statsContent = document.getElementById('stats-content');
        this.loadingOverlay = document.getElementById('loading-overlay');
        this.errorMessage = document.getElementById('error-message');
        this.errorText = document.getElementById('error-text');
        this.closeErrorBtn = document.getElementById('close-error');
    }

    bindEventListeners() {
        // Target selection
        this.targetSelect.addEventListener('change', () => {
            this.currentTarget = this.targetSelect.value;
            this.highlightTargetSquares();
            this.loadStatistics();
            this.loadRandomSolution(); // Load new random solution for new target
        });
        
        // Playback controls
        this.playPauseBtn.addEventListener('click', () => this.togglePlayback());
        this.prevBtn.addEventListener('click', () => this.previousStep());
        this.nextBtn.addEventListener('click', () => this.nextStep());
        this.firstBtn.addEventListener('click', () => this.goToStep(0));
        this.lastBtn.addEventListener('click', () => this.goToLastStep());
        this.speedSlider.addEventListener('input', () => this.updateSpeed());
        
        // Search controls
        this.searchBtn.addEventListener('click', () => this.loadSolution());
        this.randomBtn.addEventListener('click', () => this.loadRandomSolution());
        this.configIdInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.loadSolution();
        });
        
        // Editor controls
        this.editModeBtn.addEventListener('click', () => this.toggleEditMode());
        this.clearBoardBtn.addEventListener('click', () => this.clearBoard());
        this.searchBoardBtn.addEventListener('click', () => this.searchByBoard());
        this.exitEditBtn.addEventListener('click', () => this.exitEditMode());
        
        // Piece palette
        this.pieceBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                this.pieceBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                this.selectedPiece = btn.dataset.piece;
            });
        });
        
        // Error handling
        this.closeErrorBtn.addEventListener('click', () => this.hideError());
    }

    initializeBoard() {
        this.board.innerHTML = '';
        for (let i = 0; i < 16; i++) {
            const square = document.createElement('div');
            square.className = 'chess-square';
            square.dataset.position = i;
            
            // Add alternating colors
            const row = Math.floor(i / 4);
            const col = i % 4;
            if ((row + col) % 2 === 0) {
                square.classList.add('light');
            } else {
                square.classList.add('dark');
            }
            
            // Add click handler for editor
            square.addEventListener('click', () => this.handleSquareClick(i));
            
            this.board.appendChild(square);
        }
        
        // Initial target highlighting
        this.highlightTargetSquares();
    }

    async loadTargets() {
        // Define targets directly with simplified descriptions
        const targets = [
            {
                name: 'top-row',
                positions: '0,1,2,3',
                description: 'top-row'
            },
            {
                name: 'first-column', 
                positions: '0,4,8,12',
                description: 'first-column'
            },
            {
                name: 'last-column',
                positions: '3,7,11,15', 
                description: 'last-column'
            },
            {
                name: 'center',
                positions: '5,6,9,10',
                description: 'center'
            },
            {
                name: 'corners',
                positions: '0,3,12,15',
                description: 'corners'
            }
        ];
        
        this.availableTargets = targets;
        this.populateTargetDropdown(targets);
    }

    populateTargetDropdown(targets) {
        this.targetSelect.innerHTML = '';
        
        targets.forEach(target => {
            const option = document.createElement('option');
            option.value = target.name;
            option.textContent = target.description;
            if (target.name === this.currentTarget) {
                option.selected = true;
            }
            this.targetSelect.appendChild(option);
        });
    }



    highlightTargetSquares() {
        // Remove existing highlights
        document.querySelectorAll('.chess-square').forEach(square => {
            square.classList.remove('target-highlight');
        });
        
        // Add highlights for current target
        const target = this.availableTargets.find(t => t.name === this.currentTarget);
        if (target) {
            const positions = target.positions.split(',').map(p => parseInt(p.trim()));
            positions.forEach(pos => {
                const square = document.querySelector(`[data-position="${pos}"]`);
                if (square) {
                    square.classList.add('target-highlight');
                }
            });
        }
    }

    async loadSolution() {
        const configId = parseInt(this.configIdInput.value);
        
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
            this.stopPlayback();
            this.updateUI();
            this.displayBoard(data.solution_path[0]);
            
        } catch (error) {
            this.showError('Failed to load solution');
            console.error('Error:', error);
        } finally {
            this.hideLoading();
        }
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
            this.stopPlayback();
            this.updateUI();
            this.displayBoard(data.solution_path[0]);
            
            // Update the config ID input
            this.configIdInput.value = data.id;
            
        } catch (error) {
            this.showError('Failed to load random solution');
            console.error('Error:', error);
        } finally {
            this.hideLoading();
        }
    }

    async loadStatistics() {
        try {
            const response = await fetch(`/api/stats?target=${this.currentTarget}`);
            const data = await response.json();
            
            if (data.error) {
                this.statsContent.innerHTML = '<p>Error loading statistics</p>';
                return;
            }
            
            const html = `
                <div class="stat-item">
                    <span class="stat-label">Target:</span>
                    <span class="stat-value">${data.target}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Total Solutions:</span>
                    <span class="stat-value">${data.total_solutions.toLocaleString()}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Average Moves:</span>
                    <span class="stat-value">${data.avg_moves}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Move Range:</span>
                    <span class="stat-value">${data.min_moves} - ${data.max_moves}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Average Time:</span>
                    <span class="stat-value">${data.avg_time_ms}ms</span>
                </div>
            `;
            
            this.statsContent.innerHTML = html;
            
        } catch (error) {
            this.statsContent.innerHTML = '<p>Error loading statistics</p>';
            console.error('Error:', error);
        }
    }

    displayBoard(boardState) {
        if (!boardState) return;
        
        const squares = document.querySelectorAll('.chess-square');
        const target = this.availableTargets.find(t => t.name === this.currentTarget);
        const targetPositions = target ? target.positions.split(',').map(p => parseInt(p.trim())) : [];
        
        for (let i = 0; i < 16; i++) {
            const square = squares[i];
            const piece = boardState[i];
            
            // Clear previous content and classes
            square.innerHTML = '';
            square.className = square.className.replace(/piece-\w+/g, '');
            square.classList.remove('knight-on-target');
            
            if (piece !== 'x') {
                // Create Lichess-style piece image
                const img = document.createElement('img');
                img.className = 'lichess-piece';
                img.src = this.getLichessPieceUrl(piece);
                img.alt = piece;
                square.appendChild(img);
                square.classList.add(`piece-${this.getPieceType(piece)}`);
                
                // Add special glow if knight is on target position
                if ((piece === 'N' || piece === 'n') && targetPositions.includes(i)) {
                    square.classList.add('knight-on-target');
                }
            }
        }
        
        // Reapply target highlights
        this.highlightTargetSquares();
    }

    getLichessPieceUrl(piece) {
        // Using Lichess piece images for authentic look
        const baseUrl = 'https://lichess1.org/assets/piece/cburnett/';
        const pieceMap = {
            'K': 'wK.svg', 'k': 'bK.svg',
            'Q': 'wQ.svg', 'q': 'bQ.svg', 
            'R': 'wR.svg', 'r': 'bR.svg',
            'B': 'wB.svg', 'b': 'bB.svg',
            'N': 'wN.svg', 'n': 'bN.svg',
            'P': 'wP.svg', 'p': 'bP.svg'
        };
        return baseUrl + (pieceMap[piece] || '');
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

    // Playback control methods
    togglePlayback() {
        if (this.isPlaying) {
            this.stopPlayback();
        } else {
            this.startPlayback();
        }
    }

    startPlayback() {
        if (!this.currentSolution || this.currentStep >= this.currentSolution.solution_path.length - 1) {
            return;
        }
        
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
        if (!this.currentSolution || this.currentStep >= this.currentSolution.solution_path.length - 1) {
            return;
        }
        
        this.currentStep++;
        this.displayBoard(this.currentSolution.solution_path[this.currentStep]);
        this.updateProgressBar();
        this.updateStepInfo();
    }

    previousStep() {
        if (!this.currentSolution || this.currentStep <= 0) {
            return;
        }
        
        this.currentStep--;
        this.displayBoard(this.currentSolution.solution_path[this.currentStep]);
        this.updateProgressBar();
        this.updateStepInfo();
    }

    goToStep(step) {
        if (!this.currentSolution || step < 0 || step >= this.currentSolution.solution_path.length) {
            return;
        }
        
        this.currentStep = step;
        this.displayBoard(this.currentSolution.solution_path[this.currentStep]);
        this.updateProgressBar();
        this.updateStepInfo();
    }

    goToLastStep() {
        if (!this.currentSolution) return;
        this.goToStep(this.currentSolution.solution_path.length - 1);
    }

    updateSpeed() {
        // Get the slider value and reverse it (so right = fast, left = slow)
        const sliderValue = parseInt(this.speedSlider.value);
        const minValue = parseInt(this.speedSlider.min);
        const maxValue = parseInt(this.speedSlider.max);
        
        // Reverse the calculation: right side (high value) = fast speed (low ms)
        const actualSpeed = minValue + maxValue - sliderValue;
        
        // Calculate speed multiplier for display
        const speedMultiplier = (1000 / actualSpeed).toFixed(1);
        
        // Update the speed property
        this.playbackSpeed = actualSpeed;
        
        // Update the display text with speed multiplier
        this.speedDisplay.textContent = `${(this.playbackSpeed / 1000).toFixed(2)}s (${speedMultiplier}x)`;
        
        // If currently playing, restart with new speed
        if (this.isPlaying) {
            // Clear the old timer
            clearInterval(this.playInterval);
            // Start new timer with updated speed
            this.startPlayback();
        }
    }

    updateUI() {
        if (!this.currentSolution) return;
        
        this.currentId.textContent = `#${this.currentSolution.id}`;
        this.currentMoves.textContent = `${this.currentSolution.moves}`;
        
        this.updateProgressBar();
        this.updateStepInfo();
    }

    updateProgressBar() {
        if (!this.currentSolution) return;
        
        const progress = (this.currentStep / (this.currentSolution.solution_path.length - 1)) * 100;
        this.progressFill.style.width = `${progress}%`;
    }

    updateStepInfo() {
        if (!this.currentSolution) return;
        
        this.currentStepDisplay.textContent = `${this.currentStep} / ${this.currentSolution.solution_path.length - 1}`;
    }

    // Editor functionality (keeping from original)
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
        this.piecePalette.classList.remove('hidden');
        this.editModeBtn.textContent = '👁️ View Mode';
        this.boardModeText.textContent = '✏️ Edit Mode - Click squares to place pieces';
        this.stopPlayback();
        
        // Initialize with current board or empty board
        if (this.currentSolution) {
            this.editorBoardState = this.currentSolution.solution_path[this.currentStep];
        } else {
            this.editorBoardState = 'xxxxxxxxxxxxxxxx';
        }
        
        this.displayBoard(this.editorBoardState);
    }

    exitEditMode() {
        this.editMode = false;
        this.piecePalette.classList.add('hidden');
        this.editModeBtn.textContent = '📝 Edit Board';
        this.boardModeText.textContent = '📋 Solution View';
        
        // Restore solution display
        if (this.currentSolution) {
            this.displayBoard(this.currentSolution.solution_path[this.currentStep]);
        }
    }

    handleSquareClick(position) {
        if (!this.editMode) return;
        
        // Update board state
        const boardArray = this.editorBoardState.split('');
        boardArray[position] = this.selectedPiece;
        this.editorBoardState = boardArray.join('');
        
        // Update display
        this.displayBoard(this.editorBoardState);
    }

    clearBoard() {
        this.editorBoardState = 'xxxxxxxxxxxxxxxx';
        this.displayBoard(this.editorBoardState);
    }

    async searchByBoard() {
        if (this.editorBoardState.length !== 16) {
            this.showError('Invalid board state');
            return;
        }
        
        this.showLoading();
        try {
            const response = await fetch(`/api/search_by_board?board=${this.editorBoardState}&target=${this.currentTarget}`);
            const data = await response.json();
            
            if (data.error) {
                this.showError(data.error);
                return;
            }
            
            // Exit edit mode and show solution
            this.exitEditMode();
            this.currentSolution = data;
            this.currentStep = 0;
            this.updateUI();
            this.displayBoard(data.solution_path[0]);
            
            // Update config ID
            this.configIdInput.value = data.id;
            
        } catch (error) {
            this.showError('Search failed');
            console.error('Error:', error);
        } finally {
            this.hideLoading();
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

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    new HippodromeExplorer();
}); 