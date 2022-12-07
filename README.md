# Telegram Chat Stata

The project conducts a simple analysis on a telegram chat json file. There are two main scripts in the project with the following scope:
`chat_stats.py` process over the json file to generate a word cloud from. By runing the `top_users.py` script, you get the statistics of the users on a json file and a bar chart which shows top `n` users. 

> **Note**: The statistics of the users will be saved in a `json` file in `src.data` directory.

## How To Run

After cloning the repo, you need to install the requirements:

```bash
pip install -r requirements.txt
```

Next, you have to download a persian font, `BHoma.ttf`, and put it in `src.data` directory. Then you need to get a telegram chat `json` file. It's recommended to put it in the `src.data` directory. After that, you can run the script:

```bash
python src/chat_stats.py
```

```bash
python src/top_users.py
```

## Issue solving

You may face an issure during installing `hazm` package related to `command 'gcc' failed`. To solve this problem:

```bash 
sudo apt-get install gcc
```
