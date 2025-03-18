import pandas as pd
import faiss
import numpy as np
import pickle
from sklearn.preprocessing import MinMaxScaler
from api2.models import User, Interaction, Reel


vectorizer = pickle.load(open('vectorizer.pkl', 'rb'))
faiss_index = faiss.read_index('reels_index.faiss')
reel_ids_mapping = np.load('reel_ids.npy')

def recommend_reels(user_id, top_n=30):
    user = User.objects.get(id=user_id)

    recent_liked = Interaction.objects.filter(user=user, liked=True).order_by('-watched_at')[:5]
    user_features = [f"{r.reel.location.location_name} {r.reel.area.area_name} {r.reel.property_type}" for r in recent_liked]
    user_profile = " ".join(user_features) + " " + user.preferred_property_type + " " + user.location.location_name
    print(user_profile)
    
    user_vector = vectorizer.transform([user_profile]).toarray().astype('float32')

    # FAISS ANN Search (fetch more than needed for post-filter)
    # D, I = faiss_index.search(user_vector, top_n * 10)  # over-fetch
    D, I = faiss_index.search(user_vector, len(reel_ids_mapping))  # over-fetch
    faiss_reel_ids = reel_ids_mapping[I[0]]
    
    # Fetch metadata from DB
    reels = Reel.objects.filter(id__in=faiss_reel_ids)
    df = pd.DataFrame(list(reels.values('id', 'likes', 'comments', 'shares', 'location__location_name', 'area__area_name', 'property_type', 'price')))

    if df.empty:
        return []

    df['priority'] = 0
    
    for liked in recent_liked:
        mask = (
            (df['location__location_name'] == liked.reel.location.location_name) &
            (df['area__area_name'] == liked.reel.area.area_name) &
            (df['property_type'] == liked.reel.property_type)
        )
        df.loc[mask, 'priority'] = 1
   
    mask = (
        (df['location__location_name'] == user.location.location_name) &
        (df['property_type'] == user.preferred_property_type)
    )
    # Only update where priority < 2 (avoid overriding liked-based priority)
    df.loc[mask & (df['priority'] < 2), 'priority'] = 1
       
    df['engagement'] = df['likes'] + df['comments'] * 2 + df['shares'] * 3
    df['engagement'] = df['engagement'].fillna(0)
    if df['engagement'].max() > 0:
        scaler = MinMaxScaler()
        df['trend_score'] = scaler.fit_transform(df[['engagement']])
    else:
        df['trend_score'] = 0

    # Step 7: Convert FAISS distance to similarity
    df['faiss_score'] = 1 - (D[0][:len(df)] / (D[0].max() + 1e-6))  
    if user.min_price_preference and user.max_price_preference:
        print('yes')
        user_min_price = float(user.min_price_preference)
        user_max_price = float(user.max_price_preference)

        df['price_score'] = df['price'].apply(
            lambda p: 1 if p >= user_min_price and p <= user_max_price else 0
        )
    else:
        df['price_score'] = 0

    # Step 8: Final score blending (priority + faiss + engagement)
    df['final_score'] = (
        0.6 * df['faiss_score'] + 
        0.2 * df['trend_score'] + 
        0.2 * df['priority'] 
    )
    # print(df.head(64))

    # Step 9: Sort by final score
    # df = df.sort_values(['priority', 'final_score'], ascending=[False, False]).head(top_n)
    df = df.sort_values(['priority', 'price_score','final_score'], ascending=[False, False, False]).head(len(reel_ids_mapping))
    print(df.head(20))
    return list(df['id'])
