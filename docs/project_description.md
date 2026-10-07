## Project - Flight Punctuality Analytics

### 1. Purpose
The project aims to implement the modern data stack to solve a real-world problem. The focus of the
project is to build the modern data stack according to the business requirements independently as a
team of data engineers.

### 2. Scenario
Suppose your group work as the data engineering team for the hypothetical airport authority in Sweden.
In the coming sprint of two weeks, your team is asked to produce a proof of concept (PoC) for a modern
data stack that assists the analysis of flight punctuality. Your team have already met the business
stakeholders and below are the business requirements that you have got:

### 3. Business requirements
You should first work with the mandatory requirements and then with the additional ones.

**Mandatory requirements**
- build a modern data stack with dlt, dbt core, Snowflake, streamlit and dagsters, which
means that your data pipeline involves data loading, data transformation, cloud data warehouse, BI
visualization and orchestration
- the primary interest of the business stakeholders is to analyse the numbers of delayed arrivals at
and departures from Swedish airports. They would also like to analyse the delayed arrivals and
departures by airlines, airports and dates
- create a dimensional model for the transformed data according to the primary interest of the
business stakeholders. Use dbdiagram for this part
- create a dashboard that business stakeholders can use for their analysis
- use these available data sources:
  - Swedavia FlightInfo API. Sign up for the access and obtain an API key according to the
instruction. Check out the API documentation here. Use data from both the endpoints
  - arrivals and departures. You should extract data covering the past three days (including
the date when you extract data) and all available airports in Sweden
  - Airline operator info from Wikipedia
  - Airport info from Wikipedia
follow Snowflake access control's best practices when setting up your cloud data warehouse. You
should develop within THE SAME trial account of Snowflake

**Additional requirements**
- containerize your codes with Docker, separately for dagsters and streamlit. Test your containers
locally
- deploy your containers to your Azure student account. Spin up container app and web app
resources. For the group presentation, you can show the deployment in one Azure student account
