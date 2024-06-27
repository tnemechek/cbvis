import requests, json
import pandas as pd
from .conn_psql import *


url_fred = 'https://api.stlouisfed.org/fred'
api_key = 'ffaf5efa63d60fc571735ae9ac0c19df'
statargs = f'api_key={api_key}&file_type=json'
params = {
	'api_key': api_key,
	'file_type': 'json'
	}

sources = {
	'frb': {
		'source_id': 1,
		'releases': [{'release_id': 13, 'release_name': 'G.17 Industrial Production and Capacity Utilization'}, {'release_id': 14, 'release_name': 'G.19 Consumer Credit'}, {'release_id': 15, 'release_name': 'G.5 Foreign Exchange Rates'}, {'release_id': 17, 'release_name': 'H.10 Foreign Exchange Rates'}, {'release_id': 18, 'release_name': 'H.15 Selected Interest Rates'}, {'release_id': 19, 'release_name': 'H.3 Aggregate Reserves of Depository Institutions and the Monetary Base'}, {'release_id': 20, 'release_name': 'H.4.1 Factors Affecting Reserve Balances'}, {'release_id': 21, 'release_name': 'H.6 Money Stock Measures'}, {'release_id': 22, 'release_name': 'H.8 Assets and Liabilities of Commercial Banks in the United States'}, {'release_id': 52, 'release_name': 'Z.1 Financial Accounts of the United States'}, {'release_id': 86, 'release_name': 'Commercial Paper'}, {'release_id': 89, 'release_name': 'Household Debt Service and Financial Obligations Ratios'}, {'release_id': 101, 'release_name': 'FOMC Press Release'}, {'release_id': 103, 'release_name': 'Discount Rate Meeting Minutes'}, {'release_id': 104, 'release_name': 'Federal Reserve Bulletin'}, {'release_id': 106, 'release_name': 'M2 Own Rate'}, {'release_id': 121, 'release_name': 'H.6 Historical Data'}, {'release_id': 122, 'release_name': 'H.4.1 Factors Affecting Reserve Balances (data not included in press release)'}, {'release_id': 131, 'release_name': 'G.13 Selected Interest Rates'}, {'release_id': 170, 'release_name': 'U.S. Foreign Exchange Intervention'}, {'release_id': 185, 'release_name': 'Interest Rate on Reserve Balances'}, {'release_id': 186, 'release_name': 'G.5A Foreign Exchange Rates'}, {'release_id': 191, 'release_name': 'Senior Loan Officer Opinion Survey on Bank Lending Practices'}, {'release_id': 216, 'release_name': 'E.2 Survey of Terms of Business Lending'}, {'release_id': 231, 'release_name': 'Charge-Off and Delinquency Rates on Loans and Leases at Commercial Banks'}, {'release_id': 245, 'release_name': 'Summary Measures of the Foreign Exchange Value of the Dollar'}, {'release_id': 311, 'release_name': 'Currency and Coin Services'}, {'release_id': 316, 'release_name': 'G.20 Finance Companies'}, {'release_id': 337, 'release_name': 'Federal Reserve Board of Governors Labor Market Conditions Index'}, {'release_id': 354, 'release_name': 'An Arbitrage-Free Three-Factor Term Structure Model and the Recent Behavior of Long-Term Yields and Distant-Horizon Forward Rates'}, {'release_id': 388, 'release_name': 'Banking and Monetary Statistics, 1914-1941'}, {'release_id': 396, 'release_name': 'G.17.2 Retail Instalment Credit at Furniture and Household Appliance Stores'}, {'release_id': 453, 'release_name': 'Distributional Financial Accounts'}, {'release_id': 460, 'release_name': 'Seasonal Factors for Domestic Auto and Truck Production'}, {'release_id': 571, 'release_name': 'Senior Credit Officer Opinion Survey on Dealer Financing Terms'}]
		},
	'dowjones': 11,
	'bea': 18,
	'bls': 22,
	'boj': 37,
	'adp': 42,
	'fomc': 98
	}


