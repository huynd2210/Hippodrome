// Hippodrome Solution Explorer - JavaScript
class HippodromeExplorer {
    constructor() {
        this.currentSolution = null;
        this.currentStep = 0;
        this.isPlaying = false;
        this.playbackTimer = null;
        this.playbackSpeed = 1000; // milliseconds
        
        // Editor state
        this.editMode = false;
        this.selectedPiece = 'K'; // Default to King
        this.editorBoardState = 'xxxxxxxxxxxxxxxx'; // Empty board (16 x's)
        
        this.initializeElements();
        this.bindEventListeners();
        this.initializeBoard();
        this.loadStatistics();
        this.loadRandomSolution(); // Start with a random solution
        
        // Initialize speed display
        this.updateSpeed();
    }

    initializeElements() {
        // Board
        this.board = document.getElementById('chess-board');
        
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
        // Playback controls
        this.playPauseBtn.addEventListener('click', () => this.togglePlayback());
        this.prevBtn.addEventListener('click', () => this.previousStep());
        this.nextBtn.addEventListener('click', () => this.nextStep());
        this.firstBtn.addEventListener('click', () => this.goToFirstStep());
        this.lastBtn.addEventListener('click', () => this.goToLastStep());
        
        // Speed control - use both 'input' and 'change' events for better responsiveness
        this.speedSlider.addEventListener('input', () => this.updateSpeed());
        this.speedSlider.addEventListener('change', () => this.updateSpeed());
        
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

    initializeBoard() {
        // Create 4x4 grid of squares
        this.board.innerHTML = '';
        for (let i = 0; i < 16; i++) {
            const square = document.createElement('div');
            square.classList.add('square');
            
            // Alternate colors (chess board pattern)
            const row = Math.floor(i / 4);
            const col = i % 4;
            if ((row + col) % 2 === 0) {
                square.classList.add('light');
            } else {
                square.classList.add('dark');
            }
            
            square.id = `square-${i}`;
            
            // Add click handler for edit mode
            square.addEventListener('click', () => this.handleSquareClick(i));
            
            this.board.appendChild(square);
        }
    }

    displayBoard(boardState) {
        // Lichess-style chess pieces (cburnett style - most popular)
        const lichessPieces = {
            'K': 'https://lichess1.org/assets/piece/cburnett/wK.svg',
            'R': 'https://lichess1.org/assets/piece/cburnett/wR.svg',
            'B': 'https://lichess1.org/assets/piece/cburnett/wB.svg',
            'N': 'https://lichess1.org/assets/piece/cburnett/wN.svg'
        };

        for (let i = 0; i < 16; i++) {
            const square = document.getElementById(`square-${i}`);
            const piece = boardState[i];
            
            // Clear previous content and classes
            square.innerHTML = '';
            square.className = square.className.replace(/piece-\w+/g, '');
            
            if (piece !== 'x' && lichessPieces[piece]) {
                // Create image element for Lichess piece
                const img = document.createElement('img');
                img.src = lichessPieces[piece];
                img.className = `lichess-piece piece-${piece.toLowerCase()}`;
                img.alt = piece;
                img.style.width = '85%';
                img.style.height = '85%';
                img.style.objectFit = 'contain';
                
                // Add color class for potential future styling
                square.classList.add(`piece-${piece.toLowerCase()}`);
                square.appendChild(img);
            }
            
            // Remove previous highlights
            square.classList.remove('highlight', 'goal-row');
            
            // Highlight goal row (top row) if it contains knights
            if (i < 4 && piece === 'N') {
                square.classList.add('goal-row');
            }
        }
    }

    highlightMovedPiece(prevBoard, currentBoard) {
        // Find the squares that changed and highlight them
        for (let i = 0; i < 16; i++) {
            const square = document.getElementById(`square-${i}`);
            if (prevBoard && prevBoard[i] !== currentBoard[i]) {
                square.classList.add('highlight');
                // Remove highlight after animation
                setTimeout(() => {
                    square.classList.remove('highlight');
                }, 1000);
            }
        }
    }

    async loadSolution(id) {
        this.showLoading();
        try {
            const response = await fetch(`/api/solution/${id}`);
            if (!response.ok) {
                throw new Error(`Solution not found for ID ${id}`);
            }
            
            const solution = await response.json();
            this.currentSolution = solution;
            this.currentStep = 0;
            this.updateDisplay();
            this.displayBoard(solution.solution_path[0]);
            
            this.hideLoading();
        } catch (error) {
            this.hideLoading();
            this.showError(error.message);
        }
    }

    async loadRandomSolution() {
        this.showLoading();
        try {
            const response = await fetch('/api/random');
            const solution = await response.json();
            this.currentSolution = solution;
            this.currentStep = 0;
            this.updateDisplay();
            this.displayBoard(solution.solution_path[0]);
            
            this.hideLoading();
        } catch (error) {
            this.hideLoading();
            this.showError('Failed to load random solution');
        }
    }





    async loadStatistics() {
        try {
            const response = await fetch('/api/stats');
            const stats = await response.json();
            
            const statsHtml = `
                <div class="stat-item">
                    <span>Total Solutions:</span>
                    <span class="stat-value">${stats.total_solutions.toLocaleString()}</span>
                </div>
                <div class="stat-item">
                    <span>Move Range:</span>
                    <span class="stat-value">${stats.move_stats.min} - ${stats.move_stats.max}</span>
                </div>
                <div class="stat-item">
                    <span>Average Moves:</span>
                    <span class="stat-value">${stats.move_stats.mean.toFixed(1)}</span>
                </div>
                <div class="stat-item">
                    <span>Median Moves:</span>
                    <span class="stat-value">${stats.move_stats.median}</span>
                </div>
            `;
            
            this.statsContent.innerHTML = statsHtml;
        } catch (error) {
            this.statsContent.innerHTML = '<p>Failed to load statistics</p>';
        }
    }

    searchById() {
        const id = parseInt(this.configIdInput.value);
        if (isNaN(id) || id < 0 || id > 415800) {
            this.showError('Please enter a valid ID between 0 and 415800');
            return;
        }
        this.loadSolution(id);
    }

    updateDisplay() {
        if (!this.currentSolution) return;
        
        this.currentId.textContent = this.currentSolution.id;
        this.currentMoves.textContent = this.currentSolution.moves;
        this.currentStepDisplay.textContent = `${this.currentStep + 1} / ${this.currentSolution.total_steps}`;
        
        // Update progress bar
        const progress = ((this.currentStep + 1) / this.currentSolution.total_steps) * 100;
        this.progressFill.style.width = `${progress}%`;
        
        // Update config ID input
        this.configIdInput.value = this.currentSolution.id;
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
            if (this.playbackTimer) {
                clearInterval(this.playbackTimer);
                this.playbackTimer = null;
            }
            
            // Start new timer with updated speed
            this.playbackTimer = setInterval(() => {
                this.nextStep();
                if (this.currentStep >= this.currentSolution.total_steps - 1) {
                    this.stopPlayback();
                }
            }, this.playbackSpeed);
        }
        
        console.log(`🚀 Slider: ${sliderValue} → Speed: ${this.playbackSpeed}ms (${(this.playbackSpeed / 1000).toFixed(2)}s) = ${speedMultiplier}x`);
        console.log(`📊 Slider range: ${minValue} to ${maxValue} (reversed calculation)`);
    }

