# Telegram Chat Stata

Give a telegram chat json file and after processing, get a word cloud from. Another feature is to get the most active users in the chat or who answered the most questions.

## How To Run

After cloning the repo, you need to install the requirements:

```bash
pip install -r requirements.txt
```

Next, you have to download a persian font, `BHoma.ttf`, and put it in `src.data` directory. Then you need to get a telegram chat `json` file. It's recommended to put it in the `src.data` directory. After that, you can run the script:

```bash
python src/chat_stats.py
```
## Issue solving

You may face an issure during installing `hazm` package related to `command 'gcc' failed`. To solve this problem:

```bash 
sudo apt-get install gcc
```
