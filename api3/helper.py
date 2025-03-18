import faiss
import pickle
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from api2.models import Reel


def run_offline_pipeline():
    # Load all reels data
    reels = Reel.objects.all()
    print('======++++++++++++++++++++++++++++++++++++++++++++++++=========')
    df = pd.DataFrame(list(reels.values('id', 'property_type', 'location__location_name', 'area__area_name', 'tags')))

    # Combine features
    df['combined_features'] = df['location__location_name'] + " " + df['area__area_name'] + " " + df['property_type']

    # TF-IDF vectorizer
    vectorizer = TfidfVectorizer(max_features=5000)
    vectors = vectorizer.fit_transform(df['combined_features']).toarray().astype('float32')

    # Save vectorizer for later use
    with open('vectorizer.pkl', 'wb') as f:
        pickle.dump(vectorizer, f)

    # Create FAISS index
    index = faiss.IndexFlatL2(vectors.shape[1])
    index.add(vectors)

    # Save FAISS index
    faiss.write_index(index, 'reels_index.faiss')

    # Save reel_id to index mapping
    np.save('reel_ids.npy', df['id'].values)

    print("Offline pipeline completed: vectorizer, FAISS index, and reel IDs saved.")

if __name__ == '__main__':
    run_offline_pipeline()