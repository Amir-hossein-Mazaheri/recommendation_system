import math
import json
import os
from os.path import exists

users_ratings = []


def fill_users_ratings():
    if exists('without_prediction.json'):
        with open('without_prediction.json', 'r') as without_prediction:
            global users_ratings
            users_ratings = json.load(without_prediction)

            print("Loaded users ratings(without prediction) from file :)")

        return

    items_file_encoding = 'ISO-8859-1'

    # Create a matrix users in the first column and ratings in other columns
    with open('users.csv', 'r') as users_file:
        for line in users_file:
            users_ratings.append([{
                'user_id': int(line.strip().split('|')[0]),
                'ratings_avg': float(0),
                'ratings_count': 0,
            }])

    with open('items.csv', 'r', encoding=items_file_encoding) as items_file:
        for user_row in users_ratings:
            for line in items_file:
                [item_id, item_title] = line.strip().split('|')[:2]

                item = {
                    'item_id': int(item_id),
                    'item_title': item_title,
                    'similarities': [],
                    'prediction': None,
                    'user_rating': None
                }

                user_row.append(item)

            items_file.seek(0)

    # Fill ratings in the correct position
    # This matrix is very sparse
    with open('ratings.csv', 'r') as users_file:
        for line in users_file:
            [user_id, item_id, rating] = map(int, line.strip().split('\t')[:3])

            users_ratings[user_id - 1][0]['ratings_avg'] = (users_ratings[user_id - 1][0]['ratings_avg'] *
                                                            users_ratings[user_id - 1][0]['ratings_count'] + rating) / (
                                                                   users_ratings[user_id - 1][0]['ratings_count'] + 1)
            users_ratings[user_id - 1][0]['ratings_count'] += 1
            users_ratings[user_id - 1][item_id]['user_rating'] = rating

    for item in users_ratings[0][1:]:
        fill_similarities(item['item_id'])

    with open('without_prediction.json', 'w+') as without_prediction:
        without_prediction.write(json.dumps(users_ratings))

        print("Saved users ratings(without prediction) to file :)")


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
        rub += i2_adjusted_rating ** 2

    if rub == 0 or rua == 0:
        return 0

    return ruab / (math.sqrt(rua) * math.sqrt(rub))


def fill_similarities(iid):
    similarities = []
    fill_item = users_ratings[0][iid]

    for comparing_item in users_ratings[0][1:]:
        if fill_item['item_id'] == comparing_item['item_id']:
            continue

        similarity = cosine_similarity(fill_item['item_id'], comparing_item['item_id'])

        similarities.append((similarity, comparing_item['item_id']))

    fill_item['similarities'] = sorted(similarities, key=lambda i: i[0], reverse=True)


def predict(uid, iid):
    similarities = users_ratings[0][iid]['similarities']
    count = 0
    top = 0
    bottom = 0

    for similar_item in similarities:
        for rated_item in users_ratings[uid - 1][1:]:
            if count == 10:
                break

            if rated_item['user_rating'] is None:
                continue

            if rated_item['item_id'] == similar_item[1]:
                count += 1

                top += similar_item[0] * users_ratings[uid - 1][similar_item[1]]['user_rating']
                bottom += similar_item[0]

    if bottom == 0:
        return 0

    return top / bottom


def fill_prediction():
    if exists('prediction.json'):
        with open('prediction.json', 'r') as prediction:
            global users_ratings
            users_ratings = json.load(prediction)

            print("Loaded users ratings from file :)")

        return

    # Fill the users ratings matrix also fill the similarities
    fill_users_ratings()

    for row in users_ratings:
        for column in row[1:]:
            column['prediction'] = predict(row[0]['user_id'], column['item_id'])

    with open('prediction.json', 'w+') as file:
        json_users_ratings = json.dumps(users_ratings)

        file.write(json_users_ratings)


# Return a dictionary which keys are user id and value is top 10 movies recommended by item-item method
def recommend():
    recommendations = {}

    # Calculate everything including all similarities,
    # and prediction for each user for each item even the ones that user rated for testing
    fill_prediction()

    for row in users_ratings:
        sorted_item_based_on_prediction = sorted(row[1:],
                                                 key=lambda item: -10000000 if item['user_rating'] is not None else
                                                 item['prediction'], reverse=True)

        recommendations[row[0]['user_id']] = list(map(
            lambda sorted_item: (sorted_item['item_id'], sorted_item['item_title'], sorted_item['prediction']),
            sorted_item_based_on_prediction[:10]))

    return recommendations


def clear_terminal():
    # Check the operating system and clear the terminal accordingly
    if os.name == 'nt':  # For Windows
        os.system('cls')
    else:  # For macOS and Linux
        os.system('clear')


# Calculate the Mean Absolute Error(MAE) and Root Mean Squared Error(RMSE)
def get_the_mae_rmse():
    print("Calculating mean absolute error and root mean squared error...")

    mae = 0
    rmse = 0
    count = 0

    for row in users_ratings:
        for column in row[1:]:
            if column['user_rating'] is None:
                continue

            common = abs(column['user_rating'] - column['prediction'])
            mae += common
            rmse += common ** 2
            count += 1

    clear_terminal()

    return mae / count, rmse / count


r = recommend()
mae, rmse = get_the_mae_rmse()

while True:
    try:
        uid = int(input("Give the user id to see recommendations: "))
        clear_terminal()

        recommended = r[uid]

        for i, item in enumerate(recommended):
            print(f"{i + 1}. {item[1]}, prediction: {item[2]:.1f}")

        print(
            f"\033[31mAccuracy prediction based on of Mean Absolute Error: {mae:.2f}, Root Mean Squared Error: {rmse:.2f}\033[0m")
    except KeyError:
        print("Invalid user id")
