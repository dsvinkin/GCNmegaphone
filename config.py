
import yaml

def read_config(file_name):

    info = None
    with open(file_name, 'r') as stream:
        try:
            info = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
            exit()

    return info

if __name__ == "__main__":

    info = read_config('config.yaml')
    print(info)

    keys = "telegram_proxy bot_token chat_id log_dir".split()
    for key in keys:
        print("{:16s}: {:s}".format(key, info[key]))