import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Union

import seaborn as sns
from loguru import logger
from matplotlib import pyplot as plt

from data import DATA_DIR


class tlg_top_users:
    def __init__(self, chat_json: Union[str, Path]):
        """
        a class to extract and plot the top users of a telegram chat based on a specific tag (e.g. #reply_ques)

        Arguments:
            chat_json {Union[str, Path]} -- the path to the chat json file (only the json file from telegram)
        """
        logger.info(f'Loading chat data from {chat_json}')
        # load data
        with open(DATA_DIR/chat_json) as data_file:
            self.chat_data = json.load(data_file)
            
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
    
    def get_user_data(self):
        """
        process the chat json file to extract info and statistics about users. finnaly save the metadata of users (users info) to a json file.
    
        """
        self.users_info = defaultdict(self.user_metadata)
        self.ques_id = set()
        
        logger.info('Processing chat data...')
        for msg in self.chat_data['messages']:
            # skip service messages (pin, join, etc)
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
            if not isinstance(msg['text'], str):
                for i in range(len(msg['text'])):
                    if not isinstance(msg['text'][i], str):
                        continue
                    if ('?' not in msg['text'][i]) and ('؟' not in msg['text'][i]):
                        continue
                
                    # add this message id as `question_id`
                    self.ques_id.add(msg['id'])
                    # This user ask a question, add to metadata (#ques_msg) of this user
                    self.users_info[msg['from_id']]['#ques_msg'] += 1
            
            if ('?' in msg['text']) or ('؟' in msg['text']):
                self.ques_id.add(msg['id'])
                self.users_info[msg['from_id']]['#ques_msg'] += 1
            
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
        top_users = dict(Counter({k: v[tag] for k, v in self.users_info.items()}).most_common(n))
        
        # get the usernames of the top n users
        top_usersnames = [self.users_info[i]['username'] for i in top_users] 
        
        # plot the top n users
        fig, ax = plt.subplots(figsize=figsize)
        sns.barplot(x=list(top_users.keys()), y=list(top_users.values()))
        ax.xaxis.set_ticklabels(top_usersnames, rotation=45, ha='right', rotation_mode='anchor')
        ax.set_title(f'Top {n} users by {tag}')
        
        logger.info(f'Saving plot to {save_path}')
        fig.savefig(save_path)
        
        
if __name__ == '__main__':
    user_stats = tlg_top_users('pytopia.json')
    user_stats.get_user_data()
    user_stats.plot_top_users(n=10, tag='#reply_ques', save_path='src/top_users.png')
    logger.info('Done!')