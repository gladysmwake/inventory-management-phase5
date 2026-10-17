"""Everything the CLI prints. Kept separate so the format can change without
touching the commands."""


def print_item(item):
    print(f"[{item['id']}] {item['product_name']}")
    print(f"    brand:       {item['brands'] or '-'}")
    print(f"    barcode:     {item['barcode'] or '-'}")
    print(f"    price:       {item['price']}")
    print(f"    stock:       {item['stock']}")
    print(f"    ingredients: {item['ingredients_text'] or '-'}")


def print_item_row(item):
    print(f"{item['id']:>3}  {item['product_name']:<30} price {item['price']:<8} stock {item['stock']}")


def print_product(product):
    name = product["product_name"] or "(no name)"
    print(f"{name}  |  {product['brands'] or '-'}  |  barcode {product['barcode'] or '-'}")
