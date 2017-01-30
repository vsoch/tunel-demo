import os
from logman import bot

def get_cache(base=None):
    '''get_cache returns a path to the user's home directory
    :param base: the base directory to use. If not specified, 
    uses home as a default
    '''
    if base == None:
        base = os.environ["HOME"]
    cache_dir = "%s/.tunel" %(base)
    if not os.path.exists(cache_dir):
        bot.logger.info("Creating tunel cache at %s", cache_dir)
        os.mkdir(cache_dir)
    return cache_dir
