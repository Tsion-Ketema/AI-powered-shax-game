import React from 'react';
import './Shaxboard.css';
import Node from './Node.jsx';
import Popup from './Popup.jsx';
import { Helmet } from 'react-helmet';


class Shaxboard extends React.Component {
  constructor() {
    super();
    // Initialize the state of the board and game variables
    this.state = {
      board: this.initializeBoard(),
      info: "Player 1's turn to place a piece.",
      gamePhase: "I", // "I" for initial placement, "II" for removing pieces, "III" for moving pieces
      player1Moves: 0,
      player2Moves: 0,
      player1Nodes: 0,
      player2Nodes: 0,
      currentPlayer: 1,
      firstMillPlayer: null,
      showPopup: false,
      popupMessage: '',
      removePiece: false,
      firstRemovalDone: false, // Track if the first removal in phase 2 is done
      selectedNode: null, // Track selected node in Phase III
      blockedHelpUsed: false, // Track if "I am blocked, help" was used
      winner: null, // Track the winner
      gameOver: false, // Track if the game is over
    };
  }

  // Initialize the board with 24 positions
  initializeBoard() {
    const board = [];
    for (let i = 0; i < 24; i++) {
      board.push({ position: this.getPosition(i), controllingPlayer: 0 });
    }
    return board;
  }

  // Get the next player in turn
  getNextPlayer(player) {
    return player === 1 ? 2 : 1;
  }

  // Check if a mill (three pieces in a row) is formed
  millIsFormed(index) {
    const board = this.state.board;
    const player = board[index].controllingPlayer;
    const positionsToCheck = [
      [2, 4, 10, 12, 18, 20], // Mid positions in a row
      [0, 8, 16], // Left column positions
      [6, 14, 22], // Right column positions
    ];

    // Check horizontal and vertical mills
    if (index % 2 === 0) {
      if (positionsToCheck[0].includes(index)) {
        if ((board[index - 1]?.controllingPlayer === player && board[index - 2]?.controllingPlayer === player) ||
            (board[index + 1]?.controllingPlayer === player && board[index + 2]?.controllingPlayer === player)) {
          return true;
        }
      } else if (positionsToCheck[1].includes(index)) {
        if ((board[index + 1]?.controllingPlayer === player && board[index + 2]?.controllingPlayer === player) ||
            (board[index + 6]?.controllingPlayer === player && board[index + 7]?.controllingPlayer === player)) {
          return true;
        }
      } else if (positionsToCheck[2].includes(index)) {
        if ((board[index - 1]?.controllingPlayer === player && board[index - 2]?.controllingPlayer === player) ||
            (board[index + 1]?.controllingPlayer === player && board[index - 6]?.controllingPlayer === player)) {
          return true;
        }
      }
    } else {
      if (![7, 15, 23].includes(index)) {
        if (board[index - 1]?.controllingPlayer === player && board[index + 1]?.controllingPlayer === player) {
          return true;
        }
      } else {
        if (board[index - 1]?.controllingPlayer === player && board[index - 7]?.controllingPlayer === player) {
          return true;
        }
      }
      if (index <= 7) {
        if (board[index + 8]?.controllingPlayer === player && board[index + 16]?.controllingPlayer === player) {
          return true;
        }
      } else if (index > 7 && index <= 15) {
        if (board[index - 8]?.controllingPlayer === player && board[index + 8]?.controllingPlayer === player) {
          return true;
        }
      } else if (index > 15 && index <= 23) {
        if (board[index - 8]?.controllingPlayer === player && board[index - 16]?.controllingPlayer === player) {
          return true;
        }
      }
    }
    return false;
  }

  // Get adjacent nodes for a given node index
  getAdjacentNodes(index) {
    const adjacent = {
      0: [1, 7], 1: [0, 2, 9], 2: [1, 3], 3: [2, 4, 11], 4: [3, 5], 5: [4, 6, 13], 6: [5, 7], 7: [0, 6, 15], 
      8: [9, 15], 9: [1, 8, 10, 17], 10: [9, 11], 11: [3, 10, 12, 19], 12: [11, 13], 13: [5, 12, 14, 21], 14: [13, 15], 
      15: [7, 8, 14, 23], 16: [17, 23], 17: [9, 16, 18], 18: [17, 19, 21], 19: [11, 18, 20], 20: [19, 21], 
      21: [13, 18, 20, 22], 22: [21, 23], 23: [15, 16, 22]
    };
    return adjacent[index] || [];
  }

