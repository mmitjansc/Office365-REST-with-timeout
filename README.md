This is the same project as Office365-REST (https://github.com/vgrem/Office365-REST-Python-Client), but with the addition of a timeout_ variable in execute_query(), which gets passed down to requests.get. This prevents the execution from hanging indefinitely.

To execute a query with a timeout, simply add the following argument at the end:
 TIMEOUT=10
 my_query.execute_query(timeout_=TIMEOUT)

It also works with `execute_query_retry(timeout_=TIMEOUT)`.