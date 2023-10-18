"""This program serves as a comprehensive toolkit for analyzing and categorizing businesses using provided data.
It offers a range of crucial functionalities, including the calculation of Minkowski distances to assess business
similarities, conducting t-tests to evaluate profit changes, and categorizing businesses based on various criteria.

The "minkowski_distance" function allows for customizable distance calculations, while the "calculate_minkowski_distances"
function utilizes this to provide insights into business similarities by country.

On the other hand, the "calculate_t_test" function handles profit change significance testing, even in cases of missing
or invalid data, yielding precise statistical scores.

The "calculate_category_data" function categorizes businesses by industry and ranks them based on employee counts and profit
change percentages, enhancing our understanding of businesses within each category.

The "combine_t_test_and_minkowski" function merges t-test and Minkowski distance results, facilitating a comprehensive analysis
from both statistical and similarity-based perspectives.

The "main" function ties everything together and runs the functions.

"""

def minkowski_distance(x1, x2, p):
    if len(x1) != len(x2):
        raise ValueError("Input vectors must have the same dimensionality.")

    distance = 0
    for i in range(len(x1)):
        distance += abs(x1[i] - x2[i]) ** p

    return distance ** (1 / p)

def calculate_minkowski_distances(filename, p=3):
    country_data = {}

    with open(filename, 'r') as file:
        lines = file.readlines()

    header = lines[0].strip().split(',')
    employees_index = header.index("number of employees")
    median_salary_index = header.index("median Salary")

    for line in lines[1:]:
        row = line.strip().split(',')
        country = row[header.index("country")]
        employees = int(row[employees_index])
        median_salary = float(row[median_salary_index])

        if country not in country_data:
            country_data[country] = []

        country_data[country].append((employees, median_salary))
    country_distances = {}

    for country, points in country_data.items():
        x1 = [point[0] for point in points]
        x2 = [point[1] for point in points]
        minkowski_dist = minkowski_distance(x1, x2, p)
        country_distances[country] = round(minkowski_dist,4)

    return country_distances


def calculate_t_test(filename):
    profits_2020 = {}
    profits_2021 = {}

    with open(filename, 'r') as file:
        lines = file.readlines()

    header = lines[0].strip().split(',')
    profit_2020_index = header.index("profits in 2020(million)")
    profit_2021_index = header.index("profits in 2021(million)")

    for line in lines[1:]:
        row = line.strip().split(',')
        country = row[header.index("country")]

        try:
            profit_2020 = float(row[profit_2020_index])
            profit_2021 = float(row[profit_2021_index])
        except ValueError:
            print(f"Skipping row for country {country} due to invalid profit values.")
            continue

        if country not in profits_2020:
            profits_2020[country] = []
        if country not in profits_2021:
            profits_2021[country] = []

        profits_2020[country].append(profit_2020)
        profits_2021[country].append(profit_2021)

    t_test_scores = {}

    for country in profits_2020:
        profits_2020_values = profits_2020[country]
        profits_2021_values = profits_2021[country]

        n1 = len(profits_2020_values)
        n2 = len(profits_2021_values)

        mean_2020 = sum(profits_2020_values) / n1
        mean_2021 = sum(profits_2021_values) / n2

        sum_2020 = sum([(x - mean_2020) ** 2 for x in profits_2020_values])
        std_dev_2020 = (sum_2020 / (n1 - 1)) ** 0.5

        sum_2021 = sum([(x - mean_2021) ** 2 for x in profits_2021_values])
        std_dev_2021 = (sum_2021 / (n2 - 1)) ** 0.5

        t_statistic = (mean_2020 - mean_2021) / ((std_dev_2020 ** 2 / n1) + (std_dev_2021 ** 2 / n2)) ** 0.5

        t_test_scores[country] = round(t_statistic, 4)

    return t_test_scores


def combine_t_test_and_minkowski(filename, p=3):
    t_test_results = calculate_t_test(filename)
    minkowski_results = calculate_minkowski_distances(filename, p)

    combined_results = {}

    for country in t_test_results.keys():
        if country in minkowski_results:
            combined_results[country] = [t_test_results[country], minkowski_results[country]]

    return combined_results


def calculate_category_data(csv_data):
    category_data = {}

    for row in csv_data[1:]:

        try:
            category = row[5].lower()
            org_id = row[0]
            employees = int(row[6])
            profit_2020 = float(row[8])
            profit_2021 = float(row[9])

            if employees <= 0:
                continue

            profit_change_percentage = abs(((profit_2021 - profit_2020) / profit_2020) * 100)
            profit_change_percentage = f"{profit_change_percentage:.4f}"

            if category not in category_data:
                category_data[category] = {}

            if org_id not in category_data[category]:
                category_data[category][org_id] = []

            category_data[category][org_id].append([employees, profit_change_percentage])
        except (ValueError, IndexError):
            continue

    for category, org_data in category_data.items():
        sorted_orgs = sorted(org_data.items(), key=lambda x: sum(float(data[0]) for data in x[1]), reverse=True)
        for rank, (org_id, org_info) in enumerate(sorted_orgs, start=1):
            for data in org_info:
                data.append(rank)

    return category_data

def main(filename):
    output1 = combine_t_test_and_minkowski(filename)
    data = []

    with open(filename, 'r') as file:
        lines = file.readlines()
        for line in lines:
            row = line.strip().split(',')
            data.append(row)

    category_data = calculate_category_data(data)
    output2 = category_data
    return output1, output2

