import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Union

import arabic_reshaper
import demoji
import seaborn as sns
from hazm import Normalizer, sent_tokenize, word_tokenize
from loguru import logger
from matplotlib import pyplot as plt
from tqdm import tqdm
from wordcloud import WordCloud

from data import DATA_DIR


class tlg_ChatStats:
    def __init__(self, chat_json: Union[Path, str], stop_words: Union[Path, str]):
        """
        A class for extracting statistics from Telegram chat json file

        Arguments:
            chat_json {Union[Path, str]} -- Path to the chat json file
            stop_words {Union[Path, str]} -- Path to the stop words file
        """

        self.normalizer = Normalizer()

        # load data
        logger.info(f'Loading data from {chat_json}')
        with open(DATA_DIR / chat_json, encoding='UTF8') as f:
            self.chat_data = json.load(f)

        # load stopwords
        logger.info('Loading stopwords')
        stop_words = open(DATA_DIR / stop_words).readlines()
        # remove \n from each line
        stop_words = map(lambda x: x.strip(), stop_words)
        # normalize stop words and remove duplicates
        self.stop_words = set(map(self.normalizer.normalize, stop_words))

    @staticmethod
    def user_metadata():
        """
        a template for recording user metadata (username, user_id, number of messages, questions, replies, etc)

        Returns:
            dict -- default metadata for users
        """
        default_info = {
            'username': str(),
            'user_id': str(),
            '#messages': int(),
            '#ques_msg': int(),
            '#reply': int(),
            '#reply_ques': int()
        }
        return default_info

    def de_emojify(self, text: str) -> str:
        """
        Remove emojies and unicode characters from text with regex and demoji module

        Arguments:
            text {str} -- text contains emojies and unicode characters

        Returns:
            str -- final text without emojies and unicode characters
        """
        regrex_pattern = re.compile(
            pattern="[\u2069\u2066]+", flags=re.UNICODE)
        text = regrex_pattern.sub('', text)
        return demoji.replace(text, " ")

    def remove_stopwords(self, text: str) -> str:
        """
        Remove stopwords from text by normalizing it and using hazm word_tokenize

        Arguments:
            text {str} -- the telegram chat text

        Returns:
            str -- the text without stopwords
        """
        tokens = word_tokenize(self.normalizer.normalize(text))
        tokens = list(filter(lambda item: item not in self.stop_words, tokens))
        return ' '.join(tokens)

    def is_msg_question(self, msg: dict):
        """
        Check if the message is a question or not. if yes, add chat id to a set of questions id and 
        add 1 to the number of questions of this user asked

        Arguments:
            msg {dict} -- a message from the chat json file
        """
        sentences = sent_tokenize(msg['text'])
        for sent in sentences:
            if ('?' in sent) or ('؟' in sent):
                self.ques_id.add(msg['id'])
                self.users_info[msg['from_id']]['#ques_msg'] += 1

    def rebuild_msg(self, msg: dict) -> str:
        """
        Rebuild the message from a list of strings, links, etc to a single string

        Arguments:
            msg {dict} -- a message from the chat json file

        Returns:
            str -- the text of the message that is in list type (contains link, mention, text, etc)
        """
        msg_text = ''
        for i in range(len(msg['text'])):
            if isinstance(msg['text'][i], str):
                msg_text += msg['text'][i]
        return msg_text

    def chat_process(self):
        """
        Extract chat texts and record user metadata (statistics)
        """
        logger.info('Extracting chat texts')
        # the all chat text for wordcloud
        self.text_content = ""
        # a dict for recording user metadata
        self.users_info = defaultdict(self.user_metadata)
        # a set for recording messages id that are questions
        self.ques_id = set()

        for msg in tqdm(self.chat_data['messages'], 'Processing messages...'):

            # skip service messages (like pin, join, etc)
            if msg['type'] != 'message':
                continue

            # record the user id and name, if it's not there (for first time)
            if not self.users_info[msg['from_id']]['username']:
                self.users_info[msg['from_id']]['username'] = msg['from']
                self.users_info[msg['from_id']]['user_id'] = msg['from_id']

            # count and record the number of messages from this user_id
            self.users_info[msg['from_id']]['#messages'] += 1

            # is this message a question? Assume any message with '?' or '؟' is question !!
            # messages are in two type, in `str` or a `list` (contains link, mention, text, etc)
            if isinstance(msg['text'], str):
                self.text_content += f" {self.remove_stopwords(msg['text'])}"
                self.is_msg_question(msg)

            # some chats are contains links > data type: list
            else:
                msg['text'] = self.rebuild_msg(msg)
                self.text_content += f" {self.remove_stopwords(msg['text'])}"
                self.is_msg_question(msg)

            # replies: the reply is on the question? or just a simple message?
            if not msg.get('reply_to_message_id'):
                continue

            # if this message is a reply to a question, add to metadata (#reply_ques and #reply) of this user
            if msg['reply_to_message_id'] in self.ques_id:
                self.users_info[msg['from_id']]['#reply_ques'] += 1
                self.users_info[msg['from_id']]['#reply'] += 1
            else:
                # if this message is a simple reply (not to a question), add to metadata (#reply) of this user
                self.users_info[msg['from_id']]['#reply'] += 1

        # removing emojies and unicode characters
        # And make text readable for a non-Arabic library like wordcloud
        self.text_content = arabic_reshaper.reshape(
            self.de_emojify(self.text_content))

        # save the user metadata and statistics to json file
        logger.info(f'Saving user metadata and statistics to {DATA_DIR}')
        with open(DATA_DIR/'users_info.json', 'w') as f:
            json.dump(self.users_info, f, indent=4)

    def plot_top_users(self, n: int = 10, tag: str = '#reply_ques', save_path: str = './top_users.png', figsize: tuple = (12, 9)):
        """
        plot the top (n) users based on a sepecific tag (e.g. #reply_ques)

        Keyword Arguments:
            n {int} -- number of top users (default: {10})
            tag {str} -- the compression based on (default: {'#reply_ques'}) -- 
            the possible tags are: {
                #messages: number of messages a user send,
                #ques_msg: number of questions a user ask,
                #reply: number of replies a user send,
                #reply_ques: number of replies to questions a user send
            }
            save_path {str} -- the path to save figure (default: {'./top_users.png'})
            figsize {tuple} -- the figure size (default: {(12, 9)})
        """

        logger.info(f'Plotting top {n} users')
        # get the top n users (id: number of {tag})
        top_users = dict(
            Counter({k: v[tag] for k, v in self.users_info.items()}).most_common(n))

        # get the usernames of the top n users
        top_usersnames = [self.users_info[i]['username'] for i in top_users]

        # plot the top n users
        fig, ax = plt.subplots(figsize=figsize)
        ax.set(
            title=f'Top {n} Users by {tag}',
            xlabel='Users',
            ylabel=f'{tag}',
        )
        sns.set(
            font_scale=3,
            style='whitegrid',
        )
        sns.barplot(
            y=list(top_users.values()),
            x=list(top_users.keys()),
            ax=ax
        )
        ax.xaxis.set_ticklabels(top_usersnames, rotation=45, ha='right',
                                rotation_mode='anchor')
        logger.info(f'Saving plot to {save_path}')
        fig.savefig(save_path)

    def generate_wordcloud(self,
                           font_path: Union[Path, str], outputdir: Union[Path, str],
                           width=1200, height=1200,
                           background_color='white'
                           ) -> None:
        """
        generate wordcloud from chat data

        Arguments:
            font_path {Union[Path, str]} -- path to the font file (.ttf)

            outputdir {Union[Path, str]} -- destination directory to save the wordcloud image

        Keyword Arguments:
            width {int} -- width of wordcloud picture (default: {1200})
            height {int} -- height of wordcloud picture (default: {1200})
            background_color {str} -- background color of wordcloud picture (default: {'white'})
        """
        # Generate a word cloud image
        logger.info('Generating wordcloud ...')
        wordcloud = WordCloud(
            width=width, height=height,
            font_path=str(font_path),
            background_color=background_color
        ).generate(self.text_content)
        # save the picture
        logger.info(f'Saving wordcloud to {outputdir} ...')
        wordcloud.to_file(str(Path(outputdir) / 'wordcloud.png'))


if __name__ == '__main__':
    chat_stats = tlg_ChatStats(
        chat_json=DATA_DIR / 'pytopia.json',
        stop_words=DATA_DIR / 'stopwords.txt'
    )
    chat_stats.chat_process()
    chat_stats.generate_wordcloud(
        outputdir='./src',
        font_path=DATA_DIR / 'BHoma.ttf'
    )
    chat_stats.plot_top_users(n=10, tag='#reply_ques',
                              save_path='src/top_users.png')
    logger.info('Done!')
