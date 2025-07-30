# Sage

![](https://img.shields.io/badge/Python-3.10+-blue)

Sage is an easy-to-use command line timer that looks good and adheres
to your human inclinations about the language of time. Use natural
language like "25m" or "1 hour 30 minutes" when running timers, or
create preset timers that can be called with names like "pomodoro".

*Sage integrated into a development workflow.*

![Sage pomodoro timer](https://raw.githubusercontent.com/nmsalvatore/sage/main/docs/images/workflow.png)

## Quick Start

1. Install Sage:

```bash
pip install sage-timer
```

2. Start a timer or stopwatch.

```bash
sage timer 35m                          # Start a 35-minute timer
sage stopwatch                          # Start a stopwatch
```

## Usage

### Timer

*A running Sage timer.*

![Sage timer](https://raw.githubusercontent.com/nmsalvatore/sage/main/docs/images/timer.png)

#### Run A Timer

Sage recognizes flexible, human-readable time formats across multiple
styles that match however you naturally express time.

```bash
sage timer 25m                          # Start a 25-minute timer
sage timer "10 minutes 30 seconds"      # Start a 10-minute 30-second timer
sage timer 3min25s                      # Start a 3-minute 25-second
```

It also accepts custom timer names. A list of built-in timers can be
found with `sage list`.

```bash
sage timer pomodoro                     # Start a 25-minute timer
```

#### Let A Timer Complete Quietly

Use the `--quiet` flag to let the timer complete without a sound.

```bash
sage timer 7m --quiet
```

#### Custom Timers

Create custom timers and run them with `sage timer`.

```bash
sage create workout 1hr                 # Create 1 hour workout timer
sage timer workout                      # Start workout timer
```

#### Managing Custom Timers

Custom timers are managed with the following commands:

```bash
sage list                               # List all available timers
sage create <name> <duration>           # Create a new timer
sage update <name> <duration>           # Update existing timer
sage rename <name> <new_name>           # Rename a timer
sage delete <name>                      # Delete a timer
```

##### Example Usage

```bash
sage create workout 45m                 # Create 45 minute workout timer
sage update workout 1hr                 # Update workout timer to 1 hour
sage rename workout yoga                # Rename workout timer name to yoga
sage timer yoga                         # Start 1 hour yoga timer
sage delete yoga                        # Delete yoga timer
```

### Stopwatch

*A running Sage stopwatch, with centisecond precision.*

![Sage stopwatch](https://raw.githubusercontent.com/nmsalvatore/sage/main/docs/images/stopwatch.png)

#### Run A Stopwatch

Sage provides precise time tracking with centisecond accuracy for
activities with unknown duration.

```bash
sage stopwatch                          # Start a stopwatch immediately
```

### Clock Controls

Once running, both the timer and stopwatch can be controlled with the
following simple keystrokes:

- **Space** - Pause and resume
- **Enter** - Increment counter
- **Q** - Quit

### The Counter

The Sage timer and stopwatch include a counter which can be used to track
laps, counts, reps, etc. Just press `Enter` to increment while in the
clock interface.

### Load A Clock Without Starting

*Built-in potato timer, loaded in a paused state.*

![Paused Sage timer](https://raw.githubusercontent.com/nmsalvatore/sage/main/docs/images/paused.png)

The `timer` and `stopwatch` commands accept a `--paused` flag that will
load the clock in a paused state. Once the clock is loaded, a "Paused"
message will appear beneath the clock time and the clock will wait for
the `Space` key to start.

```bash
sage timer 25m --paused                 # Load timer in paused state
sage stopwatch --paused                 # Load stopwatch in paused state
```

## Philosophy

Most CLI tools prioritize technical precision over human usability,
making them inaccessible to casual users. Sage was built out of a
desire to prove that command line applications can be both powerful
and intuitive, using natural language processing and a simple UX
design.

## License

MIT License - see [LICENSE](https://github.com/nmsalvatore/sage/blob/main/LICENSE) file for details.

## Contributing

Contributions welcome! Please feel free to submit issues and pull requests.
