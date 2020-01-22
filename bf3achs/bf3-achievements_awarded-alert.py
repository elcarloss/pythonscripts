#!/usr/bin/python
import sys
import requests

GRAPH_URL = ("http://internal.graphite.eu.renderer.gos.gameservices.ea.com/render?"
             "target=alias(sumSeries(nonNegativeDerivative(prod.achievements.*.achievements-prod-"
             "achievements*.achievements.products.BF_BF3_PC.ACHIEVEMENT_AWARDED.count)),%20%27BF3"
             "%20Achievements%20Awarded%27)&from-61min&format=json")


def get_graph_values(url):
    """
    Get the values from graphana and them, if the sum is greater than zero then the alert passes,
    if it is zero then trigger a critical alert.
    """
    try:
        response = requests.get(url)
    except requests.exceptions.RequestException as err:
        output = "Data check FAIL - Could not get data from URL", err
        sys.exit(2)
    try:
        response.json()[0]["datapoints"]
    except ValueError as erro:
        output = "There's not exist valid Datapoints", erro
        sys.exit(2)
    datapoints = response.json()[0]["datapoints"]
    values = []
    for datapoint in datapoints:
        achievements_count = datapoint[0]
        if achievements_count is None:
            achievements_count = 0
        values.append(achievements_count)
    achievements_count_sum = sum(values)
    return achievements_count_sum

def main():
    """
    This alert checks the values of achievements awarded for Battlefield 3 PC
    and triggers when the values have been zero for more than 1 hour.
    """
    achievement_sum = get_graph_values(GRAPH_URL)
    if achievement_sum > 0:
        output = "Data check OK - Achievements awarded in the last hour: {0}"
        print output.format(achievement_sum)
        sys.exit(0)
    else:
        output = "Data check FAIL - Achievements awarded in the last hour: {0}"
        print output.format(achievement_sum)
        sys.exit(2)

if __name__ == '__main__':
    main()
