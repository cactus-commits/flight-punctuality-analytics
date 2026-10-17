with src_arrivals as (select * from {{ ref('src_arrivals') }})

select
    {{ dbt_utils.generate_surrogate_key([
        'flight_number',
        'flight_departure_date_utc',
        'departure_airport_iata',
        'arrival_airport_iata'
    ]) }} as arrival_id,
    flight_number,
    {{ dbt_utils.generate_surrogate_key(['cast(scheduled_arrival_utc as date)']) }} as date_id,
    {{ dbt_utils.generate_surrogate_key(['airline_iata']) }} as airline_id,
    {{ dbt_utils.generate_surrogate_key(['arrival_airport_iata']) }} as arrival_airport_id,
    {{ dbt_utils.generate_surrogate_key(['departure_airport_iata']) }} as departure_airport_id,
    flight_status_code,
    flight_status,
    scheduled_arrival_utc,
    estimated_arrival_utc,
    actual_arrival_utc,
    data_fetched_date
from src_arrivals
-- keep only one row per unique flight
qualify row_number() over ( 
    -- if these row has the exact same information 
    -- - they hashes as one row, to avoid duplicates
    partition by
        flight_number,
        flight_departure_date_utc,
        departure_airport_iata,
        arrival_airport_iata
    order by case when flight_status = 'Deleted' then 1 else 0 end, -- real row before Deleted copy, regardless of fetch order
    data_fetched_date desc, actual_arrival_utc desc nulls last) = 1 -- keeps the first row in each group


