#server_queries.py
queries = {
	#______________
	#вспомогательные
	'help_count_out_props': 
	{
		'query': '''
			SELECT (COUNT(?wd) AS ?countOut){{
		 	  VALUES (?company) {{(wd:{qid})}}
		      ?company ?p ?statement .
		      ?statement ?ps ?ps_ .
		      ?wd wikibase:claim ?p.
		      ?wd wikibase:statementProperty ?ps.
		    }} 
			'''
	},
	'help_count_in_props':
	{
		'query': '''
			SELECT  (COUNT(?obj) AS ?countIn) 
			WHERE {{
			  VALUES (?book) {{(wd:{qid})}}.
			  ?obj ?prop_id ?book.
			  ?wd wikibase:directClaim ?prop_id.
			  ?wd rdfs:label ?prop_label.
			  FILTER((LANG(?prop_label)) = "ru").
			}}
			'''
	},	
	'help_count_books':
	{
		'query': '''
			SELECT (COUNT(?book) AS ?cBooks) WHERE {{
			  ?book wdt:P50 wd:{author_id}
			}}
			'''
	},	
	#___________
	'book_author' : 
	{
		'query':'''
			SELECT ?authorLabel ?test
			WHERE{{
				wd:{book_name} wdt:P50 ?author.
				SERVICE wikibase:label {{ bd:serviceParam wikibase:language "ru,en". }}
			}}
			''',
		'params': {'book_name': 'book'}
	},	

	'book_written' : 
	{
		'query':'''
			SELECT (YEAR(?year) as ?years)
			WHERE
			{{
				wd:{book_name} wdt:P571 ?year.
				SERVICE wikibase:label {{ bd:serviceParam wikibase:language "ru,en"}}.
			}}
			''',
		'params': {'book_name': 'book'}
	},

	'book_published' : 
	{
		'query':'''
			SELECT (YEAR(?year) as ?years)
			WHERE
			{{
				wd:{book_name} wdt:P577 ?year.
				SERVICE wikibase:label {{ bd:serviceParam wikibase:language "ru,en"}}.
			}}
			''',
		'params': {'book_name': 'book'}
	},

	'book_characters' : 
	{
		'query':'''
			SELECT ?charsLabel
			WHERE
			{{
				wd:{book_name} wdt:P674 ?chars
				SERVICE wikibase:label {{ bd:serviceParam wikibase:language "ru,en". }}
			}}
			''',
		'params': {'book_name': 'book'}
	},	

	'book_genre' : 
	{
		'query':'''
			SELECT ?genreLabel
			WHERE
			{{
				wd:{book_name} wdt:P136 ?genre
				SERVICE wikibase:label {{ bd:serviceParam wikibase:language "ru,en". }}
			}}
			''',
		'params': {'book_name': 'book'}
	},
	'book_main_theme' : 
	{
		'query':'''
			SELECT ?subjLabel  
			WHERE  
			{{   
			  wd:{book_name} wdt:P921 ?subj;  	   
			  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "ru,en". }}  
			}}  
			''',
		'params': {'book_name': 'book'}
	},

	'author_birthplace' : 
	{
		'query':'''
			SELECT ?placeLabel
			WHERE
			{{
			  wd:{author_name} wdt:P19 ?place
			  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "ru,en". }}
			}}
			''',
		'params': {'author_name': 'author'}
	},	
	'author_productions' : 
	{
		'query':'''
			SELECT ?titleLabel
			WHERE
			{{
			  wd:{author_name} wdt:P800 ?title
			  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "ru,en". }}
			}}
			''',
		'params': {'author_name': 'author'}
	},		
	'author_genres' : 
	{
		'query':'''
			SELECT ?genreLabel
			WHERE
			{{
			  wd:{author_name} wdt:P136 ?genre
			  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "ru,en". }}
			}}
			''',
		'params': {'author_name': 'author'}
	},
	'author_when_born' : 
	{
		'query':'''
			SELECT ?DATE ?dateLabel
			WHERE
			{{
			  wd:{author_name} wdt:P569 ?DATE
			  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "ru,en". }}
			}}
			''',
		'params': {'author_name': 'author'}
	},
	'author_where_lived' : 
	{
		'query':'''
			SELECT ?placeLabel
			WHERE
			{{
				wd:{author_name} wdt:P551 ?place
				SERVICE wikibase:label {{ bd:serviceParam wikibase:language "ru,en". }}
			}}
			''',
		'params': {'author_name': 'author'}
	},	
	'author_languages' : 
	{
		'query':'''
			SELECT ?langLabel
			WHERE
			{{
			  wd:{author_name} wdt:P1412 ?lang
			  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "ru,en". }}
			}}
			''',
		'params': {'author_name': 'author'}
	},		
	'author_when_died' : 
	{
		'query':'''
			SELECT ?date ?dateLabel
			WHERE
			{{
			  wd:{author_name} wdt:P570 ?date
			  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "ru,en". }}
			}}
			''',
		'params': {'author_name': 'author'}
	},		
	'author_where_died' : 
	{
		'query':'''
			SELECT ?placeLabel
			WHERE
			{{
			  wd:{author_name} wdt:P20 ?place
			  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "ru,en". }}
			}}
			''',
		'params': {'author_name': 'author'}
	},	
	'author_where_buried' : 
	{
		'query':'''
			SELECT ?placeLabel
			WHERE
			{{
			  wd:{author_name} wdt:P119 ?place
			  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "ru,en". }}
			}}
			''',
		'params': {'author_name': 'author'}
	},		
	'author_inspired_by' : 
	{
		'query':'''
			SELECT ?nameLabel
			WHERE
			{{
			  wd:{author_name} wdt:P737 ?name
			  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "ru,en". }}
			}}
			''',
		'params': {'author_name': 'author'}
	},	
}