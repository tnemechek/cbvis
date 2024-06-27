import requests, json
import pandas as pd
from tqdm import tqdm

url_fred = 'https://api.stlouisfed.org/fred'
api_key = 'ffaf5efa63d60fc571735ae9ac0c19df'

def get_fred(url_ext, xparams=None):
	url_fred = 'https://api.stlouisfed.org/fred'
	api_key = 'ffaf5efa63d60fc571735ae9ac0c19df'
	temp_params = {
	'api_key': api_key,
	'file_type': 'json'
	}
	if xparams: temp_params.update(xparams)
	return requests.get(url_fred + url_ext, params=temp_params).json()

def get_subcategories(category_id):
	rf = get_fred('/category/children', {'category_id': category_id})
	if len(rf['categories']) == 0:
		return None
	else:
		return pd.DataFrame(rf['categories']).sort_values(by='id').reset_index(drop=True)

def get_populate_subcategories(dff_cats, deadends):
	given_ids = dff_cats['id'].unique().tolist()
	deadends_new = []
	ids = list(set(given_ids) - set(deadends) - set(dff_cats['parent_id'].unique().to_list()))
	if len(ids) == 0:
		return dff_cats, deadends
	for i in tqdm(ids, total=len(ids), ncols=100):
		if i in deadends:
			continue
		else:
			dff_cats_t = get_subcategories(i)
			if dff_cats_t is not None:
				dff_cats_t = dff_cats_t[~dff_cats_t['id'].isin(dff_cats['id'].to_list())]
				dff_cats = pd.concat([dff_cats, dff_cats_t], ignore_index=True)
			else:
				deadends_new.append(i)
				continue

	dff_cats = dff_cats.sort_values(by='id').reset_index(drop=True)
	return dff_cats.copy(), deadends_new


def get_categories_all(start_category_id=0):
	dff = get_subcategories(start_category_id)
	dff_t = None
	deadends = []
	for x in range(10):
		dff_t, deadends_t = get_populate_subcategories(dff, deadends)
		deadends.extend(deadends_t)
		if dff_t.equals(dff):
			break
		else:
			dff = dff_t.copy()
			dff_t = None
		dff = dff.drop_duplicates().reset_index(drop=True)
	dff = dff.sort_values(by=['id', 'parent_id']).reset_index(drop=True)
	dff = dff.rename(columns={'id': 'category_id'})
	dff = dff.drop(columns=['notes'], errors='ignore')
	return dff.copy()

if __name__ == '__main__':
	df = get_categories_all()
	df.to_pickle('df_fred_categories.pkl')