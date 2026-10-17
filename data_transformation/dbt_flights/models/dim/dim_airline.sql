with src_airline as (select * from {{ ref('src_airline') }}

)
select
    {{ dbt_utils.generate_surrogate_key(['airline_iata']) }} as airline_id,
    airline_iata,
    coalesce(max(airline_icao), 'Missing') as airline_icao,
    coalesce(max(trim(airline_name)), 'Missing') as airline_name,
    coalesce(max(trim(airline_country)), 'Missing') as airline_country
from src_airline
where airline_iata is not null
group by airline_iata


