with 
    fct_departures as (select * from {{ ref('fct_departures') }}),
    dim_airline as (select * from {{ ref('dim_airline') }}),
    dim_airport as (select * from {{ ref('dim_airport') }}),
    dim_date as (select * from {{ ref('dim_date') }})
select
    coalesce(al.airline_name, 'Unknown') as airline_name,
    coalesce(al.airline_country, 'Unknown') as airline_country,
    coalesce(dep.airport_name, 'Unknown') as departure_airport_name, 
    coalesce(arr.airport_name, 'Unknown') as arrival_airport_name, 
    d.date,
    fd.flight_status,
    fd.scheduled_departure_utc,
    fd.actual_departure_utc,
    datediff('minute', fd.scheduled_departure_utc, fd.actual_departure_utc) as delay_minutes,
    delay_minutes >= 15 as is_delayed -- null if not landed yet, so averages only count landed flights
from fct_departures fd
left join dim_date d on fd.date_id = d.date_id
left join dim_airline al on fd.airline_id = al.airline_id
left join dim_airport dep on fd.departure_airport_id = dep.airport_id
left join dim_airport arr on fd.arrival_airport_id = arr.airport_id
WHERE flight_status != 'Deleted'