release_ids = {
	'fomc_pr': 101,
	'chicago_natl_finconds': 221
	}

# data_schema:
# | date (yyyymmdd) | mapent_id | series_id | unit | value |
# | 202040605       | frb-1     | d1watal   | lin  | 342.5 |
# | ............... | ......... | ......... | .... | ..... |


map = {
	'frb': {
		'frb-1': {'name': 'boston', 'id': 1, 'title': 'Boston', 'mapent_id': 'frb-1', 'map': 'frb'},
		'frb-2': {'name': 'new_york', 'id': 2, 'title': 'New York', 'mapent_id': 'frb-2', 'map': 'frb'},
		'frb-3': {'name': 'philadelphia', 'id': 3, 'title': 'Philadelphia', 'mapent_id': 'frb-3', 'map': 'frb'},
		'frb-4': {'name': 'cleveland', 'id': 4, 'title': 'Cleveland', 'mapent_id': 'frb-4', 'map': 'frb'},
		'frb-5': {'name': 'richmond', 'id': 5, 'title': 'Richmond', 'mapent_id': 'frb-5', 'map': 'frb'},
		'frb-6': {'name': 'atlanta', 'id': 6, 'title': 'Atlanta', 'mapent_id': 'frb-6', 'map': 'frb'},
		'frb-7': {'name': 'chicago', 'id': 7, 'title': 'Chicago', 'mapent_id': 'frb-7', 'map': 'frb'},
		'frb-8': {'name': 'st_louis', 'id': 8, 'title': 'St. Louis', 'mapent_id': 'frb-8', 'map': 'frb'},
		'frb-9': {'name': 'minneapolis', 'id': 9, 'title': 'Minneapolis', 'mapent_id': 'frb-9', 'map': 'frb'},
		'frb-10': {'name': 'kansas_city', 'id': 10, 'title': 'Kansas City', 'mapent_id': 'frb-10', 'map': 'frb'},
		'frb-11': {'name': 'dallas', 'id': 11, 'title': 'Dallas', 'mapent_id': 'frb-11', 'map': 'frb'},
		'frb-12': {'name': 'san_francisco', 'id': 12, 'title': 'San Francisco', 'mapent_id': 'frb-12', 'map': 'frb'}
		},
	'bea': {
		'bea-ne': {'name': 'new_england', 'id': 'ne', 'title': 'New England', 'mapent_id': 'bea-ne', 'map': 'bea', 'constits_mapent_ids': ['us-me', 'us-nh', 'us-vt', 'us-ma', 'us-ri', 'us-ct'], 'constits_map': 'us_states'},
		'bea-me': {'name': 'mideast', 'id': 'me', 'title': 'Mideast', 'mapent_id': 'bea-me', 'map': 'bea', 'constits_mapent_ids': ['us-de', 'us-md', 'us-dc', 'us-pa', 'us-nj', 'us-ny'], 'constits_map': 'us_states'},
		'bea-gl': {'name': 'great_lakes', 'id': 'gl', 'title': 'Great Lakes', 'mapent_id': 'bea-gl', 'map': 'bea', 'constits_mapent_ids': ['us-oh', 'us-mi', 'us-in', 'us-il', 'us-wi'], 'constits_map': 'us_states'},
		'bea-pl': {'name': 'plains', 'id': 'pl', 'title': 'Plains', 'mapent_id': 'bea-pl', 'map': 'bea', 'constits_mapent_ids': ['us-nd', 'us-sd', 'us-ne', 'us-ks', 'us-mo', 'us-ia', 'us-mn'], 'constits_map': 'us_states'},
		'bea-se': {'name': 'southeast', 'id': 'se', 'title': 'Southeast', 'mapent_id': 'bea-se', 'map': 'bea', 'constits_mapent_ids': ['us-wv', 'us-va', 'us-nc', 'us-sc', 'us-ga', 'us-fl', 'us-tn', 'us-ky', 'us-al', 'us-ms', 'us-la', 'us-ar'], 'constits_map': 'us_states'},
		'bea-sw': {'name': 'southwest', 'id': 'sw', 'title': 'Southwest', 'mapent_id': 'bea-sw', 'map': 'bea', 'constits_mapent_ids': ['us-tx', 'us-ok', 'us-nm', 'us-az'], 'constits_map': 'us_states'},
		'bea-rm': {'name': 'rocky_mountain', 'id': 'rm', 'title': 'Rocky Mountain', 'mapent_id': 'bea-rm', 'map': 'bea', 'constits_mapent_ids': ['us-id', 'us-mt', 'us-wy', 'us-co', 'us-ut'], 'constits_map': 'us_states'},
		'bea-fw': {'name': 'far_west', 'id': 'fw', 'title': 'Far West', 'mapent_id': 'bea-fw', 'map': 'bea', 'constits_mapent_ids': ['us-wa', 'us-or', 'us-ca', 'us-nv', 'us-ak', 'us-hi'], 'constits_map': 'us_states'}
		},
	'us_states': {
		'ak': {'name': 'alaska', 'id': 'ak', 'title': 'Alaska', 'mapent_id': 'us-ak', 'map': 'usa_states'},
		'al': {'name': 'alabama', 'id': 'al', 'title': 'Alabama', 'mapent_id': 'us-al', 'map': 'usa_states'}, 'ar': {'name': 'arkansas', 'id': 'ar', 'title': 'Arkansas', 'mapent_id': 'us-ar', 'map': 'usa_states'}, 'az': {'name': 'arizona', 'id': 'az', 'title': 'Arizona', 'mapent_id': 'us-az', 'map': 'usa_states'}, 'ca': {'name': 'california', 'id': 'ca', 'title': 'California', 'mapent_id': 'us-ca', 'map': 'usa_states'}, 'co': {'name': 'colorado', 'id': 'co', 'title': 'Colorado', 'mapent_id': 'us-co', 'map': 'usa_states'}, 'ct': {'name': 'connecticut', 'id': 'ct', 'title': 'Connecticut', 'mapent_id': 'us-ct', 'map': 'usa_states'}, 'de': {'name': 'delaware', 'id': 'de', 'title': 'Delaware', 'mapent_id': 'us-de', 'map': 'usa_states'}, 'fl': {'name': 'florida', 'id': 'fl', 'title': 'Florida', 'mapent_id': 'us-fl', 'map': 'usa_states'}, 'ga': {'name': 'georgia', 'id': 'ga', 'title': 'Georgia', 'mapent_id': 'us-ga', 'map': 'usa_states'}, 'hi': {'name': 'hawaii', 'id': 'hi', 'title': 'Hawaii', 'mapent_id': 'us-hi', 'map': 'usa_states'}, 'ia': {'name': 'iowa', 'id': 'ia', 'title': 'Iowa', 'mapent_id': 'us-ia', 'map': 'usa_states'}, 'id': {'name': 'idaho', 'id': 'id', 'title': 'Idaho', 'mapent_id': 'us-id', 'map': 'usa_states'}, 'il': {'name': 'illinois', 'id': 'il', 'title': 'Illinois', 'mapent_id': 'us-il', 'map': 'usa_states'}, 'in': {'name': 'indiana', 'id': 'in', 'title': 'Indiana', 'mapent_id': 'us-in', 'map': 'usa_states'}, 'ks': {'name': 'kansas', 'id': 'ks', 'title': 'Kansas', 'mapent_id': 'us-ks', 'map': 'usa_states'}, 'ky': {'name': 'kentucky', 'id': 'ky', 'title': 'Kentucky', 'mapent_id': 'us-ky', 'map': 'usa_states'}, 'la': {'name': 'louisiana', 'id': 'la', 'title': 'Louisiana', 'mapent_id': 'us-la', 'map': 'usa_states'}, 'ma': {'name': 'massachusetts', 'id': 'ma', 'title': 'Massachusetts', 'mapent_id': 'us-ma', 'map': 'usa_states'}, 'md': {'name': 'maryland', 'id': 'md', 'title': 'Maryland', 'mapent_id': 'us-md', 'map': 'usa_states'}, 'me': {'name': 'maine', 'id': 'me', 'title': 'Maine', 'mapent_id': 'us-me', 'map': 'usa_states'}, 'mi': {'name': 'michigan', 'id': 'mi', 'title': 'Michigan', 'mapent_id': 'us-mi', 'map': 'usa_states'}, 'mn': {'name': 'minnesota', 'id': 'mn', 'title': 'Minnesota', 'mapent_id': 'us-mn', 'map': 'usa_states'}, 'mo': {'name': 'missouri', 'id': 'mo', 'title': 'Missouri', 'mapent_id': 'us-mo', 'map': 'usa_states'}, 'ms': {'name': 'mississippi', 'id': 'ms', 'title': 'Mississippi', 'mapent_id': 'us-ms', 'map': 'usa_states'}, 'mt': {'name': 'montana', 'id': 'mt', 'title': 'Montana', 'mapent_id': 'us-mt', 'map': 'usa_states'}, 'nc': {'name': 'north_carolina', 'id': 'nc', 'title': 'North Carolina', 'mapent_id': 'us-nc', 'map': 'usa_states'}, 'nd': {'name': 'north_dakota', 'id': 'nd', 'title': 'North Dakota', 'mapent_id': 'us-nd', 'map': 'usa_states'}, 'ne': {'name': 'nebraska', 'id': 'ne', 'title': 'Nebraska', 'mapent_id': 'us-ne', 'map': 'usa_states'}, 'nh': {'name': 'new_hampshire', 'id': 'nh', 'title': 'New Hampshire', 'mapent_id': 'us-nh', 'map': 'usa_states'}, 'nj': {'name': 'new_jersey', 'id': 'nj', 'title': 'New Jersey', 'mapent_id': 'us-nj', 'map': 'usa_states'}, 'nm': {'name': 'new_mexico', 'id': 'nm', 'title': 'New Mexico', 'mapent_id': 'us-nm', 'map': 'usa_states'}, 'nv': {'name': 'nevada', 'id': 'nv', 'title': 'Nevada', 'mapent_id': 'us-nv', 'map': 'usa_states'}, 'ny': {'name': 'new_york', 'id': 'ny', 'title': 'New York', 'mapent_id': 'us-ny', 'map': 'usa_states'}, 'oh': {'name': 'ohio', 'id': 'oh', 'title': 'Ohio', 'mapent_id': 'us-oh', 'map': 'usa_states'}, 'ok': {'name': 'oklahoma', 'id': 'ok', 'title': 'Oklahoma', 'mapent_id': 'us-ok', 'map': 'usa_states'}, 'or': {'name': 'oregon', 'id': 'or', 'title': 'Oregon', 'mapent_id': 'us-or', 'map': 'usa_states'}, 'pa': {'name': 'pennsylvania', 'id': 'pa', 'title': 'Pennsylvania', 'mapent_id': 'us-pa', 'map': 'usa_states'}, 'ri': {'name': 'rhode_island', 'id': 'ri', 'title': 'Rhode Island', 'mapent_id': 'us-ri', 'map': 'usa_states'}, 'sc': {'name': 'south_carolina', 'id': 'sc', 'title': 'South Carolina', 'mapent_id': 'us-sc', 'map': 'usa_states'}, 'sd': {'name': 'south_dakota', 'id': 'sd', 'title': 'South Dakota', 'mapent_id': 'us-sd', 'map': 'usa_states'}, 'tn': {'name': 'tennessee', 'id': 'tn', 'title': 'Tennessee', 'mapent_id': 'us-tn', 'map': 'usa_states'}, 'tx': {'name': 'texas', 'id': 'tx', 'title': 'Texas', 'mapent_id': 'us-tx', 'map': 'usa_states'}, 'ut': {'name': 'utah', 'id': 'ut', 'title': 'Utah', 'mapent_id': 'us-ut', 'map': 'usa_states'}, 'va': {'name': 'virginia', 'id': 'va', 'title': 'Virginia', 'mapent_id': 'us-va', 'map': 'usa_states'}, 'vt': {'name': 'vermont', 'id': 'vt', 'title': 'Vermont', 'mapent_id': 'us-vt', 'map': 'usa_states'}, 'wa': {'name': 'washington', 'id': 'wa', 'title': 'Washington', 'mapent_id': 'us-wa', 'map': 'usa_states'}, 'wi': {'name': 'wisconsin', 'id': 'wi', 'title': 'Wisconsin', 'mapent_id': 'us-wi', 'map': 'usa_states'}, 'wv': {'name': 'west_virginia', 'id': 'wv', 'title': 'West Virginia', 'mapent_id': 'us-wv', 'map': 'usa_states'}, 'wy': {'name': 'wyoming', 'id': 'wy', 'title': 'Wyoming', 'mapent_id': 'us-wy', 'map': 'usa_states'}, 'dc': {'name': 'district_of_columbia', 'id': 'dc', 'title': 'District of Columbia', 'mapent_id': 'us-dc', 'map': 'usa_states'}
		},
	}

