from collections import defaultdict
from datetime import datetime

import numpy
import unicodecsv


# ------------------------------
# FUNCTION: read_csv
# Reads csv file using name and returns as list of dictionaries
# ------------------------------
def read_csv(param):
    with open(param, "rb") as file:
        reader = unicodecsv.DictReader(file)
        return list(reader)


# ------------------------------
# FUNCTION: parse_date
# Read date string and returns as datetime object
# ------------------------------
def parse_date(param):
    if param:
        return datetime.strptime(param, "%Y-%m-%d")
    else:
        return None


# ------------------------------
# FUNCTION: get_unique
# Get set of unique student numbers in dataset and return them
# ------------------------------
def get_unique(data):
    unique_students = set()
    for each in data:
        unique_students.add(each["account_key"])
    return unique_students


# ------------------------------
# FUNCTION: remove_test_accounts
# Creates new dataset without test account numbers and returns it
# ------------------------------
def remove_test_accounts(data, test_accs):
    new_data = []
    for each in data:
        if each["account_key"] not in test_accs:
            new_data.append(each)
    return new_data


# ------------------------------
# FUNCTION: within_one_week
# Determine if difference if difference between dates is less than 7 days
# ------------------------------
def within_one_week(join_date, engage_date):
    time_difference = engage_date - join_date
    return 7 > time_difference.days >= 0


# ------------------------------
# FUNCTION: get_avg
# Get mean, standard deviation, minimum and maximum and student with max, of column being analysed
# ------------------------------
def get_avg(paid_students_first_week, column):
    engagement_by_acc = defaultdict(list)
    for each in paid_students_first_week:
        engagement_by_acc[each["account_key"]].append(each)
    acc_stats = {}  # Account statistics being analysed
    for k, v in engagement_by_acc.items():
        stat = 0
        for each in v:
            stat += each[column]
        acc_stats[k] = stat
    acc_stats_values = list(acc_stats.values())

    max_student = (0, 0)
    for k, v in acc_stats.items():
        if v > max_student[1]:
            max_student = (k, v)

    return {"average": numpy.mean(acc_stats_values), "std_dev": numpy.std(acc_stats_values),
            "minimum": numpy.min(acc_stats_values),
            "maximum": numpy.max(acc_stats_values), "max_student": max_student}


# ------------------------------
# FUNCTION: visualise_column
#
# ------------------------------
def visualise_column(dataset, column_name, title):
    column = []
    for each in dataset:
        column.append(each[column_name])
    import matplotlib.pyplot as plt
    plt.hist(column, bins=8)
    plt.title(title)
    plt.xlabel(column_name)
    plt.ylabel("num_students")
    plt.show()


