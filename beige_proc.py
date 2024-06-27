import fitz  # PyMuPDF
from sklearn.feature_extraction.text import CountVectorizer
from textblob import TextBlob
import pandas as pd
import numpy as np
import re
import json
import geopandas as gpd
import requests
from shapely.geometry import shape
import matplotlib.pyplot as plt

url_fed = 'https://api.stlouisfed.org/fred'
api_key = 'ffaf5efa63d60fc571735ae9ac0c19df'
statargs = f'api_key={api_key}&file_type=json'

fed_cities = [
	'Boston', 'New York', 'Philadelphia', 'Cleveland',
	'Richmond', 'Atlanta', 'Chicago', 'St. Louis',
	'Minneapolis', 'Kansas City', 'Dallas', 'San Francisco'
	]
fed_cities_dict = {
	1: 'Boston',
	2: 'New York',
	3: 'Philadelphia',
	4: 'Cleveland',
	5: 'Richmond',
	6: 'Atlanta',
	7: 'Chicago',
	8: 'St. Louis',
	9: 'Minneapolis',
	10: 'Kansas City',
	11: 'Dallas',
	12: 'San Francisco'
	}

regex_split_by_fed_city = '|'.join(map(re.escape, fed_cities))



# Step 1: Extract text from the PDF
def extract_text_from_pdf(pdf_path):
	doc = fitz.open(pdf_path)
	text = ""
	for page in doc:
		text += page.get_text()
	text = text.replace("-\n", "")
	# text = text.replace("\n", " ")
	return text

def get_pagenums(text):
	pnums = [int(i) for i in re.findall(u'[\\n|\\D](\\d{1,2})\\n', text)]
	return sorted(list(set(pnums)))

def map_toc(text):
	text0 = text.split('.. ii\n')[1].split('\ni\n')[0]
	trimellps = u'(?:\\s\\.+\\s)'
	toc = re.subn(trimellps, ' ', text0)[0].split('\n')
	tocdict = {}
	for cont in toc:
		contlist = cont.split(' ')
		k = ' '.join(contlist[:-1])
		v = contlist[-1]
		try:
			vnext = toc[toc.index(cont) + 1].split(' ')[-1]
		except:
			vnext = get_pagenums(text)[-1]
		tocdict[k] = list(range(int(v), int(vnext)))
	return tocdict.copy()

# Main script
pdf_path = "BeigeBook/BeigeBook_20240529.pdf"
text = extract_text_from_pdf(pdf_path)
pagenums = get_pagenums(text)
contents = map_toc(text)

text_body = text.split('iii\n')[1]
pages = re.split(u'[\\n|\\D]\\d{1,2}\\n', text_body)


def compile_section(section):
	return ' '.join(pages[i-1].rsplit('Note:')[0] for i in contents[section])

def org_natl_summary(natl_summary_text):
	text_t = natl_summary_text.split('Highlights by Federal Reserve District')
	natl_summary = text_t[0]
	highlights_by_city = re.split(regex_split_by_fed_city, text_t[1])
	text_l = [natl_summary] + highlights_by_city
	cats = ['National Summary'] + fed_cities
	return {cats[i]: text_l[i] for i in range(len(cats))}


sections = {k: compile_section(k).replace('\n', ' ') for k in contents.keys()}
setions = {k.replace('Federal Reserve Bank of ', ''): v for k, v in sections.items()}
text_full = ' '.join(sections.values())

categories = {
    "economic_activity": ["economic activity", "business activity", "consumer spending", "housing demand", "retail spending", "auto sales", "manufacturing activity"],
    "prices": ["prices", "inflation", "price increases", "input costs", "price growth", "wage growth"],
    "labor_market": ["employment", "job gains", "labor availability", "hiring plans", "wages"],
}

def preprocess_text(text):
    text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with a single space
    sentences = text.split('. ')  # Split text into sentences
    return sentences

# Function to calculate sentiment
def get_sentiment(text):
    blob = TextBlob(text)
    return blob.sentiment.polarity

# Function to categorize and analyze sentiment
def categorize_and_analyze(sections, categories):
	ks = list(sections.keys())
	vs = list(sections.values())
	results = {}
	for k, v in sections.items():
		results[k] = {category: 0 for category in list(categories.keys())}
		sentences = preprocess_text(v)
		for sentence in sentences:
			for category, keywords in categories.items():
				if any(keyword in sentence.lower() for keyword in keywords):
					sentiment = get_sentiment(sentence)
					results[k].update({category: sentiment})
	return results

results = categorize_and_analyze(sections, categories)
df_summary = pd.DataFrame(results)
df_summary.columns = ['National Summary'] + fed_cities
df_summary = df_summary.T
df_summary.loc['average_sentiment', :] = df_summary.mean()
df_summary['overall_sentiment'] = df_summary['economic_activity'] - df_summary['prices'] + df_summary['labor_market']
df_summary['name'] = df_summary.index
df_summary.reset_index(drop=True, inplace=True)


def getmap_frb_dists():
	r = requests.get('https://fred.stlouisfed.org/graph/api/maps/shapes/byseries/D8POP')
	data = r.json()
	geodata = data['features']
	geo_shapes = []
	for i in geodata:
		if 'id' and 'Dist_Nm' in i['properties'].keys():
			tempdict = {
				'id': i['properties']['id'],
				'name': i['properties']['Dist_Nm'],
				'geometry': shape(i['geometry']),
				}
			geo_shapes.append(tempdict)
	geoframe = gpd.GeoDataFrame(geo_shapes)
	geoframe['geometry'] = geoframe['geometry'].set_crs('EPSG:3395')
	return geoframe.copy()


def getmap_states():
	r = requests.get(f'https://fred.stlouisfed.org/graph/api/maps/shapes/byseries/SMU06000000500000003')
	data = r.json()
	features = data['features']
	geo_shapes = []
	for i in features:
		if 'id' in i.keys() and 'name' in i['properties'].keys():
			geo_shapes.append({
				'id': i['id'],
				'name': i['properties']['name'],
				'geometry': shape(i['geometry']),
				})
	geoframe = gpd.GeoDataFrame(geo_shapes)
	geoframe['geometry'] = geoframe['geometry'].set_crs('EPSG:3395')
	# geoframe['geometry'] = geoframe['geometry'].set_crs('urn:ogc:def:crs:EPSG:102004')
	return geoframe.copy()



def load_geo(item='frb', ext='geojson'):
	geoframe = gpd.read_file(f'C:/KL_Capital Dropbox/kldata/klcpy/scripts/cbvis/shapes/{item}.{ext}')
	geoframe['geometry'] = geoframe['geometry'].set_crs('EPSG:3395')
	return geoframe.copy()




gdf_bases = {
	'frb': getmap_frb_dists(),
	'states': getmap_states(),
	}
gdf_frb = gdf_bases['frb'].copy()
gdf_frb['geometry'] = gdf_frb['geometry'].set_crs('EPSG:3395')
# gdf = gdf.merge(df_summary[['name','overall_sentiment']].copy(), on='name', how='left')
# gdf.plot(column='overall_sentiment', legend=True, cmap='rg').set_axis_off()
# plt.show()

