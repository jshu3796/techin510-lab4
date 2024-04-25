import streamlit as st
import psycopg2
import pandas as pd
import os

# Function to connect to the database
def connect_db():
    return psycopg2.connect(os.getenv('DATABASE_URL'))

# Function to get books based on filters
def get_books(query_params):
    conn = connect_db()
    title_filter = query_params['title_filter']
    description_filter = query_params['description_filter']
    order_by = query_params['order_by']
    order_direction = 'ASC' if query_params['order_direction'] == 'Low to High' else 'DESC'
    
    # Start building the query
    query_parts = ["SELECT title, price, description, rating FROM books"]
    conditions = []
    params = []
    
    if title_filter:
        conditions.append("title ILIKE %s")
        params.append('%' + title_filter + '%')
    
    if description_filter:
        conditions.append("description ILIKE %s")
        params.append('%' + description_filter + '%')
    
    if conditions:
        query_parts.append("WHERE " + " AND ".join(conditions))
    
    query_parts.append(f"ORDER BY {order_by} {order_direction}")
    
    query = " ".join(query_parts)
    df = pd.read_sql(query, conn, params=params)
    conn.close()
    return df

# Streamlit interface
st.title('Book Search and Filter App')

# Inputs for the search criteria
title_filter = st.text_input('Search by Book Name')
description_filter = st.text_input('Search by Description')
order_by = st.selectbox('Order by', ['price', 'rating'])
order_direction = st.selectbox('Order Direction', ['Low to High', 'High to Low'])

# Button to trigger the search
if st.button('Search Books'):
    query_params = {
        'title_filter': title_filter,
        'description_filter': description_filter,
        'order_by': order_by,
        'order_direction': order_direction
    }
    books_df = get_books(query_params)
    if not books_df.empty:
        st.write(books_df)
    else:
        st.write("No books found with the given search criteria.")
