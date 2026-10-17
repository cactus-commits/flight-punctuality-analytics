with 
    fct_arrivals as (select * from {{ ref('fct_arrivals') }}),
    dim_airline as (select * from {{ ref('dim_airline') }}),
    dim_airport as (select * from {{ ref('dim_airport') }}),
    dim_date as (select * from {{ ref('dim_date') }})
select
    al.airline_name,
    al.airline_country,
    dep.airport_name as departure_airport_name,
    arr.airport_name as arrival_airport_name, 
    d.date,
    fa.flight_status,
    fa.scheduled_arrival_utc,
    fa.actual_arrival_utc,
    datediff('minute', fa.scheduled_arrival_utc, fa.actual_arrival_utc) as delay_minutes,
    delay_minutes >= 15 as is_delayed -- null if not landed yet, so averages only count landed flights
from fct_arrivals fa
left join dim_date d on fa.date_id = d.date_id
left join dim_airline al on fa.airline_id = al.airline_id
left join dim_airport arr on fa.arrival_airport_id = arr.airport_id
left join dim_airport dep on fa.departure_airport_id = dep.airport_id
where fa.flight_status != 'Deleted' -- Deleted = removed record in Swedavia data, not a real flight



