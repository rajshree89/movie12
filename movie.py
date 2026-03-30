import pandas as pd
import numpy as np
import ast

# ==============================
# 1. LOAD DATA & SANITY CHECK
# ==============================

df = pd.read_csv(r"C:\Users\DELL\AppData\Local\Packages\5319275A.WhatsAppDesktop_cv1g1gvanyjgm\LocalState\sessions\1FAB2E689BC7168A5574D524DE8AD84847FAE215\transfers\2026-07\movie1.csv")

print("First 5 rows:")
print(df.head())

print("\nDataset Info:")
print(df.info())

print("\nMissing Values:")
print(df.isnull().sum())

# Remove duplicates
df = df.drop_duplicates()

# Convert numeric columns
df['budget'] = pd.to_numeric(df['budget'], errors='coerce')
df['revenue'] = pd.to_numeric(df['revenue'], errors='coerce')

# Remove invalid values
df = df[(df['budget'] > 0) & (df['revenue'] > 0)]

# Create Profit & ROI
df['profit'] = df['revenue'] - df['budget']
df['ROI'] = df['profit'] / df['budget']

# ==============================
# 2. Q1: HIGHEST PROFIT MOVIE
# ==============================

print("\n=== Q1: Highest Profit Movie ===")

max_profit_movie = df.loc[df['profit'].idxmax()]

print("Movie:", max_profit_movie['title'])
print("Profit:", max_profit_movie['profit'])

# ==============================
# 3. Q2: LANGUAGE WITH HIGHEST ROI
# ==============================

print("\n=== Q2: Highest Avg ROI by Language ===")

roi_by_lang = df.groupby('original_language')['ROI'].mean().sort_values(ascending=False)

print(roi_by_lang)
print("\nTop Language:", roi_by_lang.idxmax())

# ==============================
# 4. Q3: UNIQUE GENRES (JSON FIX)
# ==============================

print("\n=== Q3: Unique Genres ===")

def extract_genres(x):
    try:
        genres = ast.literal_eval(x)
        return [i['name'] for i in genres]
    except:
        return []

df['genres_list'] = df['genres'].apply(extract_genres)

unique_genres = set(g for sublist in df['genres_list'] for g in sublist)

print(unique_genres)

# ==============================
# 5. EXTRACT DIRECTOR & PRODUCER
# ==============================

def get_person(crew_data, job):
    try:
        crew_list = ast.literal_eval(crew_data)
        for person in crew_list:
            if person.get('job') == job:
                return person.get('name')
    except:
        return None

df['director'] = df['crew'].apply(lambda x: get_person(x, 'Director'))
df['producer'] = df['crew'].apply(lambda x: get_person(x, 'Producer'))

# ==============================
# 6. Q4: PRODUCERS & DIRECTORS
# ==============================

print("\n=== Q4: Producers & Directors Table ===")

prod_dir_table = df[['title', 'producer', 'director']]
print(prod_dir_table.head())

producer_roi = df.groupby('producer')['ROI'].mean().sort_values(ascending=False)

print("\nTop 3 Producers by ROI:")
print(producer_roi.head(3))

# ==============================
# 7. Q5: ACTOR WITH MOST MOVIES
# ==============================

print("\n=== Q5: Actor with Most Movies ===")

def extract_cast(x):
    try:
        cast = ast.literal_eval(x)
        return [i['name'] for i in cast]
    except:
        return []

df['cast_list'] = df['cast'].apply(extract_cast)

actors_df = df.explode('cast_list')

actor_counts = actors_df['cast_list'].value_counts()

top_actor = actor_counts.idxmax()

print("Top Actor:", top_actor)
print("Number of Movies:", actor_counts.max())

# Deep dive
actor_data = actors_df[actors_df['cast_list'] == top_actor]

print("\nMovies of Top Actor:")
print(actor_data[['title', 'genres_list', 'profit']])

# ==============================
# 8. Q6: TOP 3 DIRECTORS & ACTORS
# ==============================

print("\n=== Q6: Directors & Preferred Actors ===")

top_directors = df['director'].value_counts().head(3).index

for director in top_directors:
    print("\nDirector:", director)
    
    director_movies = df[df['director'] == director]
    
    temp = director_movies.explode('cast_list')
    
    top_actors = temp['cast_list'].value_counts().head(3)
    
    print("Preferred Actors:")
    print(top_actors)