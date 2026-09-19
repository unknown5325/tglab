import deep_translator

def translate_word(text):
    return deep_translator.MyMemoryTranslator(source='english', target='russian').translate(text)