import math
from pprint import pprint

users_ratings = []

# Create a matrix users in the first column and ratings in other columns
with open('users.csv', 'r') as file:
    for line in file:
        users_ratings.append([{
            'user_id': int(line.strip().split('|')[0]),
            'ratings_sum': 0,
            'ratings_count': 0,
            'most_similar_users': [],
            'recommended_item': None
        }])

# Fill the matrix based on users rating
# This matrix is not sparse
with open('ratings.csv', 'r') as file:
    for line in file:
        [user_id, item_id, rating] = map(int, line.strip().split('\t')[:3])

        users_ratings[user_id - 1][0]['ratings_sum'] += rating
        users_ratings[user_id - 1][0]['ratings_count'] += 1
        users_ratings[user_id - 1].append({
            'item_id': item_id,
            'user_rating': rating
        })


def limit_precision(number):
    str_number = str(number)
    splitted_number = str_number.split('.')

    if len(splitted_number) < 2:
        return number

    return float(splitted_number[0] + '.' + splitted_number[1][:2])


# i1 and i2 are user1 and user2 ratings
def cosine_similarity(i1, i2, avg1, avg2):
    ruab = 0
    rua = 0
    rub = 0

    for a in i1:
        for b in i2:
            if a['item_id'] == b['item_id']:
                a_adjusted = a['user_rating'] - avg1
                b_adjusted = b['user_rating'] - avg2

                ruab += a_adjusted * b_adjusted

                rua += a_adjusted ** 2
                rub += b_adjusted ** 2

    if rua == 0 or rub == 0:
        return None

    return ruab / (math.sqrt(rua) * math.sqrt(rub))


for row in users_ratings:
    user = row[0]
    avg = user['ratings_sum'] / user['ratings_count']

    # Five most similar users
    most_similar_users = []

    for comparing_row in users_ratings:
        comparing_user = comparing_row[0]

        # The most similar user is the user itself so to avoid this we won't compare it to itself
        if comparing_user['user_id'] == user['user_id']:
            continue

        comparing_avg = comparing_user['ratings_sum'] / comparing_user['ratings_count']

        similarity = cosine_similarity(row[1:], comparing_row[1:], avg, comparing_avg)

        if similarity is None:
            continue

        if len(most_similar_users) < 5:
            most_similar_users.append((similarity, comparing_user['user_id']))

            if len(most_similar_users) == 5:
                most_similar_users.sort(key=lambda i: i[0])

            continue

        if len(most_similar_users) == 5:
            for index, item in enumerate(most_similar_users):
                if similarity > item[0]:
                    most_similar_users[index] = (similarity, comparing_user['user_id'])
                    break

    user['most_similar_users'] = list(map(lambda i: [limit_precision(i[0]), i[1]], most_similar_users))

for row in users_ratings[:10]:
    pprint(row[:1])
