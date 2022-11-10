import json
from pathlib import Path
from typing import Union

import arabic_reshaper
import demoji
from hazm import Normalizer, word_tokenize
from wordcloud import WordCloud

from data import DATA_DIR


class tlg_ChatStats:
    """Generate chat statistics and wordcloud from a telegram chat json file"""
    def __init__(self, chat_json: Union[Path, str], stop_words: Union[Path, str]): 
        """
        Arguments:
            chat_json {Union[Path, str]} -- path to the chat json file
            stop_words {Union[Path, str]} -- path to the stop words file
        """
        
        # load data
        with open(chat_json, encoding='UTF8') as f:
            self.chat_data = json.load(f)
            
        # load stopwords   
        with open(stop_words) as swf:
            self.stopwords = swf.read().split()
        
        # extract chat texts
        self.text_content = ""
        for msg in self.chat_data['messages']:
            # some chats are only contain text and without links 
            if isinstance(msg['text'], str):
                self.text_content += msg['text']
            
            # some chats are contains links > data type: list  
            if isinstance(msg['text'], list):
                # look up, where is messages in list
                for i in range(len(msg['text'])):
                    if isinstance(msg['text'][i], str):
                        self.text_content += msg['text'][i]
                        
        # pre-processing : normalize, tokenize, remove emojies ...
        normalizer = Normalizer()
        normal_text = normalizer.normalize(self.text_content)
        text_tokens = word_tokenize(normal_text)
        # remove stop words
        clean_tokens = [token for token in text_tokens if token not in self.stopwords]
        # remove emojies, half space and unicodes from
        full_text = ' '.join(clean_tokens)
        full_text = demoji.replace(full_text, ' ')
        full_text = full_text.replace('‌', ' ')
        full_text = full_text.replace('\u2066', ' ')
        full_text = full_text.replace('\u2069', ' ')
        full_text = full_text.replace('\U0001f979', ' ')
        full_text = full_text.replace('\U0001fae0', ' ')
        self.text_content = full_text.replace('\U0001fae1', ' ')
    
    def generate_wordcloud(self, 
            font_path:Union[Path, str], outputdir: Union[Path, str], 
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
        
        # Make text readable for a non-Arabic library like wordcloud
        self.text_content = arabic_reshaper.reshape(self.text_content)
        
        # Generate a word cloud image
        wordcloud = WordCloud(
            width=width, height=height, 
            font_path=str(font_path), 
            background_color=background_color
        ).generate(self.text_content)
        
        # save the picture
        wordcloud.to_file(str(Path(outputdir) / 'wordcloud.png'))
        

if __name__ == '__main__':
    chat_stats = tlg_ChatStats(
        chat_json=DATA_DIR / 'pytopia.json',
        stop_words=DATA_DIR / 'stopwords.txt' 
    )
    chat_stats.generate_wordcloud(
        outputdir=DATA_DIR,
        font_path=DATA_DIR / 'BHoma.ttf'
    )
    print('Done')
