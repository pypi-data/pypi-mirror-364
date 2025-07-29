--install airport from community;
--load airport;

CREATE SECRET airport_testing (
  type airport,
  auth_token uuid(),
  scope 'grpc://localhost:50003');

CALL airport_action('grpc://localhost:50003', 'create_database', 'test1');

ATTACH 'test1' (TYPE  AIRPORT, location 'grpc://localhost:50003');
--create table small_numbers (n bigint);
--INSERT INTO small_numbers (select * as n  from generate_series(1, 900000000));
explain analyze select sum(test1.utils.test_add(n, n)) from small_numbers;

--explain analyze select n, length(test1.utils.collatz_sequence(n)) from small_numbers order by 2 desc;

-- select test1.utils.soa_for_ip('8.8.8.8');

-- select test1.utils.soa_for_ip('1.1.1.1');
-- select test1.utils.soa_for_ip('153.90.3.216');

-- create table addresses as (
-- with values as (
-- select * as n from generate_series(1, 252)
-- )
-- select v1.n || '.' || v2.n || '.1.1' as ip from values as v1, values as v2 order by random());


-- select ip, test1.utils.soa_for_ip(ip) from addresses limit 100;