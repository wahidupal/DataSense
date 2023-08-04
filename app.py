import streamlit as st
import plotly_express as px
import pandas as pd
import io
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt
# from pandas_profiling import ProfileReport 
# from streamlit_pandas_profiling import st_profile_report

# configuration
st.set_option('deprecation.showfileUploaderEncoding', False)

# title of the app
st.title("Data Analyzer")

# Add a sidebar
st.sidebar.subheader("Visualization Settings")

# Setup file upload
uploaded_file = st.sidebar.file_uploader(
                        label="Upload your CSV or Excel file. (200MB max)",
                         type=['csv', 'xlsx'])

global df
if uploaded_file is not None:
    print(uploaded_file)
    #print("hello")

    try:
        df = pd.read_csv(uploaded_file)
    except Exception as e:
        print(e)
        df = pd.read_excel(uploaded_file)

global numeric_columns
global non_numeric_columns
try:

    # add check box to sidebar
    check_box = st.sidebar.checkbox(label="Display dataset")

    if check_box:
    # lets show the dataset
        st.write(df)
    # Sidebar Select Box
    select = st.sidebar.selectbox('Tools', ['Info about datasets', 'Describe data',  'Find Missing value', 'Correlation' ])
    
    numeric_columns = list(df.select_dtypes(['float', 'int']).columns)
    non_numeric_columns = list(df.select_dtypes(['object']).columns)
    non_numeric_columns.append(None)
    print(non_numeric_columns)
    # column filter data 
    filtered = st.multiselect("Filter columns", options=list(df.columns), default=list(df.columns))
    st.write(df[filtered])


     # Data Information
    if select == "Info about datasets":  
            buffer = io.StringIO()
            df.info(buf=buffer)
            s = buffer.getvalue()
            st.text(s)
    
    elif select=='Describe data':
        
        buffer = io.StringIO()
        s= df.describe()
        st.table(s)

    elif select== 'Find Missing value':
        buffer = io.StringIO()
        s= df.isnull().sum()
        st.table(s)

    elif select == 'Correlation':
        fig, ax = plt.subplots(figsize=(10,10))
        sns.heatmap(df.corr(), annot=True, ax=ax, cmap='coolwarm')
        st.pyplot(fig)


#graph
   
    chart_select= st.sidebar.selectbox(
                    label='Select the chart type',
                     options=['Scatterplots','Lineplot','Histogram','Boxplot','Barchart'])
    

    if chart_select == 'Scatterplots':
        st.sidebar.subheader("Scatterplot Settings")
        x_values = st.sidebar.selectbox('X axis', options= df.columns)
        y_values = st.sidebar.selectbox('Y axis', options= df.columns)
        plot = px.scatter(data_frame=df, x=x_values, y=y_values)
        #Display the chart
        st.plotly_chart(plot)


    elif chart_select == 'Lineplot':
        st.sidebar.subheader("Line Plot Settings")
        x_values = st.sidebar.selectbox('X axis', options=df.columns)
        y_values = st.sidebar.selectbox('Y axis', options=df.columns)
        plot = px.line(data_frame=df, x=x_values, y=y_values)
        st.plotly_chart(plot)
    


    elif chart_select == 'Boxplot':
        st.sidebar.subheader("Boxplot Settings")
        x = st.sidebar.selectbox("X axis", options=df.columns)
        y = st.sidebar.selectbox("Y axis", options=df.columns)
        #color_value = st.sidebar.selectbox("Color", options=non_numeric_columns)
        plot = px.box(data_frame=df, x=x, y=y)
        st.plotly_chart(plot)

    elif chart_select == 'Barchart':
        st.sidebar.subheader("Barchart Settings")
        x = st.sidebar.selectbox("X axis", options=df.columns)
        y = st.sidebar.selectbox("Y axis", options=df.columns)
        plot = px.bar(data_frame=df, x=x, y=y)
        st.plotly_chart(plot)

    

    elif chart_select == 'Histogram':
        st.sidebar.subheader("Histogram Settings")
        x = st.sidebar.selectbox('Feature', options=df.columns)
        bin_size = st.sidebar.slider("Number of Bins", min_value=10,
                                     max_value=100, value=40)
        #color_value = st.sidebar.selectbox("Color", options=non_numeric_columns)
        plot = px.histogram(x=x, data_frame=df)
        st.plotly_chart(plot)







except Exception as e:
    print(e)
    st.write("Please upload file to the application.")


# st.sidebar.title("Analyzing Option")
# st.sidebar.subheader("Analyze")
# feature_selection = st.sidebar.multiselect(label="Setting",
#                                            options=numeric_cols)

# stock_dropdown = st.sidebar.selectbox(label="Stock Ticker",
#                                       options=unique_stocks)