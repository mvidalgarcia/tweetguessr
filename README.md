# tweetguessr

## Install

Clone repository:

```bash
git clone https://github.com/mvidalgarcia/tweetguessr.git
cd tweetguessr
```

## Usage 

```bash
python3 run.py [-h] [--write-results] [--face-recognition] [--min-conf N] [--llr-threshold N]
```

#### Optional arguments:  

| Argument           | Description                                             |
|--------------------|---------------------------------------------------------|
| `-h`, `--help`         | show help message                                       |
| `--write-results`    | write results in .tsv file (default: No)                |
| `--face-recognition` | perform face recognition with facepp (default: No)      |
| `--min-conf N`       | minimum confidence in gender recognition (default 0.75) |
| `--llr-threshold N`  | float for LLR threshold (default 0.5)                   |
