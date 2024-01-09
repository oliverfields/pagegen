from re import sub
from pagegen.utility import relative_path, load_file
from pagegen.utility_no_deps import report_error, report_warning
from pagegen.constants import STOPWORDSFILE, NEWLINE

class searchindex:

	def __init__(self, stop_words_file=STOPWORDSFILE):
		self.terms={} # Contains terms as key and Hit objects as values
		self.index_xpaths=[] # Xpath to nodes to look for indexable content in
		self.content_tags=['p','li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'td', 'th', 'strong', 'em', 'i', 'b', 'a', 'blockquote', 'div', 'span', 'pre', 'abbr', 'address', 'cite', 'code', 'del', 'dfn', 'ins', 'kbd', 'q', 'samp', 'small', 'sub', 'sup', 'var', 'dt', 'dd', 'legend', 'caption', 'article', 'aside', 'details', 'figcaption', 'section', 'summary', 'title'] # HTML tags that may contain searchable content
		self.meta_tags=['description'] # Meta tags attributes that may contain searchable content
		self.stop_words=[]

		try:
			stop_words=load_file(stop_words_file)
			for stop_word in stop_words.split(NEWLINE):
				self.stop_words.append(stop_word)
		except:
			report_warning("Stop words not loaded from '%s'" % STOPWORDSFILE)


	def build_json_index(self):
		''' Create json index '''

		urls={}
		id=1

		i='{'
		i+='"terms":{'
		for term, hits in self.terms.items():

			# Assign id to each unique url in hits
			for hit in hits:
				if not hit.url in urls.keys():
					urls[hit.url]=hit
					hit.id=id
					id+=1
				else:
					hit.id=urls[hit.url].id

			i+='"%s":[' % term
			for hit in sorted(hits, key=lambda hit: hit.weight, reverse=True):
				#i+='"%s":"%s",' % (hit.url, hit.description)
				i+='%s,' % hit.id
			i=i.rstrip(',')
			i+='],'
		i=i.rstrip(',')
		i+='},'

		i+='"urls":{'
		for url, hit in urls.items():
			i+='"%s":["%s","%s","%s"],' % (hit.id, hit.url, hit.title.replace('\\', '\\\\'), hit.description)
		i=i.rstrip(',')
		i+='}'
		i+='}'

		return i


	def index_string(self, string, url, weight, title, description):
		''' For each word in string add to index if not a stop word '''

		# Index only lowercase
		string_original=string
		string=string.lower()

		if not string:
			return True

		#print "indexing -> %s" % string

		for word in string.split(' '):

			word=sub('[^a-z0-9]*', '', word)
			word=word.strip()

			if len(word) == 0:
				continue

			if word in self.stop_words:
				#print 'Word "%s" is stop word for %s' % (word, hit.url)
				continue

			hit=Hit(word, url, weight, string_original, title, description)

			if word in self.terms.keys():
				#print 'Considering "%s"..' % word
				# Return if hit for this file alredy added
				if not self.is_hit_indexed(hit):
					#print 'Adding "%s" to index for %s (%s)' % (repr(word), hit.url, weight)
					hits=self.terms[word]
					hits.append(hit)
					self.terms[word]=hits
				# Update weight if is indexed
				else:
					for indexed_hit in self.terms[word]:
						if indexed_hit.term==hit.term and indexed_hit.url==hit.url and indexed_hit.weight < hit.weight:
							#print "Increasing weight for hit '%s'" % hit.url
							indexed_hit.weight=hit.weight

			else:
				#print 'Adding "%s" to index for %s (%s)' % (repr(word), hit.url, weight)
				self.terms[word]=[hit]

		return True


	def is_hit_indexed(self, hit):
		''' Check if hit is indexed for given word and url '''
		for indexed_hit in self.terms[hit.term]:
			if hit.term==indexed_hit.term and hit.url==indexed_hit.url:
				return True
		return False


	def index_file(self, file, url, title, description):
		''' Search in file for relevant xpaths for containing tags that may contain indexable content '''

		from lxml import etree

		try:
			data=load_file(file)
			tree = etree.HTML(data)
		except Exception as e:
			report_error(1, "Unable to index '%s': %s" % (relative_path(file), e))

		# Loop over meta tags
		for search_attribute in self.meta_tags:
			try:
				result=tree.xpath("//meta[@name='"+search_attribute+"']")
				for tag in result:
					self.index_string(tag.attrib['content'], url, 5, title, description)
			except:
				pass # No meta tags found, fair enough

		# Index title
		try:
			result=tree.xpath("/html/head/title")
			for tag in result:
				text=''
				if tag.text:
					text+=tag.text+' '
				if tag.tail:
					text+=tag.tail

				self.index_string(text, url, 10, title, description)
		except:
			pass # Unable to find a title


		# Loop over tags in content_tags and get text
		if not self.index_xpaths:
			report_error(1,'No search index xpath set')

		for content_tag in self.index_xpaths:
			for search_tag in self.content_tags:
				xpath=content_tag+"//"+search_tag

				try:
					result=tree.xpath(xpath)
					for tag in result:
						text=''
						if tag.text:
							text+=tag.text+' '
						if tag.tail:
							text+=tag.tail

						if text:
							if tag.tag=='h1':
								weight=7
							elif tag.tag=='h2':
								weight=6
							elif tag.tag=='h3':
								weight=5
							elif tag.tag=='h4':
								weight=4
							elif tag.tag=='h5':
								weight=3
							elif tag.tag=='h6':
								weight=2
							elif tag.tag=='strong' or tag.tag=='em' or tag.tag=='b' or tag.tag=='i':
								weight=1
							else:
								weight=0

							self.index_string(text, url, weight, title, description)
				except:
					pass # No results


class Hit:
	''' Weighted occurence of a term in file'''

	def __init__(self, term, url, weight, line, title, description):
		self.term=term
		self.url=url
		self.weight=weight
		self.line=line
		self.description=description.replace('"', '\"')
		self.description=description.replace('\n', ' ')
		self.title=title
