# Simple Zuma Clone

A simple version of the classic Zuma game built with Python and Pygame.

## About the Game
This project is a fan-made clone of the original Zuma. It features a spiral track, a shooter, and a variety of special effect balls. Your goal is to eliminate all balls before they reach the hole. If a ball reaches the hole, the game is over.

## How to Run
1. Ensure you have Python installed.
2. Install Pygame:
   ```bash
   pip install pygame
3. Run the game:
   ```bash
   python Zuma.py
   ```

Controls

· Mouse: Aim the shooter.
· Left Click: Shoot a ball.
· Spacebar: Start the game / Restart.

Special Effect Balls

Here are the effects you can trigger when you match and eliminate these special balls:

Shooter & Weapon Effects

· Aim: Doubles the shooting speed and adds a red trail to your shots for 10 seconds.
· Sluggish: Halves the shooting speed for 10 seconds (the opposite of Aim).
· Dizzy: Reverses your shooting direction for 10 seconds. For example, if you aim up, the ball shoots down.
· Block: Disables the shooter completely. You cannot fire any balls for 10 seconds.
· Arrow: Grants 6 arrow shots. When an arrow hits a ball, it instantly destroys that single ball and triggers a chain reaction for any connected same-colored balls.

Ball Chain Effects

· Slow: Slows down the moving ball chain by half for 10 seconds.
· Forward: Doubles the moving speed of the ball chain for 10 seconds.
· Reverse: Reverses the direction of the ball chain for 10 seconds. Balls will move backwards towards the start.
· Freeze: Completely stops the ball chain from moving for 10 seconds.
· Blind: Hides all balls on the track from your view for 10 seconds. The balls are still there and the game logic still works; you just can't see them!

Instant & Strategic Effects

· Explode: Instantly destroys the 9 balls surrounding the one you just hit, and triggers a chain reaction.
· Clear Color: Instantly eliminates all balls on the track that have the exact same color as the ball you hit.
· Lightning: Your next shot becomes a lightning ball. It flies straight through the ball chain, destroying every ball it touches, until it leaves the screen.
· Dye: Your next shot becomes a dye ball. When it hits a ball, it changes the color of the surrounding 9 balls to match the dye ball's color.
· Rainbow: Your next shot becomes a rainbow ball. When it hits a ball, it instantly clears both the left and right adjacent groups of same-colored balls.
· Add Score: Instantly adds 100 points to your score.
· Rearrange: Randomly shuffles the colors of all balls currently on the track.

Random & Independent Effects

· Question (Random): This ball triggers a random effect from any of the others listed above!
· Wormhole: Opens a wormhole at the end of the track for 10 seconds. If any ball reaches the end during this time, it gets sucked into the wormhole instead of making you lose the game.

License

This project is open-source and available under the MIT License.

```