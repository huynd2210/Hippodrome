// Hippodrome Solution Explorer - Enhanced Original JavaScript

/**
 * Main class for the Hippodrome Solution Explorer application.
 * Manages the UI, state, and interactions for the frontend.
 */
class HippodromeExplorer {
    constructor() {
        // --- State Properties ---
        this.currentSolution = null; // Holds the currently loaded solution object
        this.currentStep = 0;        // The current step in the solution path
        this.isPlaying = false;      // Flag for playback state
        this.playbackTimer = null;   // Timer for automatic playback
        this.playbackSpeed = 1000;   // Default playback speed in milliseconds
        this.currentTarget = 'top-row'; // Default target configuration
        this.availableTargets = [];  // List of available targets
        
        // --- Editor State ---
        this.editMode = false;       // Flag for board editor mode
        this.selectedPiece = 'K';    // Default piece for the editor palette
        this.editorBoardState = 'xxxxxxxxxxxxxxxx'; // Initial empty state for the editor
        
        // --- Initialization ---
        this.initializeElements();
        this.bindEventListeners();
        this.initializeBoard();
        
        // Load initial data in parallel for a better user experience
        this.loadTargets();
        this.loadStatistics();
        this.loadRandomSolution(); // Start with a random solution
        
        // Initialize the speed display
        this.updateSpeed();
    }

