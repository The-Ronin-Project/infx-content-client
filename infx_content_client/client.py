import requests, pandas

BASE_URL = "http://hashi-ds.prod.projectronin.io/"
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
    def __init__(self, identifier):
        self.identifier = identifier

    def load_most_recent_active_version(self):
        vs = requests.get(f'{BASE_URL}/ValueSets/{self.identifier}/most_recent_active_version')
        if vs.status_code != 200:
            raise Exception(vs.json().get('message'))
        return ValueSetVersion(vs.json())

    def load_versions_metadata(self):
        md = requests.get(f'{BASE_URL}/ValueSets/{self.identifier}/versions/')
        return md.json()

    def load_versions_metadata_as_df(self):
        return pandas.read_json(f'{BASE_URL}/ValueSets/{self.identifier}/versions/')

    @classmethod
    def load_all_value_sets_metadata(cls):
        md = requests.get(f'{BASE_URL}/ValueSets/')
        return md.json()

    @classmethod
    def load_all_value_sets_metadata_as_df(cls):
        return pandas.read_json(f'{BASE_URL}/ValueSets/')

    @classmethod
    def load_all_value_set_versions_by_status(cls, status=['active', 'retired']):
        data = requests.get(f'{BASE_URL}/ValueSets/all/', params={
            'status': ','.join(status)
        })
        return data.json()


class ValueSetVersion:
    def __init__(self, json):
        self.json = json
        self.type = 'intensional' if self.is_intensional() is True else 'extensional'
        self.type = 'intensional'
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

    @property
    def additional_data(self):
        # This property holds additional fields we've supplied that aren't part of the FHIR spec
        return self.json.get('additionalData')

    @property
    def effective_start(self):
        return self.additional_data.get('effective_start')

    @property
    def effective_end(self):
        return self.additional_data.get('effective_end')

    @property
    def version_uuid(self):
        return self.additional_data.get('version_uuid')

    @property
    def value_set_uuid(self):
        return self.additional_data.get('value_set_uuid')

    @property
    def expansion_uuid(self):
        return self.additional_data.get('expansion_uuid')

    @property
    def contact(self):
        return self.json.get('contact')[0].get('name')

    @property
    def name(self):
        return self.json.get('name')

    @property
    def title(self):
        return self.json.get('title')

    @property
    def status(self):
        return self.json.get('status')

    @property
    def version(self):
        return self.json.get('version')

    @property
    def purpose(self):
        return self.json.get('purpose')

    @property
    def description(self):
        return self.json.get('description')

    @property
    def experimental(self):
        return self.json.get('experimental')

if __name__ == '__main__':
    vs_version = ValueSet('test-breast-cancer').load_most_recent_active_version()
    for code in vs_version.codes:
        print(code.serialize())
        
    metadata = ValueSet('test-breast-cancer').load_versions_metadata_as_df()
    print(metadata)

    version = ValueSetVersion.load('529ef7a0-4241-11ec-bec2-fbf6ebf76a60')
    print(version)

    failed_version = ValueSet('0bd56b70-9ff6-11ec-95eb-3f73787c1997').load_most_recent_active_version()
    # print(dir(failed_version))

