from collections import Counter

def counts(text):
    words, current = ([], [])
    for ch in text:
        if ch.isalpha():
            current.append(ch)
        elif current:
            words.append(''.join(current).casefold())
            current = []
    if current:
        words.append(''.join(current).casefold())
    return Counter(words)
