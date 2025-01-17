import csv
import json
import codecs

movie_csv_filename='tmdb_5000_movies.csv'
credits_csv_filename='tmdb_5000_credits.csv'

# tmdb_5000_movies.csv
genres_col='genres'
movie_id_col='id'
keyword_col='keywords'
company_col='production_companies'
country_col='production_countries'
lang_col='spoken_languages'

# tmdb_5000_credits.csv
cast_col='cast' 
movie_id_col2='movie_id'

# codecs
csv_codecs='cp1252'
utf8_codec='utf-8'

class TmdbCsvBreaker:
    def __init__(self):
        self.json_decoder = json.JSONDecoder()

        # for genres breakdown
        self.movie_genres_table = dict() # key: movie_id, val: [genre_id]
        self.genres_table = dict() # key: genre_id, val: genre_name

        # for keyword breakdown
        self.movie_keywords_table = dict() # key: movie_id, val: [keyword_id]
        self.keywords_table = dict() # key: keyword_id, val: keyword_name

        # for production_company
        self.movie_company_table = dict() # {movie_id: [company_id]}
        self.company_table = dict() # {company_id: name}

        # for production_country
        self.movie_country_table = dict() # {movie_id: [country_id]}
        self.country_table = dict() # {country_id: country_name}

        # for spoken language
        self.movie_lang_table = dict() # {movie_id: [lang_id]}
        self.lang_table = dict() # {lang_id: lang_name}

        # for movie actor
        self.movie_actor_table = dict()
        self.actor_table = dict()

        self.movie_ids = set()

    def breakdown(self):
        self.breakdown_movie_csv()
        self.breakdown_credit_csv()
    
    def breakdown_credit_csv(self):
        with codecs.open(credits_csv_filename, encoding=utf8_codec, errors='replpace') as csvfile:
            reader = csv.DictReader(csvfile)
            line_no = 0
            for row in reader:
                cast_json_str = row[cast_col]
                cast_json_objs = self.json_decoder.decode(cast_json_str)
                idStr = row[movie_id_col2]
                movie_id = int(idStr.strip())
                if movie_id not in self.movie_ids:
                    continue
                else:
                    line_no += 1
                # self.movie_actor_table[movie_id] = cast_json_objs
                self.movie_actor_table[movie_id] = []
                _i = 0
                while len(self.movie_actor_table[movie_id]) < 11:
                    if _i >= len(cast_json_objs):
                        break
                    self.movie_actor_table[movie_id].append(cast_json_objs[_i])
                    for obj in cast_json_objs:
                        self.process_cast(obj)
                    _i += 1
            print('{0}, total lines parsed: {1}'.format(credits_csv_filename, line_no))
        self.save_movie_actor_csv()
        self.save_actor_csv()

    def process_cast(self, cast_json):
        '''
        actor_id, name, gender
        '''
        actor_id = cast_json['id']
        actor_name = cast_json['name']
        actor_gender = cast_json['gender']
        if actor_id in self.actor_table.keys() and actor_name != self.actor_table[actor_id][0]:
            print('WARNING actor_id={0} has multiple name'.format(actor_id))
        self.actor_table[actor_id] = (actor_name, actor_gender)

    def save_movie_actor_csv(self):
        movie_actor_filename = 'movie_cast.csv'
        movie_actor_fields = ['movie_id', 'actor_id', 'cast_id', 'char_name', 'char_gender', 'order']
        with codecs.open(movie_actor_filename, mode='w',encoding=utf8_codec, errors ='replace') as movie_actor_csv:
            writer = csv.DictWriter(movie_actor_csv, fieldnames=movie_actor_fields)
            writer.writeheader()
            for key, value in self.movie_actor_table.items():
                for cast_obj in value:
                    row = dict()
                    row['movie_id'] = key
                    row['actor_id'] = cast_obj['id']
                    row['cast_id'] = cast_obj['cast_id']
                    row['char_name'] = cast_obj['character']
                    row['char_gender'] = cast_obj['gender']
                    row['order'] = cast_obj['order']
                    writer.writerow(row)
        print('{0} is written'.format(movie_actor_filename))

    def save_actor_csv(self):
        actor_filename = 'actors.csv'
        actor_fields = ['actor_id', 'actor_name']
        with codecs.open(actor_filename, mode='w',encoding=utf8_codec, errors ='replace') as actor_csv:
            writer = csv.DictWriter(actor_csv, fieldnames=actor_fields)
            writer.writeheader()
            for key, value in self.actor_table.items():
                row = dict()
                row[actor_fields[0]] = key
                row[actor_fields[1]] = value[0]
                writer.writerow(row)
        print('{0} is written'.format(actor_filename))

    def breakdown_movie_csv(self):
        with codecs.open(movie_csv_filename, encoding=utf8_codec, errors ='replace') as csvfile:
            reader = csv.DictReader(csvfile)
            #print("field names: {0}".format(reader.fieldnames))
            line_no = 0
            for row in reader:
                idStr = row[movie_id_col]
                movie_id = int(idStr.strip())
                if len(self.movie_ids) >= 1200:
                    break
                else:
                    line_no += 1
                self.parse_genres(movie_id, row)
                self.parse_keywords(movie_id, row)
                self.parse_company(movie_id, row)
                self.parse_country(movie_id, row)
                self.parse_lang(movie_id, row)
                self.movie_ids.add(movie_id)
            print('{0}, total lines parsed: {1}'.format(movie_csv_filename, line_no))
        self.save_genres_csv()
        self.save_keywords_csv()
        self.save_company_csv()
        self.save_country_csv()
        self.save_lang_csv()

    def parse_genres(self, movie_id, row):
        self.movie_genres_table[movie_id]=[]
        jsonObjStr = row[genres_col]
        genres_objs = self.json_decoder.decode(jsonObjStr)
        for obj in genres_objs:
            #print(obj)
            genres_id = obj['id']
            genres_name = obj['name']
            self.movie_genres_table[movie_id].append(genres_id)
            if genres_id in self.genres_table.keys() and self.genres_table[genres_id] != genres_name:
                print('WARNING genre_id={0} has multiple names'.format(genres_id))
            self.genres_table[genres_id] = genres_name

    def save_genres_csv(self):
        movie_genres_filename = 'movie_genres.csv'
        movie_genres_fields = ['movie_id', 'genre_id']
        with codecs.open(movie_genres_filename, mode='w',encoding=utf8_codec, errors ='replace') as movie_genres_csv:
            writer = csv.DictWriter(movie_genres_csv, fieldnames=movie_genres_fields)
            writer.writeheader()
            for key, value in self.movie_genres_table.items():
                for genres_id in value:
                    row = dict()
                    row[movie_genres_fields[0]] = key
                    row[movie_genres_fields[1]] = genres_id
                    writer.writerow(row)
        print('{0} is written'.format(movie_genres_filename))
        genres_name_filename = 'genres_name.csv'
        genres_name_fields = ['genre_id', 'genre_name']
        with codecs.open(genres_name_filename, mode='w',encoding=utf8_codec, errors ='replace') as genres_name_csv:
            writer = csv.DictWriter(genres_name_csv, fieldnames=genres_name_fields)
            writer.writeheader()
            for key, value in self.genres_table.items():
                row = dict()
                row[genres_name_fields[0]] = key
                row[genres_name_fields[1]] = value
                writer.writerow(row)
        print('{0} is written'.format(genres_name_filename))

    def parse_keywords(self, movie_id, row):
        self.movie_keywords_table[movie_id] = []
        jsonStr = row[keyword_col]
        keywordObjs = self.json_decoder.decode(jsonStr)
        for obj in keywordObjs:
            kw_id = obj['id']
            kw_name = obj['name']
            self.movie_keywords_table[movie_id].append(kw_id)
            if kw_id in self.keywords_table.keys() and self.keywords_table[kw_id] != kw_name:
                print('WARNING keyword_id={0} has multiple names'.format(kw_id))
            self.keywords_table[kw_id] = kw_name

    def save_keywords_csv(self):
        movie_keyword_filename = 'movie_keywords.csv'
        keyword_fields = ['movie_id', 'keyword_id']
        with codecs.open(movie_keyword_filename, mode='w',encoding=utf8_codec, errors ='replace') as movie_keywords_csv:
            writer = csv.DictWriter(movie_keywords_csv, fieldnames=keyword_fields)
            writer.writeheader()
            for key, value in self.movie_keywords_table.items():
                for kw_id in value:
                    row = dict()
                    row[keyword_fields[0]] = key
                    row[keyword_fields[1]] = kw_id
                    writer.writerow(row)
        print('{0} is written'.format(movie_keyword_filename))
        keyword_name_filename = 'keyword_name.csv'
        keyword_name_fields = ['keyword_id', 'keyword_name']
        with codecs.open(keyword_name_filename, mode='w',encoding=utf8_codec, errors ='replace') as keyword_name_csv:
            writer = csv.DictWriter(keyword_name_csv, fieldnames=keyword_name_fields)
            writer.writeheader()
            for key, value in self.keywords_table.items():
                row = dict()
                row[keyword_name_fields[0]] = key
                row[keyword_name_fields[1]] = value
                writer.writerow(row)
        print('{0} is written'.format(keyword_name_filename))
    
    def parse_company(self, movie_id, row):
        self.movie_company_table[movie_id] = []
        jsonStr = row[company_col]
        companyObjs = self.json_decoder.decode(jsonStr)
        for obj in companyObjs:
            comp_id = obj['id']
            comp_name = obj['name']
            self.movie_company_table[movie_id].append(comp_id)
            if comp_id in self.company_table.keys() and self.company_table[comp_id] != comp_name:
                print('WARNING comp_id={0} has multiple names'.format(comp_id))
            self.company_table[comp_id] = comp_name

    def save_company_csv(self):
        company_csv_filename='movie_company.csv'
        company_fields = ['movie_id', 'production_id']
        with codecs.open(company_csv_filename, mode='w',encoding=utf8_codec, errors ='replace') as movie_company_csv:
            writer = csv.DictWriter(movie_company_csv, fieldnames=company_fields)
            writer.writeheader()
            for key, value in self.movie_company_table.items():
                for comp_id in value:
                    row = dict()
                    row[company_fields[0]] = key
                    row[company_fields[1]] = comp_id
                    writer.writerow(row)
        print('{0} is written'.format(company_csv_filename))
        company_name_filename = 'company_name.csv'
        company_name_fields = ['production_id', 'production_name']
        with codecs.open(company_name_filename, mode='w',encoding=utf8_codec, errors ='replace') as company_name_csv:
            writer = csv.DictWriter(company_name_csv, fieldnames=company_name_fields)
            writer.writeheader()
            for key, value in self.company_table.items():
                row = dict()
                row[company_name_fields[0]] = key
                row[company_name_fields[1]] = value
                writer.writerow(row)
        print('{0} is written'.format(company_name_filename))

    def parse_country(self, movie_id, row):
        self.movie_country_table[movie_id] = []
        jsonStr = row[country_col]
        countryObjs = self.json_decoder.decode(jsonStr)
        for obj in countryObjs:
            country_id = obj['iso_3166_1']
            country_name = obj['name']
            self.movie_country_table[movie_id].append(country_id)
            if country_id in self.country_table.keys() and self.country_table[country_id] != country_name:
                print('WARNING country_id={0} has multiple names'.format(country_id))
            self.country_table[country_id] = country_name

    def save_country_csv(self):
        country_csv_filename = 'movie_country.csv'
        country_fields = ['movie_id', 'production_country_id']
        with codecs.open(country_csv_filename, mode='w',encoding=utf8_codec, errors ='replace') as movie_country_csv:
            writer = csv.DictWriter(movie_country_csv, fieldnames=country_fields)
            writer.writeheader()
            for key, value in self.movie_country_table.items():
                for country_id in value:
                    row = dict()
                    row[country_fields[0]] = key
                    row[country_fields[1]] = country_id
                    writer.writerow(row)
        print('{0} is written'.format(country_csv_filename))
        country_name_filename = 'country_name.csv'
        country_name_fields = ['production_country_id', 'production_country_name']
        with codecs.open(country_name_filename, mode='w',encoding=utf8_codec, errors ='replace') as country_name_csv:
            writer = csv.DictWriter(country_name_csv, fieldnames=country_name_fields)
            writer.writeheader()
            for key, value in self.country_table.items():
                row = dict()
                row[country_name_fields[0]] = key
                row[country_name_fields[1]] = value
                writer.writerow(row)
        print('{0} is written'.format(country_name_filename))

    def parse_lang(self, movie_id, row):
        self.movie_lang_table[movie_id] = []
        jsonStr = row[lang_col]
        langObjs = self.json_decoder.decode(jsonStr)
        for obj in langObjs:
            lang_id = obj['iso_639_1']
            lang_name = obj['name']
            self.movie_lang_table[movie_id].append(lang_id)
            if lang_id in self.lang_table.keys() and self.lang_table[lang_id] != lang_name:
                print('WARNING lang_id={0} has multiple names'.format(lang_id))
            self.lang_table[lang_id] = lang_name

    def save_lang_csv(self):
        lang_csv_filename = 'movie_lang.csv'
        lang_fields = ['movie_id', 'language_id']
        with codecs.open(lang_csv_filename, mode='w', encoding=utf8_codec, errors ='replace') as movie_lang_csv:
            writer = csv.DictWriter(movie_lang_csv, fieldnames=lang_fields)
            writer.writeheader()
            for key, value in self.movie_lang_table.items():
                for lang_id in value:
                    row = dict()
                    row[lang_fields[0]] = key
                    row[lang_fields[1]] = lang_id
                    writer.writerow(row)
            print('{0} is written'.format(lang_csv_filename))
        lang_name_filename = 'lang_name.csv'
        lang_name_fields = ['language_id', 'language_name']
        with codecs.open(lang_name_filename, mode='w',encoding=utf8_codec, errors ='replace') as lang_name_csv:
            writer = csv.DictWriter(lang_name_csv, fieldnames=lang_name_fields)
            writer.writeheader()
            for key, value in self.lang_table.items():
                row = dict()
                row[lang_name_fields[0]] = key
                row[lang_name_fields[1]] = value
                writer.writerow(row)
        print('{0} is written'.format(lang_name_filename))

if __name__ == '__main__':
    tmdb_csv_breaker = TmdbCsvBreaker()
    tmdb_csv_breaker.breakdown()