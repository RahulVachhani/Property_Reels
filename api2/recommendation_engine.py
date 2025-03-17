import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .models import User, Reel, Interaction

def recommend_reels(user_id, top_n=30):
    user = User.objects.get(id=user_id)
    # watched_reels = Interaction.objects.filter(user=user).values_list('reel_id', flat=True)
    watched_reels = Interaction.objects.filter(user=user, liked = True)
    watched_reels_ids = []
    prioritized_property_types = []

    
    for i in watched_reels:
        print(i.user.username)
        print(i.reel.id)
        watched_reels_ids.append(i.reel.id)
        prioritized_property_types.append({
            'location__location_name': i.reel.location.location_name,
            'area__area_name': i.reel.area.area_name,
            'property_type': i.reel.property_type
        })

    reels = Reel.objects.exclude(id__in=watched_reels_ids[:10])

    df = pd.DataFrame(list(reels.values('id', 'property_type', 'location__location_name', 'area__area_name', 'tags', 'likes', 'comments', 'shares')))
    # print(df)

    if df.empty:
        return []
    
    df['priority'] = 0

    for condition in prioritized_property_types:
        mask = (
            (df['location__location_name'] == condition['location__location_name']) &
            (df['area__area_name'] == condition['area__area_name']) &
            (df['property_type'] == condition['property_type'])
        )
        df.loc[mask, 'priority'] = 1

    # df['combined_features'] = df['tags'] + " " + df['property_type'] + " " + df['location__location_name'] + " " + df['area__area_name']
    df['combined_features'] =  df['location__location_name'] + " " + df['area__area_name'] + " " + df['property_type'] 

      # Also combine the watched reels' content
    watched_reels_data = Reel.objects.filter(id__in=watched_reels_ids[-4:]).values('property_type', 'location__location_name','area__area_name', 'tags')
    # watched_features = ["{} {} {}".format(r['tags'], r['property_type'], r['location__location_name']) for r in watched_reels_data]
    watched_features = ["{} {} {}".format(r['location__location_name'], r['area__area_name'], r['property_type']) for r in watched_reels_data]


    if watched_features:
        print('============================== watched ==================================')
        # user_profile = " ".join(watched_features) + " " + user.preferred_property_type + " " + user.location.location_name
        user_profile = " ".join(watched_features) + " " + user.preferred_property_type + " " + user.location.location_name
        print(user_profile)
    else:
        user_profile = user.preferred_property_type + " " + user.location.location_name
      
    vectorizer = TfidfVectorizer()
    reel_vectors = vectorizer.fit_transform(df['combined_features'])
    user_vector = vectorizer.transform([user_profile])

    df['content_score'] = cosine_similarity(user_vector, reel_vectors).flatten()

    df['engagement'] = df['likes'] + df['comments'] * 2 + df['shares'] * 3
    df['trend_score'] = df['engagement'] / df['engagement'].max()

    df['final_score'] = 0.6 * df['content_score'] + 0.4 * df['trend_score'] 
    print(df.head(65))
     
    # top_reels = df.sort_values('final_score', ascending=False).head(top_n)
    top_reels = df.sort_values(['priority', 'final_score'], ascending=[False, False]).head(top_n)
    print(top_reels)
    print(list(top_reels['id']))
    return list(top_reels['id'])
