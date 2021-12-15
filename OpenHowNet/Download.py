import requests
import os
from tqdm import tqdm
import zipfile

OPENHOWNET_DATA_URL = "https://thunlp.oss-cn-qingdao.aliyuncs.com/OpenHowNet/resources.zip"
OPENHOWNET_RESOURCE_PATH = os.path.join(os.path.expanduser('~'), ".openhownet")


def get_resource(path, mode='r', encoding='utf-8'):
    '''Open the resource file.
    '''
    try:
        if 'b' in mode:
            file = open(os.path.join(OPENHOWNET_RESOURCE_PATH, path), mode)
        else:
            file = open(os.path.join(OPENHOWNET_RESOURCE_PATH, path),
                        mode, encoding=encoding)
        return file
    except FileNotFoundError as e:
        error_msg = str(
            "Important data file \"{}\" lost, please run `OpenHowNet.download()`."
        ).format(path)
        raise FileNotFoundError(error_msg)


def download_file(url, dest_file=None):
    '''Download resources files from url to dest path.

    Args:
        url (str): 
            download url of resource file.
        dest_file (str): 
            target download path.
    '''
    req = requests.get(url, stream=True)
    total_size = int(req.headers['Content-Length']) / 1024

    if not dest_file:
        dest_file = os.path.basename(url)

    dest_path = os.path.join(OPENHOWNET_RESOURCE_PATH, dest_file)

    with open(dest_path, 'wb') as f:
        for x in tqdm(iterable=req.iter_content(1024), total=round(total_size, 2), unit='KB', desc=dest_file):
            f.write(x)

    return dest_path


def download():
    '''Download the HowNet resource file.
    The HowNet resource file is openhownet_data.zip.
    '''
    if not os.path.exists(os.path.join(OPENHOWNET_RESOURCE_PATH, 'resources')):
        os.makedirs(os.path.join(OPENHOWNET_RESOURCE_PATH, 'resources'))
    data_zip_path = download_file(
        OPENHOWNET_DATA_URL, dest_file=os.path.join("resources", "resources.zip"))
    with zipfile.ZipFile(data_zip_path, 'r') as zip_ref:
        zip_ref.extractall(os.path.join(OPENHOWNET_RESOURCE_PATH, 'resources'))
    os.remove(data_zip_path)
