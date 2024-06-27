import fitz
from scripts.cbvis.beige_proc import *
import gensim.downloader as api
from transformers import BertTokenizer, BertForSequenceClassification
import torch
from scipy.special import softmax


word_vectors = api.load('glove-wiki-gigaword-100')

model_name = 'yiyanghkust/finbert-tone'
tokenizer = BertTokenizer.from_pretrained(model_name)
model = BertForSequenceClassification.from_pretrained(model_name)

def get_related(themeword, topn=9):
	try:
		similar_words = word_vectors.most_similar(themeword, topn=topn)
		keywords = [themeword] + [word for word, _ in similar_words]
		return keywords
	except Exception as err:
		print(err)
		print(f'Word "{themeword}" not found in vocabulary')
		return [themeword]


def get_sentences_with_keywords(text, keywords):
	sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)
	return [sentence for sentence in sentences if any(keyword in sentence.lower() for keyword in keywords)]


def analyze_sentiment(sentences):
	sentiments = []
	for sentence in sentences:
		inputs = tokenizer(sentence, return_tensors='pt', truncation=True, padding=True)
		with torch.no_grad():
			outputs = model(**inputs)
		scores = outputs.logits[0].numpy()
		scores = softmax(scores)
		sentiment_score = (scores[2] - scores[0]) * 100
		sentiments.append(sentiment_score)
	return np.mean(sentiments)


def categorize_and_analyze(sections, themeword):
	_sections = {k.replace('Federal Reserve Bank of ', ''): v for k, v in sections.items()
	             if k.replace('Federal Reserve Bank of ', '') in gdf_frb['name'].values}
	sentiments = []
	keywords = get_related(themeword)
	for district, text in _sections.items():
		sentences = get_sentences_with_keywords(text, keywords)
		sentiment = analyze_sentiment(sentences)
		sentiments.append({'name': district, f'{themeword}_sentiment': sentiment})
	dfsent = pd.DataFrame(sentiments)
	# dfsent.columns = ['name', f'{themeword}_sentiment']
	return dfsent.copy()
	# return pd.DataFrame(sentiments, columns=['name', f'{themeword}_sentiment'])


datas = []
for did in range(1, 13):
	r = requests.get(url_fed + f'/series/observations?series_id=D{did}WATAL' + f'&{statargs}')
	data = r.json()
	dff = pd.DataFrame(data['observations'])
	dff['id'] = did
	dff['name'] = fed_cities_dict[did]
	datas.append(dff.drop(columns=['realtime_start', 'realtime_end']))
df = pd.concat(datas)
df = df.pivot(index='date', columns='name', values='value').copy()
df = df.reset_index()
df['date'] = pd.to_datetime(df['date'])


if __name__ == '__main__':
	theme = 'growth'
	df_theme_sent = categorize_and_analyze(sections, theme)
	gdf = gdf_frb.merge(df_theme_sent, on='name', how='left')
	gdf.plot(column=f'{theme}_sentiment', legend=True, cmap='coolwarm', figsize=(20, 12), ).set_axis_off()
	plt.title(f'Sentiment Analysis on "{theme}" and associated keywords\nin Beige Book, by Federal Reserve District', fontsize=22, fontweight='bold')
	plt.show()

