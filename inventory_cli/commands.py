"""CLI commands and argument parsing.

Each cmd_* function gets the ApiClient and the parsed arguments, calls the API
and prints the result with the display helpers.
"""
import argparse
import sys

from . import display
from .client import ApiClient, CLIError


# ---- commands ----

def cmd_list(client, args):
    items = client.list_items()
    if not items:
        print("Inventory is empty.")
    for item in items:
        display.print_item_row(item)


def cmd_view(client, args):
    display.print_item(client.get_item(args.id))


def cmd_add(client, args):
    data = {"product_name": args.name, "price": args.price, "stock": args.stock}
    if args.barcode:
        data["barcode"] = args.barcode
    if args.brand:
        data["brands"] = args.brand
    print("Added:")
    display.print_item(client.add_item(data))


def cmd_update(client, args):
    changes = {}
    if args.price is not None:
        changes["price"] = args.price
    if args.stock is not None:
        changes["stock"] = args.stock
    if not changes:
        raise CLIError("nothing to update, use --price and/or --stock")
    print("Updated:")
    display.print_item(client.update_item(args.id, changes))


def cmd_delete(client, args):
    print(client.delete_item(args.id)["message"])


def cmd_find(client, args):
    if args.barcode:
        display.print_product(client.lookup_barcode(args.barcode))
        return
    results = client.search_name(args.name)
    if not results:
        print("No products found.")
    for product in results:
        display.print_product(product)


def cmd_enrich(client, args):
    print("Item updated with OpenFoodFacts details:")
    display.print_item(client.enrich_item(args.id))


def cmd_import(client, args):
    # look the product up first, then save it in our inventory
    product = client.lookup_barcode(args.barcode)
    product["price"] = args.price
    product["stock"] = args.stock
    print("Imported:")
    display.print_item(client.add_item(product))


# ---- argument parsing ----

def whole_number(value):
    try:
        number = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"'{value}' is not a whole number")
    if number < 0:
        raise argparse.ArgumentTypeError("must be 0 or more")
    return number


def money(value):
    try:
        number = float(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"'{value}' is not a number")
    if number < 0:
        raise argparse.ArgumentTypeError("must be 0 or more")
    return number


def build_parser():
    parser = argparse.ArgumentParser(description="Inventory management CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="show all items").set_defaults(func=cmd_list)

    p = sub.add_parser("view", help="show one item")
    p.add_argument("id", type=whole_number)
    p.set_defaults(func=cmd_view)

    p = sub.add_parser("add", help="add a new item")
    p.add_argument("name")
    p.add_argument("--barcode")
    p.add_argument("--brand")
    p.add_argument("--price", type=money, default=0)
    p.add_argument("--stock", type=whole_number, default=0)
    p.set_defaults(func=cmd_add)

    p = sub.add_parser("update", help="change price or stock")
    p.add_argument("id", type=whole_number)
    p.add_argument("--price", type=money)
    p.add_argument("--stock", type=whole_number)
    p.set_defaults(func=cmd_update)

    p = sub.add_parser("delete", help="remove an item")
    p.add_argument("id", type=whole_number)
    p.set_defaults(func=cmd_delete)

    p = sub.add_parser("find", help="look a product up on OpenFoodFacts")
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--barcode")
    group.add_argument("--name")
    p.set_defaults(func=cmd_find)

    p = sub.add_parser("enrich", help="fill an item's details from OpenFoodFacts")
    p.add_argument("id", type=whole_number)
    p.set_defaults(func=cmd_enrich)

    p = sub.add_parser("import", help="add an OpenFoodFacts product by barcode")
    p.add_argument("barcode")
    p.add_argument("--price", type=money, default=0)
    p.add_argument("--stock", type=whole_number, default=0)
    p.set_defaults(func=cmd_import)

    return parser


def main(argv=None, client=None):
    args = build_parser().parse_args(argv)
    client = client or ApiClient()
    try:
        args.func(client, args)
    except CLIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    return 0
