from collections import Counter
import matplotlib.pyplot as plt
import networkx as nx
import sys
import time
from TwitterAPI import TwitterAPI

consumer_key = "IGEOWEQXQcFczZRosZbGHgmMG"
consumer_secret = "zCvrt86mUAoOWDqOJeKSfUKhdtMj1pSqve2tekKemLfQQApmiO"
access_token = "1161834823880626176-OlzCerM1DAyf0XAzh6BP1bXSw5HeUy"
access_token_secret = "zLWr6C2Q0AoNQkz61aj2m8GUUNFEJvfKYVyXCflLx39eT"


def get_twitter():
    return TwitterAPI(consumer_key, consumer_secret, access_token, access_token_secret)


def read_screen_names(filename):
    list_user = []
    for i in open(filename, 'r'):
        list_user.append(i)

    for x in range(len(list_user)):
        list_user[x] = list_user[x][:-1]
    return list_user
    pass

def robust_request(twitter, resource, params, max_tries=5):
  
    for i in range(max_tries):
        request = twitter.request(resource, params)
        if request.status_code == 200:
            return request
        else:
            print('Got error %s \nsleeping for 15 minutes.' % request.text)
            sys.stderr.flush()
            time.sleep(61 * 15)


def get_users(twitter, screen_names):
    
    return  twitter.request('users/lookup', {'screen_name':screen_names}).json()
    pass


def get_friends(twitter, screen_name):
    
    list_friends = twitter.request('friends/ids', {'screen_name':screen_name}).json()
    friends = sorted(list_friends['ids'])
    return friends
    pass


def add_all_friends(twitter, users):
    
    for x in range(len(users)):
        users[x]['friends'] = get_friends(twitter, users[x]['screen_name'])

    
    pass


def print_num_friends(users):
    
    for u in users:
        print( "%s %d\n" % (str(u['screen_name']), len(u['friends'])) )
    pass


def count_friends(users):
    
    c = Counter()
    for u in users:
        c += Counter(iter(u['friends']))

    return c
    pass


def friend_overlap(users):

    overlap_list = []
    for u1 in users:
        for u2 in users:
            if u1 != u2 and users.index(u1) > users.index(u2) :
                num_of_overlap = 0
                for f1 in u1['friends']:
                    for f2 in u2['friends']:
                        if f1 == f2:
                            num_of_overlap += 1
                overlap_list.append( [ u1['screen_name'],
                                       u2['screen_name'],
                                       num_of_overlap ] ) 

    overlap_list = sorted(overlap_list, key=lambda x: x[2], reverse=True)
    for i in overlap_list:
        if i[0] > i[1]:
            i[0], i[1] = i[1], i[0]

    ret_list = []
    for n in overlap_list:
        tup = (n[0], n[1], n[2])
        ret_list.append(tup)

    return ret_list
    pass


def followed_by_hillary_and_donald(users, twitter):

    id = ""
    for i in users[2]['friends']:
        for n in users[3]['friends']:
            if i == n:
                id = i
                break

    match_user = twitter.request('users/lookup', {'user_id':id}).json()
    return [match_user[0]['screen_name']]
    pass


def create_graph(users, friend_counts):
   
    list_friend = []
    edges = []
    list_friend = [i for i in friend_counts if friend_counts[i]>1]
    graph = nx.DiGraph()

    for u in users:
        graph.add_node(u['screen_name'])
        f = set(list_friend) & set(u['friends'])
        for i in f:
            tup = (u['screen_name'], i)
            edges.append(tup)

    graph.add_edges_from(edges)
    return graph

    pass


def draw_network(graph, users, filename):

    label = {n:n if type(n)==str  else '' for n in graph.nodes()}
    plt.figure(figsize=(12,12))
    nx.draw_networkx(graph, node_color='r', labels=label, width=.1, node_size=100)
    plt.axis("off")
    plt.savefig(filename)
    plt.show()

    pass


def main():
    twitter = get_twitter()
    screen_names = read_screen_names('candidates.txt')
    print('Established Twitter connection.')
    print('Read screen names: %s' % screen_names)
    users = sorted(get_users(twitter, screen_names), key=lambda x: x['screen_name'])
    print('found %d users with screen_names %s' %(len(users), str([u['screen_name'] for u in users])))
    add_all_friends(twitter, users)
    print('Friends per candidate:')
    print_num_friends(users)
    friend_counts = count_friends(users)
    print('Most common friends:\n%s' % str(friend_counts.most_common(5)))
    print('Friend Overlap:\n%s' % str(friend_overlap(users)))
    print('User followed by Hillary and Donald: %s' % followed_by_hillary_and_donald(users, twitter))

    graph = create_graph(users, friend_counts)
    print('graph has %s nodes and %s edges' % (len(graph.nodes()), len(graph.edges())))
    draw_network(graph, users, 'network.png')
    print('network drawn to network.png')


if __name__ == '__main__':
    main()