    togglePlayback() {
        if (this.isPlaying) {
            this.stopPlayback();
        } else {
            this.startPlayback();
        }
    }

    startPlayback() {
        if (!this.currentSolution || this.currentStep >= this.currentSolution.total_steps - 1) {
            return;
        }
        
        this.isPlaying = true;
        this.playPauseBtn.textContent = '⏸️';
        
        console.log(`Starting playback at speed: ${this.playbackSpeed}ms`);
        
        this.playbackTimer = setInterval(() => {
            this.nextStep();
            if (this.currentStep >= this.currentSolution.total_steps - 1) {
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
        if (!this.currentSolution || this.currentStep >= this.currentSolution.total_steps - 1) {
            return;
        }
        
        const prevBoard = this.currentSolution.solution_path[this.currentStep];
        this.currentStep++;
        const currentBoard = this.currentSolution.solution_path[this.currentStep];
        
        this.displayBoard(currentBoard);
        this.highlightMovedPiece(prevBoard, currentBoard);
        this.updateDisplay();
    }

    previousStep() {
        if (!this.currentSolution || this.currentStep <= 0) {
            return;
        }
        
        this.currentStep--;
        this.displayBoard(this.currentSolution.solution_path[this.currentStep]);
        this.updateDisplay();
    }

    goToFirstStep() {
        if (!this.currentSolution) return;
        
        this.stopPlayback();
        this.currentStep = 0;
        this.displayBoard(this.currentSolution.solution_path[0]);
        this.updateDisplay();
    }

    goToLastStep() {
        if (!this.currentSolution) return;
        
        this.stopPlayback();
        this.currentStep = this.currentSolution.total_steps - 1;
        this.displayBoard(this.currentSolution.solution_path[this.currentStep]);
        this.updateDisplay();
    }

    showLoading() {
        this.loadingOverlay.classList.remove('hidden');
    }

    hideLoading() {
        this.loadingOverlay.classList.add('hidden');
    }

    showError(message) {
        this.errorText.textContent = message;
        this.errorMessage.classList.remove('hidden');
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            this.hideError();
        }, 5000);
    }

    hideError() {
        this.errorMessage.classList.add('hidden');
    }
    
    // ===== BOARD EDITOR FUNCTIONS =====
    
    toggleEditMode() {
        if (this.editMode) {
            this.exitEditMode();
        } else {
            this.enterEditMode();
        }
    }
    
    enterEditMode() {
        this.editMode = true;
        console.log('🎯 Entering edit mode');
        
        // Show/hide UI elements
        this.piecePalette.classList.remove('hidden');
        this.playbackSection.classList.add('hidden');
        
        // Update button text
        this.editModeBtn.textContent = '👁️ View Mode';
        
        // Update board appearance
        this.board.classList.add('board-edit-mode');
        this.makeSquaresClickable();
        
        // Update header text
        if (this.boardTitle) this.boardTitle.textContent = 'Board Editor';
        if (this.boardModeIndicator) this.boardModeIndicator.textContent = 'Click squares to place pieces • Select piece type below';
        
        // Display current editor board
        this.displayBoard(this.editorBoardState);
        
        // Stop any playing solution
        this.stopPlayback();
    }
    
    exitEditMode() {
        this.editMode = false;
        console.log('👁️ Exiting edit mode');
        
        // Show/hide UI elements
        this.piecePalette.classList.add('hidden');
        this.playbackSection.classList.remove('hidden');
        
        // Update button text
        this.editModeBtn.textContent = '📝 Edit Board';
        
        // Update board appearance
        this.board.classList.remove('board-edit-mode');
        this.makeSquaresNonClickable();
        
        // Update header text
        if (this.boardTitle) this.boardTitle.textContent = 'Hippodrome Puzzle Board';
        if (this.boardModeIndicator) this.boardModeIndicator.textContent = 'Goal: Get all Knights (♞) to the top row';
        
        // Return to current solution if available
        if (this.currentSolution) {
            this.displayBoard(this.currentSolution.solution_path[this.currentStep]);
        }
    }
    
    selectPiece(piece) {
        this.selectedPiece = piece;
        console.log(`🎯 Selected piece: ${piece}`);
        
        // Update button active state
        this.pieceBtns.forEach(btn => {
            btn.classList.toggle('active', btn.dataset.piece === piece);
        });
    }
    
    handleSquareClick(index) {
        if (!this.editMode) return;
        
        console.log(`🎯 Placing ${this.selectedPiece} at square ${index}`);
        
        // Update the editor board state
        const boardArray = this.editorBoardState.split('');
        boardArray[index] = this.selectedPiece;
        this.editorBoardState = boardArray.join('');
        
        // Update display
        this.displayBoard(this.editorBoardState);
    }
    
    makeSquaresClickable() {
        for (let i = 0; i < 16; i++) {
            const square = document.getElementById(`square-${i}`);
            square.classList.add('clickable');
        }
    }
    
    makeSquaresNonClickable() {
        for (let i = 0; i < 16; i++) {
            const square = document.getElementById(`square-${i}`);
            square.classList.remove('clickable');
        }
    }
    
    clearBoard() {
        console.log('🧹 Clearing board');
        this.editorBoardState = 'xxxxxxxxxxxxxxxx';
        this.displayBoard(this.editorBoardState);
    }
    
    async searchByBoard() {
        const boardState = this.editorBoardState;
        console.log(`🔍 Searching for board: ${boardState}`);
        
        // Validate board is not empty
        if (boardState === 'xxxxxxxxxxxxxxxx') {
            this.showError('Please place some pieces on the board before searching');
            return;
        }
        
        this.showLoading();
        try {
            const response = await fetch('/api/search_by_board', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ board_state: boardState })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const data = await response.json();
            console.log('🔍 Search response:', data);
            
            if (data.results && data.results.length > 0) {
                // Found matching solution(s) - load the first one
                console.log(`✅ Found ${data.results.length} matching solution(s)`);
                await this.loadSolution(data.results[0].id);
                this.exitEditMode(); // Switch back to view mode to show solution
            } else if (data.unsolvable) {
                // Board exists but has no solution
                this.hideLoading();
                this.showError(`❌ This board configuration has no solution! The puzzle cannot be solved from this starting position. Try a different arrangement.`);
            } else {
                // Board doesn't exist in database
                this.hideLoading();
                this.showError(`🔍 No solutions found for this board configuration. Try a different arrangement or check if all pieces are correctly placed.`);
            }
        } catch (error) {
            console.error('❌ Search by board failed:', error);
            this.hideLoading();
            this.showError('Failed to search board configuration. Please try again.');
        }
    }
}

// Initialize the application when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new HippodromeExplorer();
});

// Add keyboard shortcuts
document.addEventListener('keydown', (e) => {
    if (e.target.tagName === 'INPUT') return; // Don't trigger when typing in inputs
    
    switch(e.key) {
        case ' ':
            e.preventDefault();
            document.getElementById('play-pause-btn').click();
            break;
        case 'ArrowLeft':
            e.preventDefault();
            document.getElementById('prev-btn').click();
            break;
        case 'ArrowRight':
            e.preventDefault();
            document.getElementById('next-btn').click();
            break;
        case 'Home':
            e.preventDefault();
            document.getElementById('first-btn').click();
            break;
        case 'End':
            e.preventDefault();
            document.getElementById('last-btn').click();
            break;
        case 'r':
            e.preventDefault();
            document.getElementById('random-btn').click();
            break;
    }
}); 