import math
from pprint import pprint

users_ratings = []

items_file_encoding = 'ISO-8859-1'

# Create a matrix users in the first column and ratings in other columns
with open('users.csv', 'r') as file:
    for line in file:
        users_ratings.append([{
            'user_id': int(line.strip().split('|')[0]),
            'ratings_avg': float(0),
            'ratings_count': 0,
        }])

with open('items.csv', 'r', encoding=items_file_encoding) as file:
    for row in users_ratings:
        for line in file:
            [item_id, item_title] = line.strip().split('|')[:2]

            item = {
                'item_id': int(item_id),
                'item_title': item_title,
                'most_similar_items': None,
                'prediction': None,
                'user_rating': None
            }

            row.append(item)

        file.seek(0)

# Fill ratings in the correct position
# This matrix is very sparse
with open('ratings.csv', 'r') as file:
    for line in file:
        [user_id, item_id, rating] = map(int, line.strip().split('\t')[:3])

        users_ratings[user_id - 1][0]['ratings_avg'] = (users_ratings[user_id - 1][0]['ratings_avg'] *
                                                        users_ratings[user_id - 1][0]['ratings_count'] + rating) / (
                                                               users_ratings[user_id - 1][0]['ratings_count'] + 1)
        users_ratings[user_id - 1][0]['ratings_count'] += 1
        users_ratings[user_id - 1][item_id]['user_rating'] = rating


def limit_precision(number):
    str_number = str(number)
    splitted_number = str_number.split('.')

    if len(splitted_number) < 2:
        return number

    return float(splitted_number[0] + '.' + splitted_number[1][:2])


# i1 and i2 are user1 and user2 ratings
def cosine_similarity(i1_id, i2_id):
    ruab = 0
    rua = 0
    rub = 0

    for user_rating in users_ratings:
        i1_rating = user_rating[i1_id]['user_rating']
        i2_rating = user_rating[i2_id]['user_rating']

        if i1_rating is None or i2_rating is None:
            continue

        i1_adjusted_rating = i1_rating - user_rating[0]['ratings_avg']
        i2_adjusted_rating = i2_rating - user_rating[0]['ratings_avg']

        ruab += i1_adjusted_rating * i2_adjusted_rating
        rua += i1_adjusted_rating ** 2
        rub += i2_adjusted_rating

    return ruab / (math.sqrt(rua) * math.sqrt(rub))

# for row in users_ratings:
#     print(row[0])
#     none_count = 0
#     count = 0
#
#     for item in row[1:]:
#         if item['user_rating'] is None:
#             none_count += 1
#         else:
#             count += 1
#
#     print(count, none_count, count + none_count)
