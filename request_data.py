import requests, json, os, time
from pathlib import Path

def request_break():
    """
    Specify a time to sleep
    """
    time.sleep(5)

def get_request_params(data_name:str, api_key:str) -> dict:
    """
    This function return the requests params.
    Example:
    {
        "method":"GetData",
        "datasetname":"NIPA",
        "tablename":"T10105",
        "frequency":"Q",
        "year":"ALL",
        "resultformat":"json"
		}
    """
    with open(os.path.join('config_data_request', 'BEA.json')) as f:
        params = json.load(f)[data_name]['params']
    params['userid'] = api_key

    return params


def form_BEA_url(params:dict) -> str:
    """
    """

    userid = params['userid']
    method = params['method']
    datasetname = params['datasetname']
    tablename = params['tablename']
    frequency = params['frequency']
    year = params['year']
    resultformat = params['resultformat']

    url = f"http://apps.bea.gov/api/data/?UserID={userid}&method={method}&datasetname={datasetname}&TableName={tablename}&Year={year}&Frequency={frequency}&ResultFormat={resultformat}"

    return url

def save_json(data_path, content):
    """
    This function save downloaded data to a json file.
    """
    with open(data_path, 'w') as f:
        json.dump(content, f)


def get_api_key(computer, file_name):

    key = None
    if computer == 'popos':
        with open(f'/home/synferlo/my_disk/git/api_key/{file_name}') as f:
            key = json.load(f)['xie']
    elif computer == 'dell':
        with open(f'/home/synferlodell/git/api_key/{file_name}') as f:
            key = json.load(f)['xie']
    
    return key



def request_BEA_data(data_name, data_path, computer):
    """
    This function is a template to request data from BEA
    """

    ###------Get api key------###
    #key = None
    #if computer == 'popos':
    #    with open('/home/synferlo/my_disk/git/api_key/BEA.json') as f:
    #        key = json.load(f)['xie']
    #elif computer == 'dell':
    #    with open('/home/synferlodell/git/api_key/BEA.json') as f:
    #        key = json.load(f)['xie']

    key = get_api_key(computer, 'BEA.json')

    ###------Format url------###
    params = get_request_params(data_name, key)
    url = form_BEA_url(params)

    ###------Request and save data------###
    r = requests.get(url)
    data = r.json()
    save_json(data_path, data)
    

def request_FRED_data(data_name, data_path, computer):
    ###------load api key------###
    key = get_api_key(computer, 'FRED.json')

    ###------form url------###
    with open(Path('config_data_request')/'FRED.json') as f:
        params = json.load(f)[data_name]['params']
    params['api_key'] = key

    ###------request------###
    # Get series title
    url = 'https://api.stlouisfed.org/fred/series'
    title = requests.get(url, params).json()['seriess'][0]['title']
    time.sleep(0.5)

    url = 'https://api.stlouisfed.org/fred/series/observations'
    data = requests.get(url, params).json()
    data['title'] = title
    save_json(data_path, data)






#############################################
#               API calls
#############################################

def get_BEA_data(data_dir, data_name, computer):
    """
    This function get data from BEA.
    """

    data_path = os.path.join(data_dir, f'{data_name}.json')

    request_BEA_data(data_name, data_path, computer)
    print(f'Received new dataset: [{data_name}]')
    # sleep
    request_break()




def get_FRED_data(data_dir, data_name, computer):
    """
    This function get data from FRED.
    """
    data_path = Path(data_dir)/f"{data_name}.json"

    request_FRED_data(data_name, data_path, computer)
    print(f'Received new dataset: [{data_name}]')
    # sleep
    request_break()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
if __name__ == "__main__":
    """
    Website     data_name                   frequency
    BEA:
                NGDP-BEA-Q (table: 1.1.5)   quarterly
    """
    
    """
    I will download and update all datasets using this script.
    """
    data_dir = os.path.join('data', 'request_data')
    Path(data_dir).mkdir(exist_ok=True, parents = True)
    
    
    ###------Download GDP table from BEA------###
    #data_name = "NGDP-BEA-Q"
    #get_NGDP_BEA(data_dir, data_name)


    computer = 'popos'
    data_name = 'UNRATE-FRED-M' # unemployment rate
    get_FRED_data(data_dir, data_name, computer)



    
    
    



















