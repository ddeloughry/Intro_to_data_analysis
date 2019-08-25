from datetime import datetime

import unicodecsv


def read_csv(param):
    with open(param, "rb") as file:
        reader = unicodecsv.DictReader(file)
        return list(reader)


def parse_date(param):
    if param:
        return datetime.strptime(param, "%Y-%m-%d")
    else:
        return None


def get_num_rows_and_unique(data):
    unique_students = set()
    for each in data:
        unique_students.add(each["account_key"])
    return data, unique_students


def my_main():
    # Read enrollments
    enrollments = read_csv("enrollments.csv")
    # Fix enrollment data types
    for each in enrollments:
        each["account_key"] = int(each["account_key"])
        each["join_date"] = parse_date(each["join_date"])
        each["is_canceled"] = each["is_canceled"] == "True"
        each["is_udacity"] = each["is_udacity"] == "True"
        if each["is_canceled"]:
            each["cancel_date"] = parse_date(each["cancel_date"])
            each["days_to_cancel"] = int(each["days_to_cancel"])

    # Read engagements
    daily_engagements = read_csv("daily_engagement.csv")
    # Fix engagement data types
    for each in daily_engagements:
        each["acct"] = int(each["acct"])
        each["utc_date"] = parse_date(each["utc_date"])
        each["num_courses_visited"] = int(float(each["num_courses_visited"]))
        each["total_minutes_visited"] = float(each["total_minutes_visited"])
        each["lessons_completed"] = int(float(each["lessons_completed"]))
        each["projects_completed"] = int(float(each["projects_completed"]))

    # Read submissions
    project_submissions = read_csv("project_submissions.csv")
    # Fix submission data types
    for each in project_submissions:
        each["creation_date"] = parse_date(each["creation_date"])
        each["completion_date"] = parse_date(each["completion_date"])
        each["account_key"] = int(each["account_key"])
        each["lesson_key"] = int(each["lesson_key"])

    for each in daily_engagements:
        each["account_key"] = each["acct"]
        each.pop("acct", None)

    enrollment_rows, enrollment_unique_students = get_num_rows_and_unique(enrollments)
    engagement_rows, engagement_unique_students = get_num_rows_and_unique(daily_engagements)

    count_strange_vals = 0
    for each in enrollments:
        if each["account_key"] not in engagement_unique_students and (
                each["is_canceled"] != True or int(each["days_to_cancel"]) > 0):
            count_strange_vals += 1

    udacity_accounts = set()
    for each in enrollments:
        if each["is_udacity"]:
            udacity_accounts.add(each["account_key"])

    for each in


if __name__ == '__main__':
    my_main()