  // Check if a node has an empty adjacent node (above, below, to the right, or to the left)
  hasEmptyDirectionalAdjacentNode(index) {
    const board = this.state.board;
    const directions = {
      top: index - 8 >= 0 ? index - 8 : null,
      bottom: index + 8 < 24 ? index + 8 : null,
      left: (index % 8 !== 0) ? index - 1 : null,
      right: (index % 8 !== 7) ? index + 1 : null
    };

    return Object.values(directions).some(adjIndex => adjIndex !== null && board[adjIndex]?.controllingPlayer === 0);
  }

  // Handle player move
  playerMove(node) {
    const { board, currentPlayer, gamePhase, removePiece, firstMillPlayer, firstRemovalDone, selectedNode, blockedHelpUsed } = this.state;

    if (removePiece) {
      this.handleRemovePiece(node);
    } else if (gamePhase === "III") {
      if (selectedNode === null) {
        if (board[node].controllingPlayer === currentPlayer) {
          this.setState({ selectedNode: node, info: `Player ${currentPlayer}, select an empty node to move to.` });
        } else {
          this.showTemporaryInfo("Invalid selection!");
        }
      } else {
        if (board[node].controllingPlayer === currentPlayer) {
          // Allow selecting another piece to move
          this.setState({ selectedNode: node, info: `Player ${currentPlayer}, select an empty node to move to.` });
        } else {
          const adjacentNodes = this.getAdjacentNodes(selectedNode);
          if (board[node].controllingPlayer === 0 && adjacentNodes.includes(node)) {
            board[node].controllingPlayer = currentPlayer;
            board[selectedNode].controllingPlayer = 0;
            this.setState({
              board,
              selectedNode: null,
            }, () => {
              if (this.millIsFormed(node)) {
                if (blockedHelpUsed) {
                  // If blockedHelpUsed is true and a mill is formed, switch back to the other player
                  const nextPlayer = this.getNextPlayer(currentPlayer);
                  this.setState({
                    currentPlayer: nextPlayer,
                    blockedHelpUsed: false,
                    info: `Player ${nextPlayer}'s turn to move a piece.`,
                  });
                } else {
                  this.setState({
                    info: `Player ${currentPlayer} formed a mill! Remove an opponent's piece.`,
                    removePiece: true,
                  });
                }
              } else {
                const nextPlayer = blockedHelpUsed ? this.getNextPlayer(currentPlayer) : this.getNextPlayer(currentPlayer);
                this.setState({
                  currentPlayer: nextPlayer,
                  blockedHelpUsed: false,
                  info: `Player ${nextPlayer}'s turn to move a piece.`,
                });
              }
            });
          } else {
            this.showTemporaryInfo("Invalid move!");
          }
        }
      }
    } else if (board[node].controllingPlayer === 0) {
      if (gamePhase === "I") {
        this.handlePhaseI(node);
      } else if (gamePhase === "II") {
        this.setState({ info: "Second game phase not yet implemented" });
      }
    } else {
      this.showTemporaryInfo("Invalid placement!");
    }
  }

  handleRemovePiece(node) {
    const board = [...this.state.board];
    const { currentPlayer, firstRemovalDone } = this.state;
    const opponentPlayer = this.getNextPlayer(currentPlayer);
    const opponentPlayerKey = currentPlayer === 1 ? 'player2Nodes' : 'player1Nodes';

    if (board[node].controllingPlayer !== 0 && board[node].controllingPlayer !== currentPlayer) {
      board[node].controllingPlayer = 0;
      this.setState(prevState => ({
        board,
        removePiece: false,
        info: `Player ${currentPlayer}'s turn to move a piece.`,
        [opponentPlayerKey]: prevState[opponentPlayerKey] - 1,
      }), () => {
        if (this.checkForWin(opponentPlayerKey)) {
          this.setState({
            showPopup: true,
            popupMessage: `Player ${currentPlayer} wins!`,
            winner: currentPlayer,
            gameOver: true,
          });
        } else {
          if (this.state.gamePhase === "II") {
            if (!firstRemovalDone) {
              // Allow the opponent to remove a piece
              this.setState({
                info: `Player ${opponentPlayer} removes an opponent's piece.`,
                removePiece: true,
                currentPlayer: opponentPlayer,
                firstRemovalDone: true,
              });
            } else {
              // Transition to phase III
              const firstMovePlayer = this.state.firstMillPlayer || 2;
              this.setState({
                gamePhase: "III",
                info: `Game Phase III: Player ${firstMovePlayer} starts moving pieces.`,
                removePiece: false,
                firstRemovalDone: false, // Reset for future removals
                currentPlayer: firstMovePlayer,
              });
            }
          } else if (this.state.gamePhase === "III") {
            // Continue to the next player's turn in Phase III
            this.setState({
              currentPlayer: this.getNextPlayer(currentPlayer),
              info: `Player ${this.getNextPlayer(currentPlayer)}'s turn to move a piece.`,
            });
          }
        }
      });
    } else {
      this.showTemporaryInfo("Invalid removal! You must remove an opponent's piece.");
    }
  }

