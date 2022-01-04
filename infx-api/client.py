import requests, pandas

BASE_URL = "http://infx-api-ds.prod.projectronin.io/"
# BASE_URL = "http://127.0.0.1:5000/"

class Code:
    def __init__(self, system, version, code, display):
        self.system = system
        self.version = version
        self.code = code
        self.display = display

    def serialize(self, with_system_and_version=True):
        serialized = {
            "system": self.system,
            "version": self.version,
            "code": self.code,
            "display": self.display
        }

        if with_system_and_version is False:
            serialized.pop('system')
            serialized.pop('version')

        return serialized

class ValueSet:
    def __init__(self, name):
        self.name = name

    def load_most_recent_active_version(self):
        vs = requests.get(f'{BASE_URL}/ValueSets/{self.name}/most_recent_active_version')
        return ValueSetVersion(vs.json())

    def load_versions_metadata(self):
        md = requests.get(f'{BASE_URL}/ValueSets/{self.name}/versions/')
        return md.json()

    def load_versions_metadata_as_df(self):
        return pandas.read_json(f'{BASE_URL}/ValueSets/{self.name}/versions/')


class ValueSetVersion:
    def __init__(self, json):
        self.json = json
        self.type = 'intensional' if self.is_intensional() is True else 'extensional'
        self.codes = []

        if self.type == 'intensional': self.load_intensional()

    @classmethod
    def load(cls, uuid):
        vs = requests.get(f'{BASE_URL}/ValueSet/{uuid}/$expand')
        return ValueSetVersion(vs.json())
    
    def is_intensional(self):
        for x in self.json.get('compose').get('include'):
            if 'filter' in x: 
                return True

    def load_intensional(self):
        for x in self.json.get('expansion').get('contains'):
            self.codes.append(
                Code(
                    system=x.get('system'),
                    version=x.get('version'),
                    code=x.get('code'),
                    display=x.get('display')
                )
            )

if __name__ == '__main__':
    vs_version = ValueSet('test-breast-cancer').load_most_recent_active_version()
    for code in vs_version.codes:
        print(code.serialize())
        
    metadata = ValueSet('test-breast-cancer').load_versions_metadata_as_df()
    print(metadata)

    version = ValueSetVersion.load('529ef7a0-4241-11ec-bec2-fbf6ebf76a60')
    print(version)
