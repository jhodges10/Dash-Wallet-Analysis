import requests
import json
from json import JSONDecodeError
import random
from multiprocessing import Pool
from functools import partial
from functools import lru_cache
import time


# Insight API
@lru_cache(maxsize=30)
def fetch_block_txs(block_height):
    # Get block hash from height
    block_height_url = "https://insight.dashevo.org/insight-api-dash/block-index/{}".format(block_height)
    response = requests.get(block_height_url)

    if response.status_code == 200:
        block_hash = response.json()['blockHash']

    else:
        time.sleep(15)
        response = requests.get(block_height_url)
        block_hash = response.json()['blockHash']

    # Get transaction in block hash
    block_hash_url = "https://insight.dashevo.org/insight-api-dash/txs/?block={}".format(block_hash)
    response = requests.get(block_hash_url)

    if response.status_code == 200:
        block_txs = response.json()['txs']
    else:
        time.sleep(15)
        block_txs = response.json()['txs']

    return block_txs


# Insight API
def fetch_wallet(address):
    url_1 = "https://insight.dashevo.org/insight-api-dash/addr/{}".format(address)
    url_2 = "https://insight.dash.org/insight-api-dash/addr/{}".format(address)
    # url_3 = "http://insight.masternode.io:3000/api/addr/{}".format(address)
    # url_4 = "http://165.227.209.32:3001/insight-api-dash/addr{}".format(address)
    urls = [url_1, url_2]

    url_selected = random.choice(urls)

    response = requests.request("GET", url_selected)

    try:
        transaction_list = json.loads(response.text)['transactions']  # Temporarily disabled for GetFreeDash
        # transaction_list = json.loads(response.text)
        # print(transaction_list)
        return transaction_list

    except KeyError:
        return []


# Insight API
def fetch_transaction_history(txid, address):

    url_1 = "https://insight.dashevo.org/insight-api-dash/tx/{}".format(txid)
    url_2 = "https://insight.dash.org/insight-api-dash/tx/{}".format(txid)
    # url_3 = "http://insight.masternode.io:3000/api/tx/{}".format(txid)
    # url_4 = "http://165.227.209.32:3001/insight-api-dash/tx/{}".format(txid)
    urls = [url_1, url_2]

    url_selected = random.choice(urls)

    response = requests.request("GET", url_selected)
    matching_transactions = False

    try:
        transaction_info = json.loads(response.text)

        if 'coinbase' in transaction_info['vin'][0].keys():
            for vout in transaction_info['vout']:
                # print(vout.keys())
                amount_to_address = float(vout['value'])
                if int(round(amount_to_address)) >= 5:
                    trans_type = 'superblock_payment'
                elif int(round(amount_to_address)) >= 1:
                    trans_type = 'mn_payment'
                else:
                    trans_type = 'mining_payment'
                try:
                    if address in vout['scriptPubKey']['addresses']:
                        trans_dict = {
                            "amount": amount_to_address,
                            "time": transaction_info['time'],
                            "type": trans_type
                        }
                        matching_transactions = trans_dict
                        # print(matching_transactions)
                    else:
                        pass
                except KeyError or UnboundLocalError:
                    continue
        else:
            for vout in transaction_info['vout']:
                amount_to_address = float(vout['value'])
                if int(round(amount_to_address)) == 1000:
                    trans_type = 'mn_setup'
                else:
                    trans_type = 'normal'
                try:
                    if address in vout['scriptPubKey']['addresses']:
                        trans_dict = {
                            "amount": amount_to_address,
                            "time": transaction_info['time'],
                            "type": trans_type
                        }
                        matching_transactions = trans_dict
                        # print(matching_transactions)
                    else:
                        pass
                except KeyError or UnboundLocalError:
                    continue

        return matching_transactions

    except JSONDecodeError:
        print("Error with that transaction")
        null_dict = {
            "amount": 'Null',
            "time": 'Null',
            "date": 'Null',
            "type": 'Null'
        }
        return null_dict


