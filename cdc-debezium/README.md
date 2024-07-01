`make`

Wait a few seconds

`make register-connector`

Open http://localhost:8080/topics and see the topic `cdc.public.customer_addresses` created

Run Spice

```bash
spice run
```

Observe that it consumes all of the changes.

Run `spice sql` to query the data

```sql
SELECT * FROM cdc;
```

Use psql to insert some data

```bash
PGPASSWORD="postgres" psql -h localhost -U postgres -d postgres -p 15432
```

```sql
INSERT INTO public.customer_addresses (id, first_name, last_name, email) 
VALUES 
(100, 'John', 'Doe', 'john@doe.com');
```

Notice that the Spice log shows the change. Querying the data again will show the new record.

```sql
SELECT * FROM cdc;
```

Stop spice with `Ctrl+C`

Restart Spice with `spice run`

Observe that it doesn't replay the changes and the data is still there. New changes will be consumed.