# Given:
# - List of creative ids
# Output:
# - CSV file for each creative with (Moving average)
import csv
import datetime
import time

import matplotlib.pyplot as plt
import pandas as pd
from pymongo import MongoClient


def time_diff_str(t1, t2):
    """
    Calculates time durations.
    """
    diff = t2 - t1
    mins = int(diff / 60)
    secs = round(diff % 60, 2)
    return str(mins) + " mins and " + str(secs) + " seconds"


def cal_click_through(interactions):
    """
    Get click-through count from interactions
    """
    click_through = 0
    for i in range(0, len(interactions)):
        interact = interactions[i]
        if interact["clickThrough"]:
            click_through += interact["count"]

    return click_through


def line_chart(plt, x, y):
    # create a line chart, years on x-axis, gdp on y-axis
    plt.plot(x, y, color="#f39c12", marker="o", linestyle="solid")

    # add a title
    plt.title("Clicks movement")

    # add a label to the y-axis
    plt.ylabel("# clicks")
    plt.show()


if __name__ == "__main__":
    t_start = time.time()
    print "------------------------------------------------"
    print " %s - ETL clicks data" % datetime.datetime.now()
    print "------------------------------------------------"

    # connect to databases
    conn = MongoClient("mongodb://localhost:27017/")
    db_brand_display_analytics = conn["brand_display_analytics"]

    # params
    widget_ids = ["knxad_knx2991_201604204777"]
    coll_brand_display_analytics = db_brand_display_analytics["brand_display" + "_05_2017"]

    for item in widget_ids:
        print "* Process widget:", item

        # query report
        num_items = 0
        cursor_report = coll_brand_display_analytics.find({
            "widgetId": item,
            "date": {
                "$gte": 1493654400,
                "$lt": 1493740800
            },
            "section": "ea845d619a665959b6a6d7415457479a55cd4149"
        })
        df_report_items = pd.DataFrame(list(cursor_report))
        df_report_items = df_report_items.sort_values(by=["date"], ascending=[1])

        # for charts
        x = []
        y = []

        # save to CSV file
        data_name = "data/" + item + ".csv"
        with open(data_name, "wb") as f:
            for index, report in df_report_items.iterrows():
                num_items += 1
                w = csv.DictWriter(f, ["widgetId", "date", "clicks"])
                w.writeheader()

                clicks = cal_click_through(report["interactions"])
                hourly = datetime.datetime.fromtimestamp(report["date"]).strftime("%H")
                w.writerow({
                    "widgetId": report["widgetId"],
                    "date": hourly,
                    "clicks": clicks
                })

                x.append(hourly)
                y.append(clicks)

        print "Number items:", num_items
        line_chart(plt, x, y)

    print " %s * DONE After * %s" % (datetime.datetime.now(), time_diff_str(t_start, time.time()))