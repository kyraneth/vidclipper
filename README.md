# VidClipper

A lightweight application for downloading YouTube videos and creating clips from specific segments.

## Features

- **User-friendly GUI**: Simple interface for downloading and clipping videos
- **Command-line Interface**: For automation and scripting
- **Multiple Clip Support**: Create multiple clips from a single video
- **Clip Concatenation**: Option to join multiple clips into a single video
- **Playback Speed Control**: Adjust the speed of your clips
- **Flexible Time Format**: Input times in seconds or MM:SS format
- **Configurable Output Directory**: Choose where to save your clips

## Installation

### Prerequisites

- Python 3.6 or higher
- Required Python packages:
  - moviepy
  - pytube
  - tkinter (usually comes with Python)

### Setup

1. Clone this repository or download the source code
2. Install the required packages:

```bash
pip install moviepy pytube
```

## Usage

### GUI Mode

Run the application without any arguments to launch the GUI:

```bash
python vidclipper.py
```

1. Enter a YouTube URL
2. Set your desired output directory
3. Add clip segments by entering start and end times
4. Adjust playback speed if needed
5. Choose whether to concatenate clips
6. Click "Download & Process" to start

### Command-line Mode

For command-line usage, provide arguments:

```bash
python vidclipper.py [YouTube URL] [start1] [end1] [start2] [end2] ... [options]
```

#### Examples:

Download a video and create a clip from 30 seconds to 1 minute:
```bash
python vidclipper.py https://www.youtube.com/watch?v=dQw4w9WgXcQ 30 60
```

Create multiple clips and concatenate them:
```bash
python vidclipper.py https://www.youtube.com/watch?v=dQw4w9WgXcQ 30 60 90 120 --conc
```

Use time format (MM:SS-MM:SS):
```bash
python vidclipper.py https://www.youtube.com/watch?v=dQw4w9WgXcQ --timecode-format "0:30-1:00, 1:30-2:00"
```

Change playback speed:
```bash
python vidclipper.py https://www.youtube.com/watch?v=dQw4w9WgXcQ 30 60 --speed 1.5
```

Specify output directory:
```bash
python vidclipper.py https://www.youtube.com/watch?v=dQw4w9WgXcQ 30 60 --output-dir /path/to/output
```

## Advanced Options

- `--speed`: Change playback speed (default: 1.0)
- `--conc`: Concatenate all clips into a single video
- `--output-dir`: Specify the output directory
- `--timecode-format`: Use time format "MM:SS-MM:SS, MM:SS-MM:SS" instead of raw seconds

## Troubleshooting

- **Download Errors**: Make sure you have a stable internet connection and the video is available
- **Processing Errors**: Ensure you have sufficient disk space and the correct permissions
- **Invalid Time Format**: Check that your time inputs are in the correct format

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Feel free to submit a pull request or open an issue.