# def fred_source(source_id):
# 	data = get_fred(
# 		'/source',
# 		{'source_id': source_id}
# 		)['sources'][0]
# 	return {'source_id': data['id'], 'source_name': data['name']}
#
# def fred_release_sources(release_id):
# 	data = get_fred(
# 		'/release/sources',
# 		{'release_id': release_id}
# 		)['sources']
#
# 	# return [{'source_id': x['id'], 'name': x['name']} for x in data]
# 	return {'source_id': data[0]['id'], 'source_name': data[0]['name']}
#
# def fred_release(release_id):
# 	data = get_fred(
# 		'/release',
# 		{'release_id': release_id}
# 		)['releases'][0]
# 	data_src = fred_release_sources(release_id)
# 	return {
# 		'release_id': data['id'],
# 		'release_name': data['name'],
# 		'source_id': data_src['source_id'],
# 		'source_name': data_src['source_name']
# 		}
#
# def fred_series_release(series_id):
# 	data = get_fred(
# 		'/series/release',
# 		{'series_id': series_id}
# 		)['releases'][0]
# 	data_release = fred_release(data['id'])
# 	return {
# 		'series_id': series_id,
# 		'release_id': data['id'],
# 		'release_name': data['name'],
# 		'source_id': data_release['source_id'],
# 		'source_name': data_release['source_name']
# 		}
# def fred_series(series_id, mapent_id=None):
# 	data = get_fred(
# 		'/series',
# 		{'series_id': series_id}
# 		)['seriess'][0]
# 	data_release = fred_series_release(series_id)
# 	mapx, ent_id = mapent_id.split('-') if mapent_id else (None, None)
# 	return {
# 		'series_id': data['id'],
# 		'series_name': data['title'],
# 		'series_raw': data['id'].replace(str(ent_id), '{id}') if ent_id else None,
# 		'units': data['units'],
# 		'frequency': data['frequency_short'],
# 		'seasonal_adjustment': 1 if data['seasonal_adjustment_short'] == 'SA' else 0,
# 		'last_updated': data['last_updated'],
# 		'observation_start': data['observation_start'],
# 		'observation_end': data['observation_end'],
# 		'release_id': data_release['release_id'],
# 		'release_name': data_release['release_name'],
# 		'source_id': data_release['source_id'],
# 		'source_name': data_release['source_name'],
# 		'mapent_id': mapent_id,
# 		'map': mapx
# 		}
# def fred_release_series(release_id, v=True):
# 	data = get_fred(
# 		'/release/series',
# 		{'release_id': release_id}
# 		)['seriess']
# 	series_ids = [x['id'] for x in data]
# 	if not v:
# 		return series_ids
# 	else:
# 		return [fred_series(x) for x in series_ids]
#
#
# def fred_releases(v=True):
# 	data = get_fred('/releases', {})['releases']
# 	release_ids = [x['id'] for x in data]
# 	if not v:
# 		return release_ids
# 	else:
# 		return [fred_release_series(x) for x in release_ids]

