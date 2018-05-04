import json
import matplotlib.pyplot as plt
import pandas as pd
import csv

def load_json():
    with open("analysis_full.json", 'r') as analysis:
        return json.load(analysis)


def load_csv():
    analysis_dict = {}
    with open('analysis.csv', 'r') as analysis:
        reader = csv.DictReader(analysis)
        for row in reader:
            address = row['address']
            received = row['received']
            sent = row['sent']
            percentage_sent = row[' percentage_sent']
            tx_count = row[' tx_count']

            wallet = {'recieved': received, 'sent': sent, 'percentage_sent': percentage_sent, 'tx_count': tx_count}

            analysis_dict.update({address: wallet})

    return analysis_dict


def convert_json(json_data):
    percentages_list = []

    for address in json_data:
        try:
            percentage = int(json_data[address]['percentage_sent'])
            percentages_list.append(percentage)
        except TypeError:
            continue
    return percentages_list


def graph_data(percentages_list):
    print(percentages_list)
    x = sorted(percentages_list, key=int)

    # the histogram of the data
    n, bins, patches = plt.hist(x, 20, density=False, facecolor='r', alpha=0.75)

    plt.xlabel('Percentage sent out of wallet (spent)')
    plt.ylabel('Distribution')
    plt.title('GetFreeDash Funds Usage From {} Addresses'.format(len(percentages_list)))
    plt.grid(True)
    plt.show()

    plt.savefig('distribution.jpg')


def graph_data_2(percentage_list):

    data = pd.DataFrame(percentage_list)

    fig, ax = plt.subplots()
    data[0].value_counts().plot(ax=ax, kind='bar')

    fig.savefig('distribution_2.png')


def total_given_away(analysis_data):
    biggest_addresses = []

    sum = 0
    for wallet in analysis_data:
        biggest_addresses.append(analysis_data[wallet]['recieved'])
        if analysis_data[wallet]['recieved'] > 10:
            print(wallet, analysis_data[wallet])
        sum += analysis_data[wallet]['recieved']


    print(sum)
    print(sorted(biggest_addresses, key=float, reverse=True)[:10])
    return sum


if __name__ == '__main__':
    # analysis_data = load_json()
    analysis_data = load_csv()
    prepared_data = convert_json(analysis_data)
    # total_given_away(analysis_data)
    graph_data(prepared_data)
