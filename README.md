# Inventory Management System (Flask REST API + CLI)

A small inventory system for a retail shop. Employees can add, view, update and delete
products through a Flask REST API, and look products up on the
[OpenFoodFacts API](https://world.openfoodfacts.org) to fill in details. There is a
command line tool to use the API without writing any requests by hand.

Storage is a plain Python list in memory, so data resets every time the server restarts.

## Setup

Needs Python 3.9+.

```bash
git clone <your-repo-url>
cd inventory-management-phase5
python -m venv venv
source venv/bin/activate        # on Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Running it

Terminal 1, start the API:

```bash
python app.py
```

It runs on http://127.0.0.1:5000. Terminal 2, use the CLI:

```bash
python cli.py list
```

If the API is somewhere else, set `INVENTORY_API_URL` first.

## Project layout

```
app.py                  entry point, creates the Flask app
cli.py                  entry point for the command line tool
inventory_api/
    __init__.py         create_app() factory
    routes.py           HTTP routes (thin, no business logic)
    store.py            the in-memory "database" (InventoryStore)
    validators.py       input validation
    services.py         logic that mixes the store and OpenFoodFacts (enrich)
    off_client.py       talks to OpenFoodFacts and nothing else
    errors.py           custom exceptions and their JSON error handlers
inventory_cli/
    client.py           HTTP calls to our API
    commands.py         CLI commands and argument parsing
    display.py          everything that gets printed
tests/                  pytest tests for each layer
```

Each layer has one job. Routes only deal with HTTP, the store only deals with the list,
and validation and error responses live in their own files. To move to a real database
later, only `store.py` needs to change.

## Data

Each item looks like this (field names follow OpenFoodFacts where it made sense):

```json
{
  "id": 3,
  "barcode": "0025293000019",
  "product_name": "Organic Almond Milk",
  "brands": "Silk",
  "ingredients_text": "Filtered water, almonds, cane sugar",
  "price": 4.0,
  "stock": 20
}
```

`product_name` is required when adding an item. `price` must be 0 or more and `stock`
must be a whole number that is 0 or more. Unknown fields are rejected with a 400.

## API endpoints

| Method | Route | What it does | Success |
|--------|-------|--------------|---------|
| GET | `/inventory` | all items | 200 |
| GET | `/inventory/<id>` | one item | 200 |
| POST | `/inventory` | add an item | 201 |
| PATCH | `/inventory/<id>` | update only the fields you send | 200 |
| DELETE | `/inventory/<id>` | remove an item | 200 |
| GET | `/lookup/barcode/<barcode>` | find a product on OpenFoodFacts by barcode | 200 |
| GET | `/lookup/search?name=<text>` | search OpenFoodFacts by name (up to 5 results) | 200 |
| POST | `/inventory/<id>/enrich` | fill an item's name, brand and ingredients from OpenFoodFacts using its barcode | 200 |

Errors always come back as `{"error": "..."}` with one of these codes:

- `400` bad input (missing name, negative price, unknown field, bad barcode)
- `404` item or product not found
- `502` OpenFoodFacts could not be reached

Example with curl:

```bash
curl -X POST http://127.0.0.1:5000/inventory \
  -H "Content-Type: application/json" \
  -d '{"product_name": "Maize Flour", "price": 2.2, "stock": 30}'

curl -X PATCH http://127.0.0.1:5000/inventory/4 \
  -H "Content-Type: application/json" \
  -d '{"stock": 25}'
```

## CLI commands

```bash
python cli.py list                                   # show all items
python cli.py view 3                                 # show one item
python cli.py add "Maize Flour" --price 2.2 --stock 30 --barcode 6001234567890 --brand Jogoo
python cli.py update 4 --price 2.5 --stock 20        # change price and/or stock
python cli.py delete 4                               # remove an item

python cli.py find --barcode 3017624010701           # look up on OpenFoodFacts
python cli.py find --name "oat milk"                 # search OpenFoodFacts by name
python cli.py enrich 2                               # fill item 2's details from OpenFoodFacts
python cli.py import 3017624010701 --price 6 --stock 10   # look up a barcode and add it
```

Bad input (a negative stock, a price that is not a number, an id that does not exist) or
an API that is down prints an `Error: ...` message and exits with code 1 instead of
crashing.

## Running the tests

```bash
pytest
```

The tests never call the real OpenFoodFacts API. `requests.get` is mocked with
`unittest.mock`, so they run offline. They cover:

- the store and the validators on their own
- all the CRUD endpoints, including 404s, 405s and invalid input
- the OpenFoodFacts client (found, not found, timeout, no internet, bad JSON)
- the lookup and enrich routes and the enrich service
- every CLI command and its error handling

To try the API by hand, start `python app.py` (debug mode is on) and send requests with
Postman or curl. Postman needs the header `Content-Type: application/json` for POST and
PATCH requests.

## Notes

- OpenFoodFacts asks apps to send a custom `User-Agent`, which `off_client.py` does.
- The v2 search endpoint does not support searching by text, so name search uses the older
  `/cgi/search.pl` endpoint.
- Since the "database" is a list, ids keep counting up and are not reused after a delete.
- Adding a new resource later means a new route file, and nothing in the store or client changes.
