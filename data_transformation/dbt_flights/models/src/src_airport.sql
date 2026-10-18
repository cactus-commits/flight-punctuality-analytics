with src_airports as (select * from {{ source('wikipedia', 'airports') }})
select
    IATA_CODE as airport_iata,
    AIRPORT as airport_name,
    LOCATION as city
from src_airports
