import math
Default_WPM = 200

def estimate_readtime (text, wpm= Default_WPM):
    words = text.split( )
    word_count = len(words)
    minutes = math.ceil( word_count/wpm)
    return minutes