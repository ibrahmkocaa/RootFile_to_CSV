import streamlit as st
import pandas as pd 
import matplotlib.pyplot as plt 
import seaborn as sns
import uproot 
import awkward as ak
from io import BytesIO

st.title("ROOT to CSV Converter with Histogram Plotter")

# Dosya yükleme
uploaded_file = st.file_uploader("Upload a ROOT file", type=["root"])

if uploaded_file is not None:
    # ROOT dosyasını açma
    file = uproot.open(uploaded_file)
    keys = file.keys()
    
    # "Ntuples;1" anahtarını filtreleme
    filtered_keys = [key for key in keys if key != 'Ntuples;1']
    
    st.write("Available keys in the ROOT file:")
    st.write(filtered_keys)
    
    # Kullanıcıya Ntuple seçimi için seçenekler sunma
    ntuple_key = st.selectbox("Select the Ntuple to convert", filtered_keys)
    
    # DataFrame'e çevirme ve gösterme
    if ntuple_key:
        try:
            # Data'yı awkward array olarak yükle
            array = file[ntuple_key].arrays(library="ak")
            
            # Akward array'i pandas DataFrame'e çevir
            df = ak.to_dataframe(array)
            
            # DataFrame'i Streamlit'te gösterme
            st.write(f"DataFrame Head for {ntuple_key}:")
            st.dataframe(df.head())  # Burada st.write yerine st.dataframe kullanıyoruz
            
            # DataFrame boyutunu yazdırma
            st.write(f"DataFrame shape: {df.shape}")
            
            # CSV'ye kaydetme
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download as CSV",
                data=csv,
                file_name=f'{ntuple_key}.csv',
                mime='text/csv',
            )
                
            # Kullanıcıya sütun seçimi için seçenekler sunma
            column = st.selectbox("Select a column to plot histogram", df.columns)
            
            if column:
                # Kullanıcıdan bins değerini alma
                bins = st.slider("Select number of bins for the histogram", min_value=1, max_value=100, value=30)
                
                # Histogram grafiği çizme
                st.write(f"Histogram of {column} with {bins} bins:")
                fig, ax = plt.subplots()
                sns.histplot(df[column], bins=bins, kde=True, ax=ax)
                st.pyplot(fig)
                
                # Grafik indirilebilir hale getirme
                buf = BytesIO()
                fig.savefig(buf, format="png" , dpi=300)
                buf.seek(0)
                
                st.download_button(
                    label="Download Histogram as PNG",
                    data=buf,
                    file_name=f'{column}_histogram.png',
                    mime='image/png',
                )
            
        except Exception as e:
            st.error(f"An error occurred: {e}")
