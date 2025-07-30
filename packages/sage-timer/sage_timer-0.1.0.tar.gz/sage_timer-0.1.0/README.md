# Sage

![](https://img.shields.io/badge/Python-3.10+-blue)

Sage is an easy-to-use command line timer that looks good and adheres
to your human inclinations about the language of time. Use natural
language like "25m" or "1 hour 30 minutes" when running timers, or
create preset timers that can be called with names like "pomodoro".

*Sage integrated into a development workflow*

![Sage pomodoro timer](https://raw.githubusercontent.com/nmsalvatore/sage/main/docs/images/workflow.png)

## Quick Start

1. Install Sage:

```bash
pip install sage-timer
```

2. Start a timer or stopwatch.

```bash
sage timer 35m                          # Start a 35-minute timer
sage timer pomodoro                     # Start pomodoro timer
sage timer pomodoro --paused            # Load pomodoro timer, but don't start
sage stopwatch                          # Start a stopwatch
sage stopwatch --paused                 # Load stopwatch, but don't start
sage list                               # See all preset timers
```

## Usage

### Timer

`sage timer` accepts flexible, human-readable time formats that work however you naturally think about time:

```bash
sage timer 25m                          # 25 minutes
sage timer "10 minutes 30 seconds"      # 10 minutes 30 seconds
sage timer 3min25s                      # 3 minutes 25 seconds
sage timer "1 hour 15m"                 # 1 hour 15 minutes
sage timer 2h30m45s                     # 2 hours 30 minutes 45 seconds
```

#### Let Timer Complete Quietly

Use the `--quiet` flag to let the timer complete without a sound.

```bash
sage timer 7m --quiet
```

#### Timer Controls

Once running, control your timer with simple keystrokes:

- **Space** - Pause and resume
- **Enter** - Increment counter
- **Q** - Quit

#### Custom Timers

Create custom timers and run them with `sage timer`.

```bash
sage create workout 1hr                 # Create 1 hour workout timer
sage timer workout                      # Start workout timer
```

### Managing Custom Timers

Custom timers are managed with the following commands:

```bash
sage list                               # List all available timers
sage create <name> <duration>           # Create a new timer
sage update <name> <duration>           # Update existing timer
sage rename <name> <new_name>           # Rename a timer
sage delete <name>                      # Delete a timer
```

#### Example Usage

```bash
sage create workout 45m                 # Create 45 minute workout timer
sage update workout 1hr                 # Update workout timer to 1 hour
sage rename workout yoga                # Rename workout timer name to yoga
sage timer yoga                         # Start 1 hour yoga timer
sage delete yoga                        # Delete yoga timer
```

All timer commands accept the same flexible time formats as the main timer.

### Stopwatch

For timing activities with unknown duration:

```bash
sage stopwatch                          # Start a stopwatch immediately
```

#### Stopwatch Controls

- **Space** - Pause and resume
- **Enter** - Increment counter
- **Q** - Quit

### Counter

Both `timer` and `stopwatch` include a counter which can be used to track
laps, counts, reps, etc. Just press `Enter` to increment.

### Load A Clock Without Starting

Both `timer` and `stopwatch` can load in a paused state with the
`--paused` flag. Once a clock is loaded, press `Space` to start.

```bash
sage timer 25m --paused                 # Load timer in paused state
sage stopwatch --paused                 # Load stopwatch in paused state
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions welcome! Please feel free to submit issues and pull requests.
