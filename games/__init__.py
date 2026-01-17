"""Games package."""
from games.flappy_bird import FlappyBirdController, Game as FlappyBirdGame
from games.counting import CountingGameController, CountingGame
from games.rhythm import RhythmHandController, RhythmGame

__all__ = [
    'FlappyBirdController', 'FlappyBirdGame',
    'CountingGameController', 'CountingGame',
    'RhythmHandController', 'RhythmGame'
]
