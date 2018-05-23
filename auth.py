import jwt
import yaml


class Auth:
    def __init__(self, config_file="config.yaml"):
        self.config_file = config_file
        self.config = None
        self.load_config()

    def load_config(self):
        with open("config.yaml", 'r') as stream:
            try:
                self.config = yaml.load(stream)
            except yaml.YAMLError as ex:
                print(ex)

    def get_config(self, config_attribute):
        return self.config[config_attribute]

    def verify_token(self, token):
        config = self.get_config('jwt')
        decoded = jwt.decode(
            token, config['secret'], audience=config['audience'])
        print(decoded)