# ------------------------------
# FUNCTION: my_main
# ------------------------------
def my_main():
    # Read enrollments and fix data types
    enrollments = read_csv("enrollments.csv")
    for each in enrollments:
        each["account_key"] = int(each["account_key"])
        each["join_date"] = parse_date(each["join_date"])
        each["is_canceled"] = each["is_canceled"] == "True"
        each["is_udacity"] = each["is_udacity"] == "True"
        if each["is_canceled"]:
            each["cancel_date"] = parse_date(each["cancel_date"])
            each["days_to_cancel"] = int(each["days_to_cancel"])

    # Read engagements and fix data types
    daily_engagements = read_csv("daily_engagement.csv")
    for each in daily_engagements:
        each["acct"] = int(each["acct"])
        each["utc_date"] = parse_date(each["utc_date"])
        each["num_courses_visited"] = int(float(each["num_courses_visited"]))
        each["total_minutes_visited"] = float(each["total_minutes_visited"])
        each["lessons_completed"] = int(float(each["lessons_completed"]))
        each["projects_completed"] = int(float(each["projects_completed"]))

    # Read submissions and fix data types
    project_submissions = read_csv("project_submissions.csv")
    for each in project_submissions:
        each["creation_date"] = parse_date(each["creation_date"])
        each["completion_date"] = parse_date(each["completion_date"])
        each["account_key"] = int(each["account_key"])
        each["lesson_key"] = int(each["lesson_key"])

    # Rename account key column
    for each in daily_engagements:
        each["account_key"] = each["acct"]
        each.pop("acct", None)

    # Get unique student number from each dataset
    enrollment_unique_students, engagement_unique_students, submissions_unique_students = get_unique(
        enrollments), get_unique(daily_engagements), get_unique(project_submissions)

    # Get number of surprising values in engagement dataset
    count_strange_vals = 0
    for each in enrollments:
        if each["account_key"] not in engagement_unique_students and (
                not each["is_canceled"] or int(each["days_to_cancel"]) > 0):
            count_strange_vals += 1

    # Create set of udacity test account numbers
    udacity_accounts = set()
    for each in enrollments:
        if each["is_udacity"]:
            udacity_accounts.add(each["account_key"])

    # Remove test accounts from all
    enrollments = remove_test_accounts(enrollments, udacity_accounts)
    daily_engagements = remove_test_accounts(daily_engagements, udacity_accounts)
    project_submissions = remove_test_accounts(project_submissions, udacity_accounts)

    # Create dictionary of paid students i.e if they haven't cancelled or cancelled after 7 days
    paid_students = {}
    for each in enrollments:
        if not each["is_canceled"] or each["days_to_cancel"] > 7:
            # Add most recent enrollment of student
            if each["account_key"] not in paid_students or each["join_date"] > paid_students[each["account_key"]]:
                paid_students[each["account_key"]] = each["join_date"]

    # Find students in engagements that paid in first week
    paid_students_first_week = []
    for each in daily_engagements:
        if each["account_key"] in paid_students and within_one_week(paid_students[each["account_key"]],
                                                                    each["utc_date"]):
            paid_students_first_week.append(each)

    # Get engagement by account for paid students first week
    engagement_by_acc = defaultdict(list)
    for each in paid_students_first_week:
        engagement_by_acc[each["account_key"]].append(each)

    # Average minutes spent in classroom
    mins_stats = get_avg(paid_students_first_week, "total_minutes_visited")
    # Find student with max minutes
    max_mins_student = mins_stats["max_student"]

    # Analysing number of lessons completed
    lessons_stats = get_avg(paid_students_first_week, "lessons_completed")
    # Find student with max minutes
    max_lessons_student = lessons_stats["max_student"]

    # Analysing number of courses visited attended
    for each in paid_students_first_week:
        each["attended"] = 0
        if each["total_minutes_visited"] > 0:
            # Add attended column
            each["attended"] = 1
    num_courses_visited_stats = get_avg(paid_students_first_week, "attended")

    # Split data into passed and not passed first project
    first_project_keys = [746169184, 3176718735]
    passed_keys, failed_keys = set(), set()
    pass_grades = ["PASSED", "DISTINCTION"]
    for each in project_submissions:
        if each["account_key"] in engagement_by_acc and each["lesson_key"] in first_project_keys:
            if each["assigned_rating"] in pass_grades:
                passed_keys.add(each["account_key"])
            else:
                failed_keys.add(each["account_key"])
    # Students passed and failed from paid_students_first_week
    passed_students, failed_students = [], []
    for each in paid_students_first_week:
        if each["account_key"] in passed_keys:
            passed_students.append(each)
        else:
            failed_students.append(each)

    # Comparing students who did and didn't pass
    avg_passed_stats = get_avg(passed_students, "total_minutes_visited")
    avg_failed_stats = get_avg(failed_students, "total_minutes_visited")

    # Visualising data
    visualise_column(passed_students, "total_minutes_visited", "Passed students total minutes visited")
    visualise_column(failed_students, "total_minutes_visited", "Failed students total minutes visited")

    visualise_column(passed_students, "attended", "Passed students attendance")
    visualise_column(failed_students, "attended", "Failed students attendance")

    visualise_column(passed_students, "lessons_completed", "Passed students lessons completed")
    visualise_column(failed_students, "lessons_completed", "Failed students lessons completed")
    pass


if __name__ == '__main__':
    my_main()
