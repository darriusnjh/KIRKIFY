"""
67 Games - Main Game Launcher
Launches games from the menu system.
"""
import sys
import os
import argparse

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from ui.menu import GameMenu
from games.counting.controller import CountingGameController

# Import FlappyBirdController
def get_flappy_controller():
    """Get FlappyBirdController class"""
    from games.flappy_bird.controller import FlappyBirdController
    return FlappyBirdController

# Import RhythmHandController
def get_rhythm_controller():
    """Get RhythmHandController class"""
    from games.rhythm.controller import RhythmHandController
    return RhythmHandController


def launch_flappy_bird(model_type="mediapipe", use_hand_control=True, fullscreen=False):
    """
    Launch Flappy Bird game.
    
    Returns:
        'main_menu' if user wants to return to menu, 'exit' if user wants to exit
    """
    FlappyBirdController = get_flappy_controller()
    controller = FlappyBirdController(
        use_hand_control=use_hand_control,
        model_type=model_type,
        fullscreen=fullscreen
    )
    return controller.run()


def launch_counting_game(model_type="mediapipe", fullscreen=False):
    """
    Launch Counting Game.
    
    Returns:
        'main_menu' if user wants to return to menu, 'exit' if user wants to exit
    """
    controller = CountingGameController(model_type=model_type, fullscreen=fullscreen)
    return controller.run()


def launch_rhythm_game(model_type="mediapipe", use_hand_control=True, fullscreen=False):
    """
    Launch Rhythm Game.
    
    Returns:
        'main_menu' if user wants to return to menu, 'exit' if user wants to exit
    """
    RhythmHandController = get_rhythm_controller()
    controller = RhythmHandController(
        use_hand_control=use_hand_control,
        model_type=model_type,
        fullscreen=fullscreen
    )
    return controller.run()


def main():
    """Main entry point - shows menu and launches games."""
    parser = argparse.ArgumentParser(description='67 Games - Hand Gesture Controlled Games')
    parser.add_argument('-m', '--model', type=str, default='mediapipe',
                       choices=['mediapipe', 'tiny', 'prn', 'v4-tiny', 'yolo'],
                       help='Hand detection model to use (default: mediapipe)')
    parser.add_argument('--no-hand', action='store_true',
                       help='Disable hand gesture control (keyboard only)')
    parser.add_argument('--game', type=str, default=None,
                       choices=['flappy', 'counting', 'rhythm'],
                       help='Launch game directly without menu')
    parser.add_argument('--fullscreen', action='store_true',
                       help='Start in fullscreen mode')
    
    args = parser.parse_args()
    
    # If game specified, launch directly
    if args.game == 'flappy':
        launch_flappy_bird(model_type=args.model, use_hand_control=not args.no_hand, fullscreen=args.fullscreen)
        return
    elif args.game == 'counting':
        launch_counting_game(model_type=args.model, fullscreen=args.fullscreen)
        return
    elif args.game == 'rhythm':
        launch_rhythm_game(model_type=args.model, use_hand_control=not args.no_hand, fullscreen=args.fullscreen)
        return
    
    # Otherwise, show menu
    menu = GameMenu(screen_width=800, screen_height=600, fullscreen=args.fullscreen)
    
    # Store fullscreen state to pass to games
    game_fullscreen = args.fullscreen
    
    # Add games to menu
    menu.add_game(
        "Flappy Bird",
        "Classic Flappy Bird with hand gesture control",
        lambda: launch_flappy_bird(model_type=args.model, use_hand_control=not args.no_hand, fullscreen=game_fullscreen)
    )
    
    menu.add_game(
        "Counting Game",
        "Count alternating hand gestures in 30 seconds",
        lambda: launch_counting_game(model_type=args.model, fullscreen=game_fullscreen)
    )
    
    menu.add_game(
        "Rhythm Game",
        "Hit notes with left and right hand gestures",
        lambda: launch_rhythm_game(model_type=args.model, use_hand_control=not args.no_hand, fullscreen=game_fullscreen)
    )
    
    # Run menu
    menu.run()


if __name__ == "__main__":
    main()
