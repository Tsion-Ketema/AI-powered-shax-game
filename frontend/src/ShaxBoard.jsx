import React from 'react';
import './css/Shaxboard.css';
import Node from './components/Node.jsx';
import Popup from './components/Popup.jsx';

class Shaxboard extends React.Component {
    constructor() {
        super();
        this.state = {
            gameState: {
                board: this.initializeBoard(),
                info: "Player 1's turn",
                currentPlayer: 1,
                showPopup: false,
                popupMessage: '',
                playerOneCaptures:0,
                playerTwoCaptures:0,
                playerOneMoves:0,
                playerTwoMoves:0,
                gameOver: false,
                winner: null,
                phase:1,
                selectedNode: null,
                firstMillPlayer: null, // Track first mill in phase 1
                mills: [
                    [0, 1, 2], [3, 4, 5], [6, 7, 8], [9, 10, 11],
                    [12, 13, 14], [15, 16, 17], [18, 19, 20],
                    [21, 22, 23], [0, 9, 21], [3, 10, 18],
                    [6, 11, 15], [1, 4, 7], [16, 19, 22],
                    [8, 12, 17], [5, 13, 20], [2, 14, 23]
                ]
            },
            loading: false,
            error: null
        };
    }

    checkMillFormation = (board, index, player) => {
        return this.state.gameState.mills.some(mill =>
            mill.includes(index) &&
            mill.every(node => board[node].controllingPlayer === player)
        );
    }

    initializeBoard() {
        const board = [];
        for (let i = 0; i < 24; i++) {
            board.push({ position: this.getPosition(i), controllingPlayer: 0 });
        }
        return board;
    }

