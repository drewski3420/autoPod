import argparse, requests
from bs4 import BeautifulSoup as bs

def arg_parser():
    global args
    parser = argparse.ArgumentParser()
    parser.add_argument('--add_pod', nargs=2, help='Provide Pod Name to add to list')
    parser.add_argument('--search_pod', help='Put Search terms to find new podcasts')
    args = parser.parse_args()

def search():
    ENDPOINT = 'http://api.digitalpodcast.com/v2r/search/?'
    params = {
        'appid': 'bee8b7961c61862fe150f1eebefdb9c2'
    }
    params['keywords'] = args.search_pod
    r = requests.get('{}'.format(ENDPOINT), params=params)
    soup = bs(r.text, features = 'xml')
    i = 0
    pod_results = []
    for pod in soup.opml.body:
        if pod.name =='outline':
            i+=1
            temp_list = {}
            temp_list['number'] = i
            temp_list['pod_name'] = pod.get('text')
            temp_list['pod_url'] = pod['url']
            pod_results.append(temp_list)
    return pod_results

def add_pod(r):
    
def menu(pod_results):
    print('Pods found with search term {}'.format(args.search_pod))
    for r in pod_results:
        print('{}: {} ({})'.format(r['number'],r['pod_name'],r['pod_url']))
    choice = input('Choose a number to add:')
    if choice == '':
        pass
    else:
        for r in pod_results:
            if str(r['number']) == str(choice):
                add_pod(r)
        
def main():
    global args
    arg_parser()
    search_results = search()
    menu(search_results)

if __name__ == '__main__':
    main()
