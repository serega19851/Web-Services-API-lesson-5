from __future__ import print_function
from terminaltables import SingleTable
from itertools import count
import requests
from dotenv import load_dotenv
import os


def calculates_average_salary(payment_from, payment_to):
    if payment_from and payment_to:
        return (payment_from + payment_to) / 2
    if payment_from and payment_to:
        return None
    if not payment_from:
        return payment_to * 0.8
    if not payment_to:
        return payment_from * 1.2


def predict_rub_salary_hh(language):
    nothing = []
    moscow = "1"
    for number in count(0):
        params = {
            "text": f"{language}",
            "per_page": "100",
            "page": number,
            "area": moscow,
            "only_with_salary": True
        }
        response = requests.get("https://api.hh.ru/vacancies/", params=params)
        response.raise_for_status()
        response = response.json()
        for vacancie in response["items"]:
            if not vacancie["salary"]:
                continue
            if vacancie["salary"]["currency"] != "RUR":
                nothing.append(None)
            nothing.append(
                calculates_average_salary(
                    vacancie["salary"]["from"], vacancie["salary"]["to"]
                )
            )
        if number == response["pages"]:
            break
    per_job_salaries = nothing
    return per_job_salaries


def calculates_the_average_salary_hh(*languages):
    languages_vacancy = dict.fromkeys(*languages)
    for language in languages_vacancy:
        per_job_salaries_hh = predict_rub_salary_hh(language)
        salaries = [
            int(salary) for salary in per_job_salaries_hh
            if salary
        ]
        number_vacancies = len(per_job_salaries_hh)
        number_of_processed_salaries = len(salaries)
        average_salary = int(sum(salaries) / len(salaries) if salaries else 0)
        languages_vacancy[language] = {
            "vacancies_found": number_vacancies,
            "vacancies_processed": number_of_processed_salaries,
            "average_salary": average_salary
        }
    return languages_vacancy


def predict_rub_salary_sj(language):
    load_dotenv()
    superjob_key = os.getenv("SUPERJOB_KEY")
    nothing = []
    moscow = 4
    development_programming = 48
    for number in count(0):
        params = {
            "count": 100,
            "t": moscow,
            "keyword": language,
            "catalogues": development_programming,
            "page": number
        }
        headers = {"X-Api-App-Id": f"{superjob_key}"}
        response = requests.get(
            "https://api.superjob.ru/2.0/vacancies", headers=headers,
            params=params
        )
        response.raise_for_status()
        response = response.json()
        for vacancie in response["objects"]:
            if not vacancie["currency"] == "rub":
                continue
            nothing.append(
                calculates_average_salary(
                    vacancie["payment_from"], vacancie["payment_to"]
                )
            )
        if not response["more"]:
            break
    per_job_salaries = nothing
    return per_job_salaries


def calculates_the_average_salary_sj(*vacancies):
    languages_vacancy = dict.fromkeys(*vacancies)
    for language in languages_vacancy:
        per_job_salaries_sj = predict_rub_salary_sj(language)
        salaries = [int(salary) for salary in per_job_salaries_sj if salary]
        number_vacancies = len(per_job_salaries_sj)
        number_of_processed_salaries = len(salaries)
        average_salary = int(sum(salaries) / len(salaries) if salaries else 0)
        languages_vacancy[language] = {
            "vacancies_found": number_vacancies,
            "vacancies_processed": number_of_processed_salaries,
            "average_salary": average_salary
        }
    return languages_vacancy


def converts_statistics_to_table(average_salaries, title):
    column_names = [
        ("Язык программирования", "Вакансий найдено",
         "Вакансий обработано", "Средняя зарплата")
    ]
    for language, statistics in average_salaries.items():
        statistics_vacancies = [numbers for numbers in statistics.values()]
        statistics_vacancies .insert(0, language)
        column_names.append(tuple(statistics_vacancies))
    table_statistics = tuple(column_names)
    table_instance = SingleTable(table_statistics, title)
    return table_instance.table


def main():
    languages = [
        "JavaScript", "Java", "Python", "Ruby", "PHP", "C++", "C#", "Go"
    ]
    average_salaries_hh = calculates_the_average_salary_hh(languages)
    average_salaries_sj = calculates_the_average_salary_sj(languages)
    print(converts_statistics_to_table(
        average_salaries_hh, "HeadHunter Moscow")
    )
    print()
    print(converts_statistics_to_table(average_salaries_sj, "SuperJob Moscow"))


if __name__ == '__main__':
    main()