def get_fred(url_ext, xparams=None):
	url_fred = 'https://api.stlouisfed.org/fred'
	temp_params = {
	'api_key': api_key,
	'file_type': 'json'
	}
	if xparams: temp_params.update(xparams)
	return requests.get(url_fred + url_ext, params=temp_params).json()


def fred_series_obs(series_id):
	data = get_fred('/series/observations', {'series_id': series_id})['observations']
	df = pd.DataFrame(data)
	df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
	df.drop(columns=['realtime_start', 'realtime_end'], inplace=True)
	return df.copy()

def get_release_series(release_id):
	r_self = get_fred('/release', {'release_id': release_id})
	r_srcs = get_fred('/release/sources', {'release_id': release_id})
	r_rls = get_fred('/release/series', {'release_id': release_id})
	dff = pd.DataFrame(r_rls['seriess'])
	dff = dff.drop(columns=['realtime_start', 'realtime_end', 'popularity', 'group_popularity', 'notes', 'seasonal_adjustment'])
	dff = dff.rename(columns={'id': 'series_id', 'title': 'series_name', 'seasonal_adjustment_short': 'seasonal_adjustment'})
	for c in ['observation_start', 'observation_end', 'last_updated']:
		dff[c] = pd.to_datetime(dff[c]).dt.strftime('%Y-%m-%d')
	# 	dff[c] = dff[c].str.replace('-', '').astype(int)
	# dff['last_updated'] = pd.to_datetime(dff['last_updated']).dt.strftime('%Y%m%d')
	dff['release_id'] = release_id
	dff['release_name'] = r_self['releases'][0]['name']
	dff['source_id'] = r_srcs['sources'][0]['id']
	dff['source_name'] = r_srcs['sources'][0]['name']
	return dff.copy()

