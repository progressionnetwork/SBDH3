import requests
import os
import json

URL = "https://ethereum-api.rarible.org/v0.1/nft/items/byCollection?collection=0x49cf6f5d44e70224e2e23fdcdd2c053f30ada28b&size=20000"
savedir = "img"


def parse_json_collection():

    limit = 100
    run_forever = (limit == 0)
    page = 0

    os.makedirs('./' + savedir + '/', exist_ok=True)

    with open('byCollection.json') as json_file:
        data = json.load(json_file)
        # print(data)

    i = 0
    for json_dict in data['items']:
        try:
            url = json_dict['meta']['image']['url']['ORIGINAL']
            img_data = requests.get(url).content
            img_name = os.path.basename(url)
            with open(savedir + '/' + img_name, 'wb') as handler:
                handler.write(img_data)
                print(str(i), url, 'saved to file', savedir + '/' + img_name)
        except:
            pass
        i += 1

    print("Done")


def parse_json_preview_collection():

    limit = 100
    run_forever = (limit == 0)
    page = 0
    savedir = "preview"

    os.makedirs('./' + savedir + '/', exist_ok=True)

    with open('byCollection.json') as json_file:
        data = json.load(json_file)
        # print(data)

    i = 0
    for json_dict in data['items']:
        try:
            url = json_dict['meta']['image']['url']['PREVIEW'] # ORIGINAL
            img_data = requests.get(url).content
            img_name = str(i)+'.png' #os.path.basename(url)
            with open(savedir + '/' + img_name, 'wb') as handler:
                handler.write(img_data)
                print(str(i), url, 'saved to file', savedir + '/' + img_name)
        except:
            pass
        i += 1

    print("Done")


if __name__ == '__main__':
    parse_json_collection()