  // Check if a player has won by having less than 3 pieces
  checkForWin(opponentPlayerKey) {
    return this.state[opponentPlayerKey] < 3;
  }

  // Handle the first phase of the game where players place their pieces
 
// Handle the first phase of the game where players place their pieces
handlePhaseI(node) {
  const board = [...this.state.board];
  board[node].controllingPlayer = this.state.currentPlayer;
  const playerKey = this.state.currentPlayer === 1 ? 'player1Nodes' : 'player2Nodes';
  const moveKey = this.state.currentPlayer === 1 ? 'player1Moves' : 'player2Moves';

  // Always increment the move count, even if a mill is formed
  this.setState(prevState => ({
    board,
    [playerKey]: prevState[playerKey] + 1,
    [moveKey]: prevState[moveKey] + 1,
  }), () => {
    // Print the number of moves for each player
    console.log(`Player 1 Moves: ${this.state.player1Moves}`);
    console.log(`Player 2 Moves: ${this.state.player2Moves}`);

    const nextPlayer = this.getNextPlayer(this.state.currentPlayer);

    // Check if a mill is formed
    if (this.millIsFormed(node)) {
      if (!this.state.firstMillPlayer) {
        this.setState({
          info: `Player ${this.state.currentPlayer} formed a mill!`,
          firstMillPlayer: this.state.currentPlayer, // Store the first mill player
          showPopup: true,
          popupMessage: 'Mill formed!',
          currentPlayer: nextPlayer,
        }, () => {
          // Hide the popup after 2 seconds
          setTimeout(() => {
            this.setState({ showPopup: false, info: `Player ${nextPlayer}'s turn to place a piece.` });
          }, 2000);
        });
      } else {
        this.setState({
          info: `Player ${this.state.currentPlayer} formed a mill!`,
          currentPlayer: nextPlayer,
        }, () => {
          this.setState({
            info: `Player ${nextPlayer}'s turn to place a piece.`,
          });
        });
      }
    }

    // Check if Player 2 has made 12 moves
    if (this.state.currentPlayer === 2 && this.state.player2Moves === 12) {
      console.log("Player 2 has made 12 moves. Moving to Phase II.");
      const firstMillPlayer = this.state.firstMillPlayer || nextPlayer;
      this.setState({
        gamePhase: "II",
        info: `Game Phase II: Player ${firstMillPlayer} removes an opponent's piece.`,
        removePiece: true,
        currentPlayer: firstMillPlayer,
      });
    } 
    // Check if both players have made all their moves (total 24 moves)
    else if (this.state.player1Moves + this.state.player2Moves >= 24) {
      const firstMillPlayer = this.state.firstMillPlayer || nextPlayer;
      this.setState({
        gamePhase: "II",
        info: `Game Phase II: Player ${firstMillPlayer} removes an opponent's piece.`,
        removePiece: true,
        currentPlayer: firstMillPlayer,
      });
    } else {
      // If not transitioning to Phase II, continue to the next player's turn
      this.setState({
        currentPlayer: nextPlayer,
        info: `Player ${nextPlayer}'s turn to place a piece.`,
      });
    }
  });
}

// Call this function after every move to check for win
checkForWinAfterEveryMove() {
  const { player1Nodes, player2Nodes } = this.state;
  if (player1Nodes < 3 || player2Nodes < 3) {
    const winner = player1Nodes < 3 ? 2 : 1;
    this.setState({
      gameOver: true,
      winner,
      popupMessage: `Player ${winner} wins!`,
      showPopup: true,
    });
  }
}

// Call this function in any place where a move is made to check if the game is over
handleAfterMove(node) {
  this.checkForWinAfterEveryMove();
}
  // Show temporary info messages
  showTemporaryInfo(message) {
    const previousInfo = this.state.info;
    this.setState({ info: message });
    setTimeout(() => this.setState({ info: previousInfo }), 1000);
  }

