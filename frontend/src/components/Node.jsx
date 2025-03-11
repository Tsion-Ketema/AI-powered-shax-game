import React from 'react';
import './Node.css'; // Import the CSS file

class Node extends React.Component {
  // Use class properties to avoid binding in render
  onNodeClick = () => {
    this.props.nodeIsClicked(this.props.nodeNumber);
  }

  render() {
    const { position, controllingPlayer, className } = this.props;

    const hitboxSize = 30; // Increase hitbox size to 40x40px
    const style = {
      left: `${position.xPos}%`,
      top: `${position.yPos}%`,
      width: `${hitboxSize}px`,
      height: `${hitboxSize}px`,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      transform: 'translate(-50%, -50%)',
      border: '0px solid black'
    };

    let nodeClass = '';
    switch (controllingPlayer) {
      case 1:
        nodeClass = 'player1';
        break;
      case 2:
        nodeClass = 'player2';
        break;
      default:
        nodeClass = 'empty';
    }

    return (
      <div 
        className={`node ${nodeClass} ${className}`} // Combine node, player, and additional classes
        style={style}
        onClick={this.onNodeClick}
      >
        <div className={nodeClass} />
      </div>
    );
  }
}

export default Node;