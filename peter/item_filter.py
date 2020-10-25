threshold = 0.45

def find_relevant(items, title):
    result = []
    keywords = title.split(' ')

    for _, item in enumerate(items, start=1):
        item_title = item.get('title').split(' ')

        score = len(set.intersection(set(item_title), set(keywords)))
        ratio = score / len(keywords)

        if ratio > threshold:
            result.append((item, score))

    result.sort(key=lambda t: t[1])
    result.reverse()

    print([x.get('title') for (x, _) in result[:5]])

    return [x for (x, _) in result[:4]]