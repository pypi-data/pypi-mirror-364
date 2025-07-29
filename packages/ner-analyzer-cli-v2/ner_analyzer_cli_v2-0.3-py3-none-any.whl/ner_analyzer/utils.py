
def entity_frequency(entities):
    freq = {}
    for ent in entities:
        label = ent['label']
        freq[label] = freq.get(label, 0) + 1
    return freq
