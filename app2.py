## with prompt

import streamlit as st
from pathlib import Path
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_community.utilities import SQLDatabase
from langchain.agents.agent_types import AgentType
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler
from sqlalchemy import create_engine
import sqlite3, os
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate


groq_api_key = os.getenv("GROQ_API_KEY")

st.set_page_config(page_title="Langchain: chat with SQLDB")
st.title("LangChain: Chat with SQL DB")

LOCALDB = "USE_LOCALDB"
MYSQL = "USE_MYSQL"

radio_opt = ["Use SQLlite3 Database - Student.db", "Connect to your SQL Database"]
selected_opt = st.sidebar.radio(label="Choose the SQLDB from whch you want tp extract data", options=radio_opt)

if radio_opt.index(selected_opt)==1:
    db_uri = MYSQL
    mysql_host = st.sidebar.text_input("Provide Host Address")
    mysql_user = st.sidebar.text_input("MySQL Username")
    mysql_password = st.sidebar.text_input("MySQL Password", type="password")
    mysql_db = st.sidebar.text_input("MySQL Database")
else:
    db_uri = LOCALDB

if not db_uri:
    st.info("Please enter the database information and uri")

## Create LLM Model
LLM = ChatGroq(model="Llama3-8b-8192", streaming=True)

@st.cache_resource(ttl="2h")
def configure_db(db_uri, mysql_host=None, mysql_user=None, mysql_password=None, mysql_db=None):
    if db_uri==LOCALDB:
        dbfilepath = (Path(__file__).parent/"student.db")
        # print(f"dbfilepath:{dbfilepath}")
        creator = lambda: sqlite3.connect(f"file:{dbfilepath}?model=ro", uri=True)
        return SQLDatabase(create_engine("sqlite:///", creator=creator))
    elif db_uri == MYSQL:
        if not (mysql_host and mysql_user and mysql_password and mysql_db):
            st.error("Please provide all MySQL connection")
            st.stop()
        return SQLDatabase(create_engine(f"mysql+mysqlconnector://{mysql_user}:{mysql_password}@{mysql_host}/{mysql_db}"))

if db_uri == MYSQL:
    db = configure_db(db_uri, mysql_host, mysql_user, mysql_password, mysql_db)
else:
    db = configure_db(db_uri)

# toolkit
toolkit = SQLDatabaseToolkit(db=db, llm=LLM)


prompt_template = PromptTemplate(
    input_variables=["query"],
    template="""
    You are a knowledgeable assistant with access to a database. Your task is to respond to the following query in a way that avoids any sensitive or confidential information. If the query involves sensitive data, ask the user for clarification instead of declining outright.

    Query: {query}
    """
)

agent = create_sql_agent(
    llm=LLM,
    toolkit=toolkit,
    verbose=False,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    handle_parsing_errors=True
)


if "messages" not in st.session_state or st.sidebar.button("Clear message History"):
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

user_query = st.chat_input(placeholder="Ask anything from the database")


formatted_prompt = prompt_template.format(query=user_query)
if user_query:
    
    st.session_state.messages.append({"role": "user", "content": user_query})
    st.chat_message("user").write(user_query)

    # Create the prompt with the user's query
    formatted_prompt = prompt_template.format(query=user_query)

    with st.chat_message("assistant"):
        response = agent.run(formatted_prompt)  # Use the formatted prompt here
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.write(response)
