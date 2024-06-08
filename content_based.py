import math
import os


def get_items_vector():
    # movie id 0 | movie title 1 | release date 2 | video release date 3 |
    # IMDb URL 4 | unknown 5 | Action 6 | Adventure 7 | Animation 8 |
    # Children's 8 | Comedy 10 | Crime 11 | Documentary 12 | Drama 13 | Fantasy 14 |
    # Film - Noir 15 | Horror 16 | Musical 17 | Mystery 18 | Romance 19 | Sci - Fi 20 |
    # Thriller 21 | War 22 | Western 23
    items_matrix = {}
    items_file_encoding = 'ISO-8859-1'

    max_year = None
    min_year = None

    with open('items.csv', 'r', encoding=items_file_encoding) as file:
        for line in file:
            splitted_line = line.strip().split("|")
            item_title = splitted_line[1]
            item_id = int(splitted_line[0])
            splitted_release = splitted_line[2].split("-")
            fake_year = False

            if len(splitted_release) != 3:
                fake_year = True

            year = None if fake_year else int(splitted_release[2])

            if max_year is None and min_year is None:
                max_year = year
                min_year = year

            if year is not None:
                if year > max_year:
                    max_year = year

                if year < min_year:
                    min_year = year

            items_matrix[item_id] = [item_title, year, *list(map(int, splitted_line[5:]))]

    # (year - min_year) / (max_year - min_year)
    # This formula normalize the year to be between 0 and 1
    for key, value in items_matrix.items():
        year = value[1]
        items_matrix[key][1] = 0.5 if year is None else (year - min_year) / (max_year - min_year)

    return items_matrix


def get_users_ratings():
    # Keys are tuple of user_id and item_id
    users_ratings = []

    with open('ratings.csv', 'r') as file:
        for line in file:
            user_id, item_id, rating = list(map(int, line.strip().split("\t")[:3]))

            users_ratings.append((user_id, item_id, rating))

    return users_ratings


def get_user_profile(user_id, users_ratings, items_vector):
    # User profile is a vector like movie vector but user's ratings are considered
    # for safety and future use I calculated the len of vector based on available
    # measures also you could replace it with 20, 19 genres and year
    user_profile = [0] * len(list(items_vector.values())[0][1:])
    ratings_sum = 0

    for rating in users_ratings:
        if rating[0] == user_id:
            item_id = rating[1]
            user_rating = rating[2]
            item = items_vector[item_id][1:]

            ratings_sum += user_rating

            for i in range(len(user_profile)):
                user_profile[i] += item[i] * user_rating

    return list(map(lambda x: x / ratings_sum, user_profile))


def cosine_similarity(vec1, vec2):
    min_len = min(len(vec1), len(vec2))
    ruab = 0
    rua = 0
    rub = 0

    for i in range(min_len):
        ruab += vec1[i] * vec2[i]
        rua += vec1[i] ** 2
        rub += vec2[i] ** 2

    return ruab / (math.sqrt(rua) * math.sqrt(rub))


def recommend_for_user(user_id, users_ratings, items_vector, limit=None):
    user_profile = get_user_profile(user_id, users_ratings, items_vector)
    similarities = []

    for key, value in items_vector.items():
        # To ignore users rated items
        for rating in users_ratings:
            if key == rating[1]:
                continue

        similarity = cosine_similarity(user_profile, value[1:])
        similarities.append((key, similarity))

    return sorted(similarities, key=lambda x: x[1], reverse=True)[:limit]


def clear_terminal():
    # Check the operating system and clear the terminal accordingly
    if os.name == 'nt':  # For Windows
        os.system('cls')
    else:  # For macOS and Linux
        os.system('clear')


# r = recommend_for_user(1, get_users_ratings(), get_items_vector(), 10)
u_ratings = get_users_ratings()
i_vector = get_items_vector()

limit = input("How many recommendations do you want to see(can't be changed) - skip if you want to see all: ")

while True:
    uid = int(input("Give the user id to see recommendations: "))
    clear_terminal()

    recommendations = recommend_for_user(uid, u_ratings, i_vector, None if limit.strip() == '' else int(limit))

    # for i, item in enumerate(recommended):
    #     print(f"{i + 1}. {item[1]}, prediction: {item[2]:.1f}")

    for i, item in enumerate(recommendations):
        print(f"{i + 1}. {i_vector[item[0]][0]}")
