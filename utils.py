import os
from dotenv import dotenv_values

env = dotenv_values('./.env')

def get_env(var_name: str) -> str:
    return os.environ.get(var_name) or env.get(var_name, "")

def remove_file(filename: str):
    file_path = 'temp/{}'.format(filename)
    if os.path.isfile(file_path):
        os.remove(file_path)
        print('{} successfully removed!'.format(file_path))
    else:
        print('Error: {} file not found'.format(file_path))

def remove_temporary_files():
    dir_name = 'temp/'
    files = os.listdir(dir_name)
    
    if len(files) > 1:
        for item in files:
            if item.endswith('.docx') or item.endswith('.doc') or item.endswith('.pdf'):
                os.remove(os.path.join(dir_name, item))

    