def get_release_series_obs(release_id):
	dff_srs = get_release_series(release_id)
	series_ids = dff_srs['series_id'].tolist()
	obs = []
	for i in series_ids:
		dff_t = fred_series_obs(i)
		dff_t['series_id'] = i
		obs.append(dff_t)
	dff_obs = pd.concat(obs).reset_index(drop=True)
	dff_obs = dff_obs[dff_obs['value'] != '.'].copy()
	dff_obs['value'] = dff_obs['value'].astype(float)
	return dff_obs.copy()

# def psql_put_release_series(release_id):
# 	dff = get_release_series(release_id)
# 	r_put = psql_put(dff, 'data', 'fred_release_series')
# 	return r_put
#
# def psql_put_series_obs(series_id):
# 	r_obs = get_fred('/series/observations', {'series_id': series_id})
# 	dff = pd.DataFrame(r_obs['observations'])
# 	dff['date'] = pd.to_datetime(dff['date'])
# 	dff['series_id'] = series_id
# 	r_put = psql_put(dff, 'data', 'fred_series_obs')
# 	return r_put


# if __name__ == '__main__':
# 	response = get_bbook()
# 	data = json.loads(response.text)
# 	# df = pd.DataFrame(data['sources'])
# 	# df.sort_values(by='name', inplace=True)
# 	# df = pd.DataFrame(data['release_date'])
# 	# df.sort_values(by='release_name', inplace=True)
# 	df = pd.DataFrame(data['seriess'])
# 	df.sort_values(by='title', inplace=True)