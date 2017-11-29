"""
North Carolina has CSV files containing precinct-level results for each county and all offices
for all years back to 2000, except for the 2000 primary. There is one zip file per election,
with additional text files for county and race-level summaries. For the 2000 primary, individual
Excel files are available for each office and party combination.
"""
from future import standard_library
standard_library.install_aliases()
from os.path import join
import json
import datetime
import urllib.parse

from openelex import PROJECT_ROOT
from openelex.base.datasource import BaseDatasource

class Datasource(BaseDatasource):

    # PUBLIC INTERFACE
    def mappings(self, year=None):
        """Return array of dicts containing source url and
        standardized filename for raw results file, along
        with other pieces of metadata
        """
        mappings = []
        for yr, elecs in list(self.elections(year).items()):
            mappings.extend(self._build_metadata(yr, elecs))
        return mappings

    def target_urls(self, year=None):
        "Get list of source data urls, optionally filtered by year"
        return [item['raw_url'] for item in self.mappings(year)]

    def filename_url_pairs(self, year=None):
        return [(item['generated_filename'], item['raw_url'])
                for item in self.mappings(year)]

    def mappings_for_url(self, url):
        return [mapping for mapping in self.mappings() if mapping['raw_url'] == url]

    # PRIVATE METHODS

    def _build_metadata(self, year, elections):
        meta = []
        year_int = int(year)
        for election in elections:
            if election['slug'] == 'nc-2000-05-02-primary':
                results = [x for x in self._url_paths() if x['date'] == election['start_date']]
                for result in results:
                    generated_filename = self._generate_office_filename(election, result)
                    meta.append({
                        "generated_filename": generated_filename,
                        "raw_url": result['url'],
                        "ocd_id": 'ocd-division/country:us/state:nc',
                        "name": 'North Carolina',
                        "election": election['slug']
                    })
            else:
                results = [x for x in self._url_paths() if x['date'] == election['start_date']]
                for result in results:
                    if result['date'] in ('2000-11-07', '2002-11-05', '2002-09-10', '2006-05-02', '2006-09-12', '2006-11-07', '2006-05-30', '2008-05-06'):
                        format = '.txt'
                    else:
                        format = '.csv'
                    generated_filename = self._generate_filename(election, format)
                    meta.append({
                        "generated_filename": generated_filename,
                        'raw_url': election['direct_links'][0],
                        'raw_extracted_filename': result['raw_extracted_filename'],
                        "ocd_id": 'ocd-division/country:us/state:nc',
                        "name": 'North Carolina',
                        "election": election['slug']
                    })
        return meta

    def _generate_filename(self, election, format):
        if election['special']:
            election_type = 'special__' + election['race_type'].replace("-","__") + '__precinct'
        else:
            election_type = election['race_type'].replace("-","__") + '__precinct'
        bits = [
            election['start_date'].replace('-',''),
            self.state.lower(),
            election_type
        ]
        name = "__".join(bits) + format
        return name

    def _generate_office_filename(self, election, result):
        if result['party'] == '':
            bits = [
                    election['start_date'].replace('-',''),
                    self.state.lower(),
                    election['race_type'],
                    result['office'],
                    'precinct'
                ]
        else:
            bits = [
                election['start_date'].replace('-',''),
                self.state.lower(),
                result['party'],
                election['race_type'],
                result['office'],
                'precinct'
            ]
        name = "__".join(bits)+'.xls'
        return name

    def _jurisdictions(self):
        """North Carolina counties"""
        m = self.jurisdiction_mappings()
        mappings = [x for x in m if x['county'] != ""]
        return mappings
