# Telegram Chat Statastics

The project conducts a simple analysis on a telegram chat json file. By processing the chat file it generates a `json` file containing the information and statistics of the users. The statistics include the number of:
- Messages a user sent
- Questions a user asked
- Answers a user gave to other users
- Replies of a user

A word cloud is also generated for chat messages.

> **Note**: The statistics of the users will be saved in a `json` file in `src.data` directory.

## How To Run

After cloning the repo, you need to install the requirements:

```bash
pip install -r requirements.txt
```

Next, you have to [download](https://www.wfonts.com/font/b-homa) a persian font, `BHoma.ttf`, and put it in `src.data` directory. Then you need to get a telegram chat `json` file. It's recommended to put it in the `src.data` directory. After that, you can run the script:

```bash
python src/tlg_stats.py
```

## Issue solving

You may face an issure during installing `hazm` package related to `command 'gcc' failed`. To solve this problem:

```bash 
sudo apt-get install gcc
```
