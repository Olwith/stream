import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

#set the title
st.title("Interactive data visualization app")
#File uploader to allow users to apload their files
uploaded_file = st.file_uploader("Upload your CSV file",type=["csv"])
if uploaded_file is not None:
    #Read the Uploaded file
    data = pd.read_csv(uploaded_file)

    #Display the data
    st.subheader("Raw Data")
    st.write(data.head())

    #Display Summary statistics
    st.subheader("Summary Statistics")
    st.write(data.describe())

    #Select column for Visualization
    column = st.selectbox("Select a column for visualization",data.columns)
    #Select type of plot
    plot_type = st.selectbox("Select the type of plot",["Histogram","Boxplot","Line Chart","Bar Chart"])

    #Plot the selected column based on selected plot type
    st.subheader(f"{plot_type} of {column}")

    if plot_type == "Histogram":
        fig,ax = plt.subplots()
        ax.hist(data[column], bins=30,edgecolor='k')
        st.pyplot(fig)
    elif plot_type == "Boxplot":
        fig,ax = plt.subplots()
        sns.boxplot(data[column],ax=ax)
        st.pyplot(fig)

    elif plot_type == "Line Chart":
        fig,ax=plt.subplots()
        ax.plot(data[column])
        st.pyplot(fig)

    elif plot_type == "Bar Chart":
        fig,ax=plt.subplots()
        ax.bar(data.index,data[column])
        st.pyplot(fig)

    #Correlation heatmap
    st.subheader("Correlation heatmap")
    fig,ax = plt.subplots()
    sns.heatmap(data.corr(),annot=True,cmap='coolwarm',ax=ax)
    st.pyplot(fig)

else:
    st.write("Please Upload a CSV file to get started")
