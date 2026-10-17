# Postman Testing Guide & Verification

This guide outlines the Postman test scenarios required by the lab, complete with expected status codes, payloads, and screenshot references.

## Quick Start with Postman

1. Start the Flask application:
   ```bash
   python app.py
   ```
2. Open **Postman**.
3. Click **Import** (top left) and select the file `docs/inventory_api_postman_collection.json`.
4. You will see all 11 pre-configured requests ready to execute against `http://127.0.0.1:5000`.

---

## Required Requests & Expected Responses

### 1. GET All Items (`GET /inventory`)
* **URL:** `http://127.0.0.1:5000/inventory`
* **Status:** `200 OK`
* **Response:** Array of all inventory items (starts with 3 seed products: Coca-Cola, Nutella, Almond Milk).

### 2. GET Single Item (`GET /inventory/1`)
* **URL:** `http://127.0.0.1:5000/inventory/1`
* **Status:** `200 OK`
* **Response:** JSON object for item `id: 1` (`Coca-Cola Original`).

### 3. POST Create Item (`POST /inventory`)
* **URL:** `http://127.0.0.1:5000/inventory`
* **Header:** `Content-Type: application/json`
* **Body (raw JSON):**
  ```json
  {
    "product_name": "Maize Flour",
    "price": 2.2,
    "stock": 30,
    "barcode": "6001234567890",
    "brands": "Jogoo"
  }
  ```
* **Status:** `201 Created`
* **Response:** Returns the newly created item with assigned `id: 4`.

### 4. PATCH Update Item (`PATCH /inventory/4`)
* **URL:** `http://127.0.0.1:5000/inventory/4`
* **Header:** `Content-Type: application/json`
* **Body (raw JSON):**
  ```json
  {
    "stock": 25
  }
  ```
* **Status:** `200 OK`
* **Response:** Returns updated item with `stock: 25` and unchanged price/name.

### 5. DELETE Item (`DELETE /inventory/4`)
* **URL:** `http://127.0.0.1:5000/inventory/4`
* **Status:** `200 OK`
* **Response:**
  ```json
  {
    "message": "item 4 deleted"
  }
  ```

---

## Required Failure Cases (Error Handling Proof)

### 6. Invalid Price (`POST /inventory`)
* **Body:** `{"product_name": "Bad Price", "price": -1}`
* **Status:** `400 Bad Request`
* **Response:** `{"error": "price must be a number that is 0 or more"}`

### 7. Missing Item (`GET /inventory/999`)
* **Status:** `404 Not Found`
* **Response:** `{"error": "item not found"}`

### 8. Unsupported Method (`PUT /inventory/1`)
* **Method:** `PUT`
* **Status:** `405 Method Not Allowed`
* **Response:** `{"error": "The method is not allowed for the requested URL."}`

---

## OpenFoodFacts Integration Requests

### 9. Barcode Lookup (`GET /lookup/barcode/3017624010701`)
* **Status:** `200 OK`
* **Response:** Fetches cleaned product details directly from OpenFoodFacts (`Nutella`, `Ferrero`).

### 10. Search by Name (`GET /lookup/search?name=nutella`)
* **Status:** `200 OK` (or `502 Bad Gateway` if upstream OpenFoodFacts search API is temporarily unavailable).

### 11. Enrich Stored Item (`POST /inventory/2/enrich`)
* **Status:** `200 OK`
* **Response:** Updates stored item `id: 2` (Nutella) with latest brand and ingredient information from OpenFoodFacts without modifying local price or stock.
