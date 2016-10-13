def parse_stash_response(response, store=None):
    parsed_haikus = []

    for val in response['values']:
        if store is not None:
            if store.is_checked(val['id']):
                continue
            store.put_checked_id(val['id'])

        if is_haiku(val['description']):
            parsed_haikus.append(desc_to_haiku(val['description'], val['author']))
        else:
            print('Not an haiku: ' + val['description'])

    return parsed_haikus


def is_haiku(desc):
    lines = desc.split('\r\n')

    if len(lines) < 3:
        return False
    if '' in lines[0:3]:
        return False

    for line in lines[0:3]:
        if '*' in line:
            return False
        if len(line) > 50:
            return False
            # TODO more haiku checks

    return True


def desc_to_haiku(desc, author):
    lines = desc.split('\r\n')[0:3]
    haiku = ""
    for line in lines:
        haiku += "> " + line.strip() + "\n"

    author = author['user']['displayName'] if 'displayName' in author['user'] else author['user']['slug']

    return {'haiku': haiku, 'author': author}
