import logging


def parse_stash_response(response, repo_id, store=None):
    logging.debug('Parsing stash response: ' + str(response))
    parsed_haikus = []

    for val in response['values']:
        if store is not None:
            if store.is_checked('{}{}'.format(repo_id, val['id'])):
                logging.debug('Response {} has been parsed before, skipping'.format(val['id']))
                continue
            store.put_checked_id('{}{}'.format(repo_id, val['id']))

        if 'description' in val and is_haiku(val['description']):
            parsed_haikus.append(desc_to_haiku(val['description'], val['author'], val['links']['self']))
            logging.debug('Found an haiku: ' + val['description'])
        else:
            logging.debug('Not an haiku: {} in {}'.format(val['id'], repo_id))
            if 'description' in val:
                logging.debug('{}'.format(val['description']))

    return parsed_haikus


def is_haiku(desc):
    if isinstance(desc, list):
        lines = desc
    else:
        lines = desc.replace('\r', '').split('\n')

    if len(lines) < 3:
        logging.debug('Less than 3 ({}) lines, not an haiku'.format(len(lines)))
        return False
    if '' in lines[0:3]:
        logging.debug('One of the first 3 lines empty, not an haiku')
        return False

    for line in lines[0:3]:
        if '*' in line:
            logging.debug('One of the first 3 lines is a list, not an haiku')
            return False
        if len(line) > 50:
            logging.debug('One of the first 3 lines has length more than 50, not an haiku')
            return False
        if len(line) < 5:
            logging.debug('One of the first 3 lines has length less than 5, not an haiku')
            return False
        # TODO more haiku checks

    return True


def desc_to_haiku(desc, author, links):
    lines = desc.replace('\r', '').split('\n')[0:3]
    haiku = ""
    for line in lines:
        haiku += line.strip() + "\n"

    author = author['user']['displayName'] if 'displayName' in author['user'] else author['user']['slug']
    link = links[0]['href']

    return {'haiku': haiku, 'author': author, 'link': link}
