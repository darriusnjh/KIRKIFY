"""
67 Games - Main Game Launcher
Launches games from the menu system.
"""
import sys
import argparse
from menu import GameMenu
from counting_game_controller import CountingGameController

# Import FlappyBirdController from main.py
# We'll import it dynamically to avoid circular imports
def get_flappy_controller():
    """Get FlappyBirdController class from main.py"""
    import main
    return main.FlappyBirdController

# Import RhythmHandController from rhythm_main.py
def get_rhythm_controller():
    """Get RhythmHandController class from rhythm_main.py"""
    import rhythm_main
    return rhythm_main.RhythmHandController


def launch_flappy_bird(model_type="mediapipe", use_hand_control=True):
    """Launch Flappy Bird game."""
    FlappyBirdController = get_flappy_controller()
    controller = FlappyBirdController(
        use_hand_control=use_hand_control,
        model_type=model_type
    )
    controller.run()


def launch_counting_game(model_type="mediapipe"):
    """Launch Counting Game."""
    controller = CountingGameController(model_type=model_type)
    controller.run()


def launch_rhythm_game(model_type="mediapipe", use_hand_control=True):
    """Launch Rhythm Game."""
    RhythmHandController = get_rhythm_controller()
    controller = RhythmHandController(
        use_hand_control=use_hand_control,
        model_type=model_type
    )
    controller.run()


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
    
    args = parser.parse_args()
    
    # If game specified, launch directly
    if args.game == 'flappy':
        launch_flappy_bird(model_type=args.model, use_hand_control=not args.no_hand)
        return
    elif args.game == 'counting':
        launch_counting_game(model_type=args.model)
        return
    elif args.game == 'rhythm':
        launch_rhythm_game(model_type=args.model, use_hand_control=not args.no_hand)
        return
    
    # Otherwise, show menu
    menu = GameMenu(screen_width=800, screen_height=600)
    
    # Add games to menu
    menu.add_game(
        "Flappy Bird",
        "Classic Flappy Bird with hand gesture control",
        lambda: launch_flappy_bird(model_type=args.model, use_hand_control=not args.no_hand)
    )
    
    menu.add_game(
        "Counting Game",
        "Count alternating hand gestures in 30 seconds",
        lambda: launch_counting_game(model_type=args.model)
    )
    
    menu.add_game(
        "Rhythm Game",
        "Hit notes with left and right hand gestures",
        lambda: launch_rhythm_game(model_type=args.model, use_hand_control=not args.no_hand)
    )
    
    # Run menu
    menu.run()


if __name__ == "__main__":
    main()
