# rock-paper-scissors-py

Multi-player and multi-action Rock, Paper, Scissors game client.

## Installation

To install, run the following commands:

```bash
pip install rock-paper-scissors-py

# or

git@github.com:jwc20/rock-paper-scissors-py.git
cd rock-paper-scissors-py
```

To use the engine, first setup and activate a python virtual environment (venv)

```bash
python3 -m venv .venv
. ./.venv/bin/activate
```

Install from requirements.txt

```bash
pip3 install -r requirements.txt
```

## Usage:

In your Python file, to import, type

```python
import rps
```

Set the number of actions allowed in the game (beats logic will be generated based on the number of actions)

```python
action_three = 3  # rock, paper, scissors

# => BEATS = {
#        0: [2],  # Rock beats Scissors
#        1: [0],  # Paper beats Rock
#        2: [1],  # Scissors beats Paper
#    }


action_five = 5      # rock, paper, scissors, Spock, lizard

# => BEATS = {
#        0: [2, 3],  # Rock crushes Scissors & Lizard
#        1: [0, 4],  # Paper covers Rock & disproves Spock
#        2: [1, 3],  # Scissors cuts Paper & decapitates Lizard
#        3: [1, 4],  # Lizard eats Paper & poisons Spock
#        4: [0, 2],  # Spock vaporizes Rock & smashes Scissors
#    }
```

Set the players with either fixed or random actions

```python
player_jae = rps.FixedActionPlayer("Jae", 0) # always plays Rock, like an idiot

# bunch of random players with random actions
random_player_names = [f"random{i}" for i in range(20)]
random_players = [rps.RandomActionPlayer(name) for name in random_player_names]
```

Set the game and play

```python
game = rps.Game(random_players, action_three)

game.play()
```

### Example

Run the `example.py` in the root directory

```bash
python example.py
```

---

## Note

Game consists of `m` players and `n` actions where `m >= 2` and `n >= 3` and `n` is an odd number.

Actions are hand gestures played by the players (rock, paper, scissors).

If the number of actions set in the game is between 5 and 15, the game uses the rules made by [Sam Kass](https://www.samkass.com/theories/RPSSL.html) and [David C. Lovelace](https://www.umop.com/rps.htm).

---

## See also:

- https://www.umop.com/rps.htm

- https://www.samkass.com/theories/RPSSL.html