    /**
     * Caches all necessary DOM elements for performance.
     */
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
        this.boardModeText = document.getElementById('board-mode-indicator');
        this.statsContent = document.getElementById('stats-content');
        this.loadingOverlay = document.getElementById('loading-overlay');
        this.errorMessage = document.getElementById('error-message');
        this.errorText = document.getElementById('error-text');
        this.closeErrorBtn = document.getElementById('close-error');
    }

    /**
     * Binds all event listeners for UI interactions.
     */
    bindEventListeners() {
        // Target selection
        this.targetSelect.addEventListener('change', () => {
            this.currentTarget = this.targetSelect.value;
            this.highlightTargetSquares();
            this.loadStatistics();
            this.loadRandomSolution(); // Load a new random solution for the selected target
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

    /**
     * Creates the 16 squares of the chessboard and sets up their properties.
     */
    initializeBoard() {
        this.board.innerHTML = '';
        for (let i = 0; i < 16; i++) {
            const square = document.createElement('div');
            square.className = 'chess-square';
            square.dataset.position = i;
            
            // Add alternating colors for a classic chessboard look
            const row = Math.floor(i / 4);
            const col = i % 4;
            if ((row + col) % 2 === 0) {
                square.classList.add('light');
            } else {
                square.classList.add('dark');
            }
            
            // Add a click handler for the editor mode
            square.addEventListener('click', () => this.handleSquareClick(i));
            
            this.board.appendChild(square);
        }
        
        // Initial highlighting of target squares
        this.highlightTargetSquares();
    }

    /**
     * Loads the available targets from the API and populates the dropdown.
     */
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

    /**
     * Populates the target selection dropdown with the available targets.
     * @param {Array} targets - An array of target objects.
     */
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

    /**
     * Highlights the squares that correspond to the current target configuration.
     */
    highlightTargetSquares() {
        // Remove existing highlights
        document.querySelectorAll('.chess-square').forEach(square => {
            square.classList.remove('target-highlight');
        });
        
        // Add highlights for the current target
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

    /**
     * Clears the solution info display to show a loading state.
     */
    clearSolutionDisplay() {
        this.currentSolution = null;
        this.stopPlayback();
        this.currentId.textContent = '...';
        this.currentMoves.textContent = '...';
        this.currentStepDisplay.textContent = '- / -';
        this.configIdInput.value = '';
        this.progressFill.style.width = '0%';
    }

    /**
     * Loads a specific solution from the API based on the configuration ID.
     */
    async loadSolution() {
        const configId = parseInt(this.configIdInput.value);
        
        if (isNaN(configId) || configId < 0 || configId > 415800) {
            this.showError('Please enter a valid configuration ID (0-415800)');
            return;
        }
        
        this.showLoading();
        this.clearSolutionDisplay();
        try {
            const response = await fetch(`/api/solution/${configId}?target=${this.currentTarget}`);
            const data = await response.json();
            
            if (data.error) {
                this.showError(data.error);
                return;
            }
            
            this.currentSolution = data;
            this.currentStep = 0;
            this.updateUI();
            this.displayBoard(data.solution_path[0]);
            
        } catch (error) {
            this.showError('Failed to load solution');
            console.error('Error:', error);
        } finally {
            this.hideLoading();
        }
    }

    /**
     * Loads a random solution from the API.
     */
    async loadRandomSolution() {
        this.showLoading();
        this.clearSolutionDisplay();
        try {
            const response = await fetch(`/api/random?target=${this.currentTarget}`);
            const data = await response.json();
            
            if (data.error) {
                this.showError(data.error);
                return;
            }
            
            this.currentSolution = data;
            this.currentStep = 0;
            this.updateUI();
            this.displayBoard(data.solution_path[0]);
            
            // Update the config ID input to show the ID of the random solution
            this.configIdInput.value = data.id;
            
        } catch (error) {
            this.showError('Failed to load random solution');
            console.error('Error:', error);
        } finally {
            this.hideLoading();
        }
    }

    /**
     * Loads and displays statistics for the current target.
     */
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

    /**
     * Displays a board state on the UI.
     * @param {string} boardState - A 16-character string representing the board.
     */
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
                // Create a Lichess-style piece image for an authentic look
                const img = document.createElement('img');
                img.className = 'lichess-piece';
                img.src = this.getLichessPieceUrl(piece);
                img.alt = piece;
                square.appendChild(img);
                square.classList.add(`piece-${this.getPieceType(piece)}`);
                
                // Add a special glow effect if a knight is on a target square
                if ((piece === 'N' || piece === 'n') && targetPositions.includes(i)) {
                    square.classList.add('knight-on-target');
                }
            }
        }
        
        // Reapply target highlights
        this.highlightTargetSquares();
    }

    /**
     * Returns the URL for a Lichess piece image.
     * @param {string} piece - The character representing the piece.
     * @returns {string} The URL of the piece image.
     */
    getLichessPieceUrl(piece) {
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

    /**
     * Returns the type of a piece (e.g., 'king', 'queen').
     * @param {string} piece - The character representing the piece.
     * @returns {string} The type of the piece.
     */
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

    // --- Playback Control Methods ---

    /**
     * Toggles the playback of the solution.
     */
    togglePlayback() {
        if (this.isPlaying) {
            this.stopPlayback();
        } else {
            this.startPlayback();
        }
    }

    /**
     * Starts the automatic playback of the solution.
     */
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

    /**
     * Stops the automatic playback.
     */
    stopPlayback() {
        this.isPlaying = false;
        this.playPauseBtn.textContent = '▶️';
        if (this.playbackTimer) {
            clearInterval(this.playbackTimer);
            this.playbackTimer = null;
        }
    }

    /**
     * Moves to the next step in the solution path.
     */
    nextStep() {
        if (!this.currentSolution || this.currentStep >= this.currentSolution.solution_path.length - 1) {
            return;
        }
        
        this.currentStep++;
        this.displayBoard(this.currentSolution.solution_path[this.currentStep]);
        this.updateProgressBar();
        this.updateStepInfo();
    }

    /**
     * Moves to the previous step in the solution path.
     */
    previousStep() {
        if (!this.currentSolution || this.currentStep <= 0) {
            return;
        }
        
        this.currentStep--;
        this.displayBoard(this.currentSolution.solution_path[this.currentStep]);
        this.updateProgressBar();
        this.updateStepInfo();
    }

    /**
     * Jumps to a specific step in the solution path.
     * @param {number} step - The step number to go to.
     */
    goToStep(step) {
        if (!this.currentSolution || step < 0 || step >= this.currentSolution.solution_path.length) {
            return;
        }
        
        this.currentStep = step;
        this.displayBoard(this.currentSolution.solution_path[this.currentStep]);
        this.updateProgressBar();
        this.updateStepInfo();
    }

    /**
     * Jumps to the last step of the solution.
     */
    goToLastStep() {
        if (!this.currentSolution) return;
        this.goToStep(this.currentSolution.solution_path.length - 1);
    }

    /**
     * Updates the playback speed based on the slider value.
     */
    updateSpeed() {
        const sliderValue = parseInt(this.speedSlider.value);
        const minValue = parseInt(this.speedSlider.min);
        const maxValue = parseInt(this.speedSlider.max);
        
        // Reverse the calculation so that the right side of the slider is faster
        const actualSpeed = minValue + maxValue - sliderValue;
        
        // Calculate a speed multiplier for display (e.g., 1.0x, 2.0x)
        const speedMultiplier = (1000 / actualSpeed).toFixed(1);
        
        this.playbackSpeed = actualSpeed;
        
        // Update the display text
        this.speedDisplay.textContent = `${(this.playbackSpeed / 1000).toFixed(2)}s (${speedMultiplier}x)`;
        
        // If currently playing, restart with the new speed
        if (this.isPlaying) {
            this.stopPlayback();
            this.startPlayback();
        }
    }

    /**
     * Updates all UI elements with the current solution information.
     */
    updateUI() {
        if (!this.currentSolution) return;
        
        this.currentId.textContent = `#${this.currentSolution.id}`;
        this.currentMoves.textContent = `${this.currentSolution.moves}`;
        
        this.updateProgressBar();
        this.updateStepInfo();
    }

    /**
     * Updates the progress bar to reflect the current step.
     */
    updateProgressBar() {
        if (!this.currentSolution) return;
        
        const progress = (this.currentStep / (this.currentSolution.solution_path.length - 1)) * 100;
        this.progressFill.style.width = `${progress}%`;
    }

    /**
     * Updates the step counter display (e.g., "5 / 10").
     */
    updateStepInfo() {
        if (!this.currentSolution) return;
        
        this.currentStepDisplay.textContent = `${this.currentStep} / ${this.currentSolution.solution_path.length - 1}`;
    }

    // --- Editor Functionality ---

    /**
     * Toggles the board editor mode.
     */
    toggleEditMode() {
        this.editMode = !this.editMode;
        
        if (this.editMode) {
            this.enterEditMode();
        } else {
            this.exitEditMode();
        }
    }

    /**
     * Enters the board editor mode.
     */
    enterEditMode() {
        this.editMode = true;
        this.piecePalette.classList.remove('hidden');
        this.editModeBtn.textContent = '👁️ View Mode';
        this.boardModeText.textContent = '✏️ Edit Mode - Click squares to place pieces';
        this.stopPlayback();
        
        // Initialize with the current board state or an empty board
        if (this.currentSolution) {
            this.editorBoardState = this.currentSolution.solution_path[this.currentStep];
        } else {
            this.editorBoardState = 'xxxxxxxxxxxxxxxx';
        }
        
        this.displayBoard(this.editorBoardState);
    }

    /**
     * Exits the board editor mode and restores the solution view.
     */
    exitEditMode() {
        this.editMode = false;
        this.piecePalette.classList.add('hidden');
        this.editModeBtn.textContent = '📝 Edit Board';
        this.boardModeText.textContent = '📋 Solution View';
        
        // Restore the solution display
        if (this.currentSolution) {
            this.displayBoard(this.currentSolution.solution_path[this.currentStep]);
        }
    }

    /**
     * Handles clicks on the board squares when in editor mode.
     * @param {number} position - The position of the clicked square (0-15).
     */
    handleSquareClick(position) {
        if (!this.editMode) return;
        
        // Update the board state string
        const boardArray = this.editorBoardState.split('');
        boardArray[position] = this.selectedPiece;
        this.editorBoardState = boardArray.join('');
        
        // Update the display
        this.displayBoard(this.editorBoardState);
    }

    /**
     * Clears the board in editor mode.
     */
    clearBoard() {
        this.editorBoardState = 'xxxxxxxxxxxxxxxx';
        this.displayBoard(this.editorBoardState);
    }

    /**
     * Searches for a solution based on the current board state in the editor.
     */
    async searchByBoard() {
        if (this.editorBoardState.length !== 16) {
            this.showError('Invalid board state');
            return;
        }
        
        this.showLoading();
        this.clearSolutionDisplay();
        try {
            const response = await fetch(`/api/search_by_board?board=${this.editorBoardState}&target=${this.currentTarget}`);
            const data = await response.json();
            
            if (data.error) {
                this.showError(data.error);
                return;
            }
            
            // Exit edit mode and show the found solution
            this.exitEditMode();
            this.currentSolution = data;
            this.currentStep = 0;
            this.updateUI();
            this.displayBoard(data.solution_path[0]);
            
            // Update the config ID input
            this.configIdInput.value = data.id;
            
        } catch (error) {
            this.showError('Search failed');
            console.error('Error:', error);
        } finally {
            this.hideLoading();
        }
    }

    // --- Utility Methods ---

    /**
     * Shows the loading overlay.
     */
    showLoading() {
        this.loadingOverlay.classList.remove('hidden');
    }

    /**
     * Hides the loading overlay.
     */
    hideLoading() {
        this.loadingOverlay.classList.add('hidden');
    }

    /**
     * Displays an error message to the user.
     * @param {string} message - The error message to display.
     */
    showError(message) {
        this.errorText.textContent = message;
        this.errorMessage.classList.remove('hidden');
        
        // Automatically hide the error after 5 seconds
        setTimeout(() => {
            this.hideError();
        }, 5000);
    }

    /**
     * Hides the error message.
     */
    hideError() {
        this.errorMessage.classList.add('hidden');
    }
}

// Initialize the application when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', () => {
    new HippodromeExplorer();
});