# Insight API
def fetch_tx_info(txid):
    url_1 = "https://insight.dashevo.org/insight-api-dash/tx/{}".format(txid)
    url_2 = "https://insight.dash.org/insight-api-dash/tx/{}".format(txid)
    urls = [url_1, url_2]
    url_selected = random.choice(urls)

    response = requests.request("GET", url_selected)

    try:
        tx_info = response.json()
        return tx_info
    except:
        print("Failed to load valid JSON for that tx.")
        return None


# Insight API
def fetch_coinbase_tx(address):
    matching_transactions = []

    transaction_list = fetch_wallet(address)

    num_of_processes = 4
    p = Pool(num_of_processes)
    coinbase_tx = p.map(partial(fetch_tx_info), transaction_list)
    p.close()
    p.join()

    for transaction_info in coinbase_tx:
        if transaction_info is not None:
            if 'coinbase' in transaction_info['vin'][0].keys():
                for vout in transaction_info['vout']:
                    amount_to_address = float(vout['value'])
                    try:
                        if address in vout['scriptPubKey']['addresses']:
                            trans_dict = {
                                "amount": amount_to_address,
                                "time": transaction_info['time'],
                            }
                            matching_transactions.append(trans_dict)
                        else:
                            pass
                    except KeyError or UnboundLocalError:
                        continue

            else:
                continue

    print("Matching Transactions: \n" + str(matching_transactions))

    return matching_transactions


# Insight API
def build_simple_wallet_history(address, mn=True):
    transaction_list = fetch_wallet(address)
    num_of_processes = 12
    p = Pool(num_of_processes)
    matching_tx = p.map(partial(fetch_transaction_history, address=address), transaction_list)
    p.close()
    p.join()

    cleaned_transactions = []
    '''
    for count, txid in enumerate(transaction_list):
        count += 1
        print("Checking txid: " + str(txid))
        transaction_info = fetch_transaction_history(txid, address)
        if transaction_info is not False:
            cleaned_transactions.append(transaction_info)
        else:
            continue
    '''
    for tx_info in matching_tx:
        if tx_info is not False:
            cleaned_transactions.append(tx_info)
        else:
            continue

    return cleaned_transactions


# Insight API
def fetch_tx_time(txid):
    url_1 = "https://insight.dashevo.org/insight-api-dash/tx/{}".format(txid)
    url_2 = "https://insight.dash.org/insight-api-dash/tx/{}".format(txid)
    # url_3 = "http://insight.masternode.io:3000/api/tx/{}".format(txid)
    # url_4 = "http://165.227.209.32:3001/insight-api-dash/tx/{}".format(txid)
    urls = [url_1, url_2]

    url_selected = random.choice(urls)

    response = requests.request("GET", url_selected)
    tx_time = 0

    try:
        transaction_info = json.loads(response.text)
        tx_time = transaction_info['time']

    except JSONDecodeError:
        print("Shit fuck we're fucked.")
        return 0

    # print("tx Time: " + str(tx_time))

    return {'txid': txid, 'tx_time': tx_time}


# Insight API
def check_txs(tx_list):
    num_of_processes = 6
    p = Pool(num_of_processes)
    tx_times = p.map(partial(fetch_tx_time), tx_list)
    p.close()
    p.join()

    new_tx_dict = {tx['txid']: tx for tx in tx_times}

    return new_tx_dict


# Chainz API
def pooled_address_history_request(list_of_addresses):
    url = "https://chainz.cryptoid.info/dash/api.dws"
    querystring = {"q": "multiaddr", "active": "{}".format(list_of_addresses), "n": "1000", "key": "deb339469dc2"}

    response = requests.request("GET", url, params=querystring)

    try:
        t_history = json.loads(response.text)
        return t_history
    except JSONDecodeError:
        return []


# Chainz API
def single_address_history_request(address):
    url = "https://chainz.cryptoid.info/dash/api.dws"
    querystring = {"q": "multiaddr", "active": "{}".format(address), "n": "1000", "key": "deb339469dc2"}

    response = requests.request("GET", url, params=querystring)

    try:
        t_history = json.loads(response.text)

        for transaction in t_history['txs']:
            #print(transaction)
            transaction['change'] = transaction['change']/100000000

        return t_history
    except JSONDecodeError as e:
        return e