  // Reset the game state
  resetGame = () => {
    this.setState({
      board: this.initializeBoard(),
      info: "Player 1's turn to place a piece.",
      gamePhase: "I",
      player1Moves: 0,
      player2Moves: 0,
      player1Nodes: 0,
      player2Nodes: 0,
      currentPlayer: 1,
      firstMillPlayer: null,
      showPopup: false,
      popupMessage: '',
      removePiece: false,
      firstRemovalDone: false,
      selectedNode: null,
      blockedHelpUsed: false,
      winner: null,
      gameOver: false,
    });
  };

  // Handle the "I am blocked, help" button click
  handleBlockedHelp = () => {
    const { currentPlayer } = this.state;
    const nextPlayer = this.getNextPlayer(currentPlayer);

    // Switch to the next player and set the flag to indicate help was used
    this.setState({
      currentPlayer: nextPlayer,
      blockedHelpUsed: true,
      info: `Player ${nextPlayer}'s turn.`,
    });
  };

  // Calculate the position of a node on the board
  getPosition(index) {
    const positions = [
      [0, 0], [50, 0], [100, 0],
      [100, 50], [100, 100], [50, 100], [0, 100], [0, 50],
      [16.66, 16.66], [50, 16.66], [83.33, 16.66],
      [83.33, 50], [83.33, 83.33], [50, 83.33], [16.66, 83.33], [16.66, 50],
      [33.33, 33.33], [50, 33.33], [66.66, 33.33],
      [66.66, 50], [66.66, 66.66], [50, 66.66], [33.33, 66.66], [33.33, 50],
    ];
    return { xPos: positions[index][0], yPos: positions[index][1] };
  }

  // Close the popup
  closePopup = () => {
    this.setState({ showPopup: false, popupMessage: '' });
  }

  render() {
    const { appClassName } = this.props;
    const nodes = this.state.board.map((node, i) => {
      // Determine if the current node is highlighted or selected
      const additionalClass = node.controllingPlayer === 0 ? 'unclicked-node' : '';
      const highlightClass = (this.state.gamePhase === "III" && node.controllingPlayer === this.state.currentPlayer && this.hasEmptyDirectionalAdjacentNode(i)) ? 'highlight' : '';
      const selectedClass = (this.state.selectedNode === i) ? 'selected' : ''; // Apply 'selected' class if the node is selected
  
      // Combine all the classes dynamically
      const combinedClass = `${additionalClass} ${highlightClass} ${selectedClass}`.trim();
  
      return (
        <Node
          key={i}
          nodeNumber={i}
          controllingPlayer={node.controllingPlayer}
          position={node.position}
          nodeIsClicked={this.playerMove.bind(this)}
          className={combinedClass}  // Pass the combined class to the Node
        />
      );
    });
  
    return (
      <div id='play-now' className={appClassName}>
        <div style={{ height: '154px' }}>
          <h1 style={{ fontFamily: 'Poppins, sans-serif' }} className='header_for_board text-3xl font-semibold mb-4 text-center'>AI crackers shaxx game...</h1>
          <h2 style={{ fontFamily: 'Poppins, sans-serif' }} className='header_for_board text-3xl font-semibold mb-4 text-center'>{this.state.info}</h2>

        </div>
        <div className="board bi-2 ">
          {nodes}
          <div className="quarter bi-2 quarter1" />
          <div className="quarter bi-2 quarter2" />
          <div className="quarter bi-2 quarter3" />
          <div className="quarter bi-2 quarter4" />
          <div className="inner1 bi-4" />
          <div className="inner2 bi-4" />
        </div>
        {this.state.showPopup && (
          <Popup 
            message={this.state.popupMessage}
            onClose={this.closePopup}
            onReset={this.resetGame}
            gameOver={this.state.gameOver}
            style={{ fontFamily: 'Roboto, sans-serif' }}
          />
        )}
        <div className="button-container">
          <Helmet>
            <link href="https://fonts.googleapis.com/css2?family=Roboto+Condensed:wght@400;700&display=swap" rel="stylesheet" />
          </Helmet>
          <button style={{ fontFamily: 'Roboto, sans-serif' }} onClick={this.resetGame} className="reset-button">Reset</button>
          {this.state.gamePhase === "III" && (
            <button style={{ fontFamily: 'Roboto, sans-serif' }} onClick={this.handleBlockedHelp} className="help-button">Help Without Jare</button>
          )}
        </div>
      </div>
    );
  }
}

export default Shaxboard;