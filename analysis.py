import csv
import random
import requests
import json
from json import JSONDecodeError
from dash_modules import wallet_insights

from multiprocessing import Pool
from functools import partial


csv_path = 'getfreedash_2.csv'


def csv_read_to_wallet_dict(path):
    dict_thing = []

    with open(path, mode='r') as address_list:
        reader = csv.DictReader(address_list)
        for count, row in enumerate(reader):
            dict_thing.append(row['Wallet Id'])

    return dict_thing


def gather_address_info(address_list):
    analysis_dict = {}
    init_csv()

    for count, address in enumerate(address_list):  # Loop through every address in the list
        count += 1

        try:
            wallet_info = wallet_insights.fetch_wallet(address)  # Check if any money left that address
        except:
            continue
        #print(wallet_info)
        try:
            if wallet_info['totalSent'] >= 0.0:
                try:
                    percentage_sent = int(100*(wallet_info['totalSent']/wallet_info['totalReceived']))
                except ZeroDivisionError:
                    percentage_sent = 0

                received = wallet_info['totalReceived']
                sent = wallet_info['totalSent']
                tx_count = wallet_info['txApperances']

                wallet = {'recieved': received, 'sent': sent, 'percentage_sent': percentage_sent, 'tx_count': tx_count}

                append_to_csv([address, received, sent, percentage_sent, tx_count])

                analysis_dict.update({address: wallet})

            else:
                pass
            
        except KeyError:
            print("Couldn't get all the data you wanted on that one")
            continue

        print("Fetched info on {}/{}".format(count, len(address_list)))

    return analysis_dict


def advanced_wallet_grabber(address):
    print(address)
    wallet_info = wallet_insights.fetch_wallet(address)

    try:
        if wallet_info['totalSent'] >= 0.0:
            try:
                percentage_sent = int(100 * (wallet_info['totalSent'] / wallet_info['totalReceived']))
            except ZeroDivisionError:
                percentage_sent = 0

            received = wallet_info['totalReceived']
            sent = wallet_info['totalSent']
            tx_count = wallet_info['txApperances']

            wallet = {'recieved': received, 'sent': sent, 'percentage_sent': percentage_sent, 'tx_count': tx_count}

            append_to_csv([address, received, sent, percentage_sent, tx_count])

            # analysis_dict.update({address: wallet})

        else:
            pass

    except KeyError:
        print("Couldn't get all the data you wanted on that one")

    return True


def multi_wallet_fetch(address_list):
    num_of_processes = 12
    p = Pool(num_of_processes)
    wallet_txs = p.map(advanced_wallet_grabber, address_list)
    p.close()
    p.join()

    return wallet_txs


def save_data(analysis_dict):
    with open("analysis_full.json", 'w') as analysis:
        json.dump(analysis_dict, analysis)
    return True


def init_csv():
    # initial content
    with open('analysis.csv', 'w') as f:
        f.write('address,received,sent, percentage_sent, tx_count,\n')  # TRAILING NEWLINE

    return True


def append_to_csv(line_by_line):
    with open('analysis.csv', 'a') as output:
        writer = csv.writer(output)
        writer.writerow(line_by_line)

    return True


if __name__ == '__main__':
    address_list = csv_read_to_wallet_dict(csv_path)
    print(len(set(address_list)))
    #analysis_dict = gather_address_info(set(address_list))

    multi_wallet_fetch(address_list)

    #save_data(analysis_dict)