    getPosition(index) {
        const positions = [
            [0, 0], [50, 0], [100, 0],
            [16.66, 16.66],[50, 16.66], [83.33, 16.66],
            [33.33, 33.33],[50, 33.33],[66.66, 33.33],
            [0, 50],[16.66, 50],[33.33, 50],[66.66, 50],[83.33, 50],[100, 50],
            [33.33, 66.66],[50, 66.66],[66.66, 66.66],
            [16.66, 83.33],[50, 83.33],[83.33, 83.33],
            [0, 100] , [50, 100] ,[100, 100]

        ];
        return { xPos: positions[index][0], yPos: positions[index][1] };
    }
    getAdjacentNodes(index) {
        const adjacent = {
            0: [1, 9], 1: [0, 4, 2], 2: [1, 14], 4: [3, 7, 5], 5: [4, 13], 6: [7, 11], 7: [6, 8],
            8: [7, 12], 9: [0, 10, 21], 10: [3, 9, 11, 18], 11: [6, 15], 12: [8, 17], 13: [5, 12, 14, 20],
            14: [2, 13, 23], 15: [11, 16], 16: [15, 19, 17], 17: [12, 16], 18: [10, 19], 19: [16, 18, 20, 22],
            20: [13, 19], 21: [9, 22], 22: [19, 21, 23], 23: [14, 22]
        };
        return adjacent[index] || [];
    }
    // Simulate a move by updating the board state locally
    sendMove = (nodeIndex) => {
        const { gameState } = this.state;
        const { board, currentPlayer, phase, selectedNode } = gameState;
        console.log("selected node "+selectedNode)

        if (gameState.gameOver) return;

        if (phase === 1) {
            if (board[nodeIndex].controllingPlayer !== 0) return;

            const updatedBoard = [...board];
            updatedBoard[nodeIndex].controllingPlayer = currentPlayer;

            // Check for mill formation
            const millFormed = this.checkMillFormation(
                updatedBoard,
                nodeIndex,
                currentPlayer
            );

            if (millFormed && gameState.firstMillPlayer === null) {
                gameState.firstMillPlayer = currentPlayer;
                console.log("First Mill formed.")

            }

            currentPlayer === 1
                ? gameState.playerOneMoves++
                : gameState.playerTwoMoves++;

            const totalMoves = gameState.playerOneMoves + gameState.playerTwoMoves;
            const nextPhase = totalMoves === 24 ? 2 : phase;
            let nextPlayer = currentPlayer === 1 ? 2 : 1;

            // Handle phase transition with mill priority
            if (nextPhase === 2) {
                if (gameState.firstMillPlayer !== null) {
                    nextPlayer = gameState.firstMillPlayer;
                }
            }

            this.setState({
                gameState: {
                    ...gameState,
                    board: updatedBoard,
                    phase: nextPhase,
                    currentPlayer: nextPlayer,
                    info: nextPhase === 2
                        ? `Phase 2: ${nextPlayer}'s turn`
                        : `Player ${nextPlayer}'s turn`,
                },
            });
        }
        else if (phase === 2) {
            console.log("controlling player = "+board[nodeIndex].controllingPlayer+ "current player" +currentPlayer)

            if (selectedNode === null) {
                // First click - select piece or capture
                if (board[nodeIndex].controllingPlayer !== 0 && board[nodeIndex].controllingPlayer !== currentPlayer)    {

                        console.log("Capturing by player "+ currentPlayer)

                        // Only allow capture if piece has no empty adjacent nodes
                        const updatedBoard = [...board];
                        updatedBoard[nodeIndex].controllingPlayer = 0;
                        currentPlayer === 2
                            ? gameState.playerTwoCaptures++
                            : gameState.playerOneCaptures++;

                        const nextPlayer = currentPlayer === 1 ? 2 : 1;

                        this.setState({
                            gameState: {
                                ...gameState,
                                board: updatedBoard,
                                currentPlayer: nextPlayer,
                                info: `Player ${nextPlayer}'s turn`,
                            },
                        });

                }else if (board[nodeIndex].controllingPlayer === currentPlayer) {
                    // Select own piece for movement
                    console.log("am clicking my own node. "+nodeIndex)

                    this.setState({
                        gameState: {
                            ...gameState,
                            selectedNode: nodeIndex,
                        },
                    });
                }

            } else {
                // Second click - handle movement
                if (nodeIndex === selectedNode) {
                    console.log("canceled clicked node "+nodeIndex)
                    // Deselect if clicking same node
                    this.setState({
                        gameState: {
                            ...gameState,
                            selectedNode: null,
                        },
                    });
                } else {
                    const adjacentNodes = this.getAdjacentNodes(selectedNode);
                    if (adjacentNodes.includes(nodeIndex) && board[nodeIndex].controllingPlayer === 0) {
                        // Valid move
                        const updatedBoard = [...board];
                        updatedBoard[nodeIndex].controllingPlayer = currentPlayer;
                        updatedBoard[selectedNode].controllingPlayer = 0;

                        currentPlayer === 1
                            ? gameState.playerOneMoves++
                            : gameState.playerTwoMoves++;

                        const nextPlayer = currentPlayer === 1 ? 2 : 1;

                        this.setState({
                            gameState: {
                                ...gameState,
                                board: updatedBoard,
                                selectedNode: null,
                                currentPlayer: nextPlayer,
                                info: `Player ${nextPlayer}'s turn`,
                            },
                        });
                    } else {
                        // Invalid move, reset selection
                        this.setState({
                            gameState: {
                                ...gameState,
                                selectedNode: null,
                            },
                        });
                    }
                }
            }
        }
    };
    render() {
        const { gameState, loading, error } = this.state;
        const { board, info, showPopup, popupMessage, gameOver } = gameState;

        if (loading) return <div>Loading...</div>;
        if (error) return <div>{error}</div>;

        return (
            <div id='play-now' className={this.props.appClassName}>
                <div style={{ height: '154px' }}>
                    <h1 className='header_for_board text-3xl font-semibold mb-4 text-center'>
                        Shax by AI crackers
                    </h1>
                    <h2 className='header_for_board text-3xl font-semibold mb-10 text-center'>
                        {info}
                    </h2>
                </div>
                <div className="board bi-2">
                    {board.map((node, i) => (
                        <Node
                            key={i}
                            nodeNumber={i}
                            controllingPlayer={node.controllingPlayer}
                            position={this.getPosition(i)}
                            nodeIsClicked={() => this.sendMove(i)}
                            className={`
                                        ${node.controllingPlayer === 0 ? 'unclicked-node' : ''}
                                        ${gameState.selectedNode === i ? 'selected' : ''}
                                        `}
                        />
                    ))}
                    <div className="quarter bi-2 quarter1" />
                    <div className="quarter bi-2 quarter2" />
                    <div className="quarter bi-2 quarter3" />
                    <div className="quarter bi-2 quarter4" />
                    <div className="inner1 bi-4" />
                    <div className="inner2 bi-4" />
                </div>
                {showPopup && (
                    <Popup
                        message={popupMessage}
                        onClose={() => this.setState({ gameState: { ...gameState, showPopup: false } })}
                        onReset={() => this.setState({ gameState: { ...gameState, board: this.initializeBoard(), info: "Player 1's turn", currentPlayer: 1 } })}
                        gameOver={gameOver}
                    />
                )}
                <div className="button-container">
                    <button onClick={() => this.setState({ gameState: { ...gameState, board: this.initializeBoard(), info: "Player 1's turn", currentPlayer: 1 } })} className="reset-button">Reset</button>
                </div>
            </div>
        );
    }
}

export default Shaxboard;