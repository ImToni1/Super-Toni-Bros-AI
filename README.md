# Super Toni Bros

Super Toni Bros is a simple platformer game built in Python using the `pygame` library. Game levels are defined via external text files, and the game now includes an AI player that learns using a genetic algorithm.

## Project Contents

-   **`start.py`**: The main script to launch the game. It opens a menu to choose manual play or run the AI.
-   **`src/core/`**: Contains core game modules:
    -   **`player.py`**: Defines the `Player` class for player movement, jumping, and gravity.
    -   **`platforms.py`**: Defines the `PlatformManager` class for loading platforms from a level file, managing them, and setting the goal.
    -   **`level.txt`**: Text file defining the platform layout for the level used in the game.
-   **`src/manual_game/`**:
    -   **`manual_game.py`**: Contains the logic for manual gameplay, including player movement, platform interaction, and the victory screen.
-   **`src/ai_game/`**: Contains modules related to Artificial Intelligence:
    -   **`main_ai.py`**: Manages the genetic algorithm for training the AI player.
    -   **`ai_brain.py`**: Defines the AI player's "brain" structure, including its actions and mutation method.
    -   **`game_simulation.py`**: Runs a single game instance for an AI brain to evaluate its performance (fitness).
    -   **`best_ai_path.pkl`**: (Potential file) Stores the instructions of the best-ranked AI player after training. If it exists, the AI will demonstrate this path.
-   **`images/`**: Contains assets such as the background, player, platforms, ground, and victory screen.
-   **`README.md`**: This document describing the project.

## How to Run

1.  **Ensure `src/core/level.txt` exists** and is formatted correctly.
    -   Inside this file, define each platform on a new line using the format: `x,y,width` (e.g., `400,500,150`). The height is fixed.
    -   Lines starting with `#` will be treated as comments and ignored.
2.  **Start the game by running:**
    ```bash
    python start.py
    ```
3.  **From the main menu, you can choose:**
    * **"Igraj Ručno" (Play Manually)**: Control the player directly.
    * **"Pokreni AI" (Run AI)**:
        * If a pre-trained AI exists at `src/ai_game/best_ai_path.pkl`, it will be loaded and demonstrated.
        * If not, the genetic algorithm training process will begin. This can take a significant amount of time. The best AI found during training (if it achieves a winning state) will be saved.

### Manual Controls:

-   **Right Arrow (`→`)**: Move the player to the right (scrolls the platforms to the left).
-   **Left Arrow (`←`)**: Move the player to the left (scrolls the platforms to the right, up to a limit).
-   **Spacebar (`Space`)**: Jump (only works when the player is on the ground).

### Game Objective (Manual & AI):

-   Reach the flag on the final platform (as defined by the `src/core/level.txt` file) to win the game.

## About the Game

-   **Gravity**: The player is affected by gravity and will fall if not on a platform.
-   **Platforms**: Platform layouts are loaded from `src/core/level.txt`.
-   **Victory Screen**: When the player reaches the goal, a "You Win!" screen is displayed along with the time taken to complete the game (for manual play).
-   **AI Player**: The game includes an AI player that can learn to play the game using a genetic algorithm. The AI's progress, current generation, and elapsed simulation time are displayed when the AI is running.

## Description of Folders and Files:

-   **`images/`**: Contains all images used in the game.
-   **`src/`**: Main source code, divided into subdirectories:
    -   **`core/`**: Contains essential game components like the player, platform manager, and the level definition file (`level.txt`).
    -   **`manual_game/`**: Contains the logic for the manually playable version of the game (`manual_game.py`).
    -   **`ai_game/`**: Contains modules for the AI, including the genetic algorithm (`main_ai.py`), AI brain/action logic (`ai_brain.py`), and the game simulation environment for AI training (`game_simulation.py`). Potentially stores the best trained AI in `best_ai_path.pkl`.
-   **`start.py`**: The entry point script to launch the game menu.
-   **`README.md`**: This document.

## Requirements

-   Python 3.x
-   `pygame` library

> [!TIP]
> Install `pygame` if it's not already installed:
> ```bash
> pip install pygame
> ```
