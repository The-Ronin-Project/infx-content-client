import requests, pandas

BASE_URL = "https://hashi.prod.projectronin.io/"
# BASE_URL = "http://127.0.0.1:5500/"

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

    def __repr__(self):
        return f'Code: ({self.code}, {self.display})'

    def __hash__(self):
        return hash((self.code, self.display, self.system, self.version))

    def __eq__(self, other):
        return (self.code, self.display, self.system, self.version) == (other.code, other.display, other.system, other.version)
      

class ValueSet:
    def __init__(self, identifier):
        self.identifier = identifier

    def load_most_recent_active_version(self):
        vs = requests.get(f'{BASE_URL}/ValueSets/{self.identifier}/most_recent_active_version')
        # This can fail if there is no active version
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
      
class Mapping:
    def __init__(self, source_code, equivalence, target_code, comments=None):
        self.source_code = source_code
        self.equivalence = equivalence
        self.target_code = target_code
        self.comments = comments

    def __repr__(self):
        return f'({self.source_code.code}, {self.source_code.display})--[{self.equivalence}]->({self.target_code.code},{self.target_code.display})'

class ConceptMap:
    @classmethod
    def all_concept_maps(cls, restrict_by_status=['active', 'retired']):
        all_map_metadata = requests.get(f'{BASE_URL}/ConceptMaps/all/')
        if all_map_metadata.status_code != 200:
            raise Exception("Unable to retrieve concept map metadata from infx-content API")
        filtered_metadata = [x for x in all_map_metadata.json() if x.get('status') in restrict_by_status]
        return [ConceptMapVersion.load(x.get('concept_map_version_uuid')) for x in filtered_metadata]

    @classmethod
    def all_concept_maps_json(cls, restrict_by_status=['active', 'retired']):
        return [x.json for x in cls.all_concept_maps(restrict_by_status=restrict_by_status)]
      
    @classmethod
    def load_most_recent_active_version(uuid):
        pass
      
class ConceptMapVersion:
    def __init__(self, comments, description, effective_start, effective_end, experimental, publisher, purpose, status, title, version, mappings, raw_json):
        self.comments = comments
        self.description = description
        self.effective_start = effective_start
        self.effective_end = effective_end
        self.experimental = experimental
        self.publisher = publisher
        self.purpose = purpose
        self.status = status
        self.title = title
        self.version = version
        self.mappings = mappings
        self.json = raw_json

    @classmethod
    def load(cls, uuid):
        md = requests.get(f'{BASE_URL}/ConceptMaps/{uuid}')
        if md.status_code != 200:
            raise Exception(f"Unable to retrieve concept map with UUID: {version_uuid}")
        data = md.json()

        mappings = {}

        groups = data.get('group')
        for group in groups:
            source_terminology = group.get('source')
            source_version = group.get('sourceVersion')
            target_terminology = group.get('target')
            target_version = group.get('targetVersion')

            for element in group.get('element'):
                source_code = Code(source_terminology, source_version, element.get('code'), element.get('display'))
                mapped_codes_for_source = [
                    Mapping(source_code, item.get('equivalence'), Code(target_terminology, target_version, item.get('code'), item.get('display')), comments=item.get('comment'))
                    for item in element.get('target')
                ]
                if source_code not in mappings: # Ensure we don't overwrite any mappings
                    mappings[source_code] = mapped_codes_for_source
                else:
                    mappings[source_code] = mappings[source_code] + mapped_codes_for_source
        
        return cls(
            comments = data.get('comments'),
            description = data.get('description'),
            effective_start = data.get('effective_start'),
            effective_end = data.get('effective_end'),
            experimental = data.get('experimental'),
            publisher = data.get('publisher'),
            purpose = data.get('purpose'),
            status = data.get('status'),
            title = data.get('title'),
            version = data.get('version'),
            mappings = mappings,
            raw_json = data
        )

    def get_mapping(self, code, filter_target_system=None, filter_equivalence=None):
        return self.mappings[code]

if __name__ == '__main__':
    # vs_version = ValueSet('test-breast-cancer').load_most_recent_active_version()
    # for code in vs_version.codes:
    #     print(code.serialize())
        
    # metadata = ValueSet('test-breast-cancer').load_versions_metadata_as_df()
    # print(metadata)

    # version = ValueSetVersion.load('529ef7a0-4241-11ec-bec2-fbf6ebf76a60')
    # print(version)

    # failed_version = ValueSet('0bd56b70-9ff6-11ec-95eb-3f73787c1997').load_most_recent_active_version()
    # print(dir(failed_version))

    # concept_map = ConceptMapVersion.load('cbe12636-102f-4ab0-9616-a8684c9f2a21')
    # code = Code('http://projectronin.io/fhir/terminologies/NLPSymptomsExtractionModel', '1', 'ee688a9f-8935-4190-83a6-ea9c970e40cf', "activity change")
    # print(concept_map.get_mapping(code))
    # print(concept_map.mappings)
    
    all_concept_maps = ConceptMap.all_concept_maps_json(restrict_by_status=['active', 'retired', 'in progress'])
    print(all_concept_maps)

