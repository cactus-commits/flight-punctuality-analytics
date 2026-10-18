-- Swedavia airports that are missing from the Wikipedia list (see seeds/missing_airports.csv)
with src_airport as (
    select airport_iata, airport_name, city from {{ ref('src_airport') }}
    union all
    select airport_iata, airport_name, city from {{ ref('missing_airports') }}
    where airport_iata not in (select airport_iata from {{ ref('src_airport') }} where airport_iata is not null)
)

select
    {{ dbt_utils.generate_surrogate_key(['airport_iata']) }} as airport_id,
    airport_iata, 
    MAX(trim(coalesce(airport_name, 'Missing'))) as airport_name,
    MAX(trim(coalesce(city, 'Missing'))) as city
from src_airport
where airport_iata is not null
group by airport_iata