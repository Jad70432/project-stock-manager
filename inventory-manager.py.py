class Product:
    def __init__(self, product_id, name, category, price, quantity, min_stock, units_sold=0):
        self.__product_id = product_id
        self.__name = name
        self.__category = category
        self.__price = float(price)
        self.__quantity = int(quantity)
        self.__min_stock = int(min_stock)
        self.__units_sold = int(units_sold)

    def get_id(self):
        return self.__product_id

    def get_name(self):
        return self.__name

    def get_category(self):
        return self.__category

    def get_price(self):
        return self.__price

    def get_quantity(self):
        return self.__quantity

    def get_min_stock(self):
        return self.__min_stock

    def get_units_sold(self):
        return self.__units_sold

    def update_info(self, name, category, price, quantity, min_stock):
        self.__name = name
        self.__category = category
        self.__price = float(price)
        self.__quantity = int(quantity)
        self.__min_stock = int(min_stock)

    def sell(self, amount):
        if amount <= 0 or amount > self.__quantity:
            return False
        self.__quantity = self.__quantity - amount
        self.__units_sold = self.__units_sold + amount
        return True

    def restock_needed(self):
        if self.__quantity < self.__min_stock:
            return self.__min_stock - self.__quantity
        return 0

    def stock_value(self):
        return self.__price * self.__quantity

    def to_line(self):
        return (self.__product_id + "," + self.__name + "," + self.__category + "," +
                str(self.__price) + "," + str(self.__quantity) + "," +
                str(self.__min_stock) + "," + str(self.__units_sold) + "\n")

    def __str__(self):
        return ("ID: " + self.__product_id + " | " + self.__name + " (" + self.__category + ")" +
                " | Price: $" + format(self.__price, ".2f") +
                " | Qty: " + str(self.__quantity) +
                " | Min: " + str(self.__min_stock) +
                " | Sold: " + str(self.__units_sold))


class Inventory:
    def __init__(self):
        self.__products = {}

    def has_product(self, product_id):
        return product_id in self.__products

    def is_empty(self):
        return len(self.__products) == 0

    def get_all_products(self):
        return self.__products.values()

    def add_product(self, product):
        pid = product.get_id()
        if pid in self.__products:
            return False
        self.__products[pid] = product
        return True

    def edit_product(self, product_id, name, category, price, quantity, min_stock):
        if product_id not in self.__products:
            return False
        p = self.__products[product_id]
        p.update_info(name, category, price, quantity, min_stock)
        return True

    def search_products(self, keyword):
        matches = []
        keyword = keyword.lower()
        for product in self.__products.values():
            product_id = product.get_id().lower()
            name = product.get_name().lower()
            category = product.get_category().lower()
            if keyword in product_id or keyword in name or keyword in category:
                matches.append(product)
        return matches

    def process_order(self, order_list):
        if len(order_list) == 0:
            return False, "Order cannot be empty.", 0.0
        quantities = {}
        for product_id, quantity in order_list:
            if product_id not in self.__products:
                return False, "Product ID not found: " + product_id, 0.0
            if quantity <= 0:
                return False, "Quantity must be greater than zero.", 0.0

            if product_id not in quantities:
                quantities[product_id] = 0
            quantities[product_id] += quantity

        for product_id, quantity in quantities.items():
            product = self.__products[product_id]
            if quantity > product.get_quantity():
                return False, "Not enough stock for " + product_id, 0.0

        total = 0.0
        for product_id, quantity in quantities.items():
            product = self.__products[product_id]
            product.sell(quantity)
            total += product.get_price() * quantity

        return True, "Order completed.", total


    def get_low_stock(self):
        low_list = []
        for product in self.__products.values():
            needed = product.restock_needed()
            if needed > 0:
                low_list.append((product, needed))
        return low_list

    def get_category_values(self):
        totals = {}
        for product in self.__products.values():
            category = product.get_category()
            if category not in totals:
                totals[category] = 0.0
            totals[category] += product.stock_value()
        return totals

    def get_top_sellers(self):
        if len(self.__products) == 0:
            return [], 0

        max_sold = -1
        for product in self.__products.values():
            sold = product.get_units_sold()
            if sold > max_sold:
                max_sold = sold

        top_list = []
        for product in self.__products.values():
            if product.get_units_sold() == max_sold:
                top_list.append(product)

        return top_list, max_sold

    def save_file(self, filename):
        outfile = open(filename, "w")
        for product in self.__products.values():
            outfile.write(product.to_line())
        outfile.close()

    def load_file(self, filename):
        try:
            infile = open(filename, "r")
        except IOError:
            return False

        self.__products.clear()
        line = infile.readline()
        while line != "":
            line = line.rstrip("\n")
            if line != "":
                parts = line.split(",")
                if len(parts) == 7:
                    product_id, name, category, price, quantity, min_stock, units_sold = parts
                    product = Product(product_id, name, category, price,
                                      quantity, min_stock, units_sold)
                    self.__products[product_id] = product
            line = infile.readline()
        infile.close()
        return True

def read_int(prompt):
    while True:
        text = input(prompt)
        try:
            num = int(text)
            return num
        except ValueError:
            print("Invalid input. Enter a whole number.")


def read_float(prompt):
    while True:
        text = input(prompt)
        try:
            num = float(text)
            return num
        except ValueError:
            print("Invalid input. Enter a number.")

def load_sample_data(inv):
    inv.add_product(Product("P101", "Wireless Mouse", "Electronics", 25.0, 15, 5, 12))
    inv.add_product(Product("P102", "Mechanical Keyboard", "Electronics", 75.0, 3, 5, 8))
    inv.add_product(Product("P103", "USB-C Cable", "Accessories", 10.0, 30, 10, 20))
    inv.add_product(Product("P104", "Laptop Stand", "Accessories", 35.0, 4, 6, 20))
    inv.add_product(Product("P105", "Notebook A4", "Stationery", 4.5, 50, 15, 5))


def main():
    inv = Inventory()
    filename = "inventory_data.txt"
    load_sample_data(inv)

    choice = ""
    while choice != "0":
        print("\n--- Inventory & Stock Manager ---")
        print("1. View all products")
        print("2. Add product")
        print("3. Edit product")
        print("4. Search products")
        print("5. Sell products (Order)")
        print("6. List low stock products")
        print("7. Stock value by category and top sellers")
        print("8. Save to file")
        print("9. Load from file")
        print("0. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            if inv.is_empty():
                print("Inventory is empty.")
            else:
                for p in inv.get_all_products():
                    print(p)

        elif choice == "2":
            pid = input("Product ID: ")
            if pid == "":
                print("ID cannot be empty.")
            elif inv.has_product(pid):
                print("Product ID already exists.")
            else:
                name = input("Name: ")
                category = input("Category: ")
                price = read_float("Price: ")
                qty = read_int("Quantity: ")
                min_stock = read_int("Minimum stock level: ")
                if price < 0 or qty < 0 or min_stock < 0:
                    print("Values cannot be negative.")
                else:
                    p = Product(pid, name, category, price, qty, min_stock)
                    inv.add_product(p)
                    print("Product added.")

        elif choice == "3":
            pid = input("Enter Product ID to edit: ")
            if not inv.has_product(pid):
                print("Product ID not found.")
            else:
                name = input("New Name: ")
                category = input("New Category: ")
                price = read_float("New Price: ")
                qty = read_int("New Quantity: ")
                min_stock = read_int("New Minimum stock level: ")
                if price < 0 or qty < 0 or min_stock < 0:
                    print("Values cannot be negative.")
                else:
                    inv.edit_product(pid, name, category, price, qty, min_stock)
                    print("Product updated.")

        elif choice == "4":
            keyword = input("Enter ID, name, or category: ")
            results = inv.search_products(keyword)
            if len(results) == 0:
                print("No matching products found.")
            else:
                for p in results:
                    print(p)

        elif choice == "5":
            order_list = []
            pid = input("Enter Product ID (or done to finish): ")
            while pid.lower() != "done":
                qty = read_int("Enter quantity: ")
                order_list.append((pid, qty))
                pid = input("Enter Product ID (or done to finish): ")

            ok, msg, total = inv.process_order(order_list)
            print(msg)
            if ok:
                print("Total price: $" + format(total, ".2f"))

        elif choice == "6":
            low_items = inv.get_low_stock()
            if len(low_items) == 0:
                print("No products below minimum stock.")
            else:
                for product, needed in low_items:
                    print(product.get_id(), "-", product.get_name(),
                          "| Qty:", product.get_quantity(),
                          "| Min:", product.get_min_stock(), "| Needed:", needed)

        elif choice == "7":
            cat_totals = inv.get_category_values()
            if len(cat_totals) == 0:
                print("Inventory is empty.")
            else:
                print("\nStock value by category:")
                for category, value in cat_totals.items():
                    print(category + ": $" + format(value, ".2f"))

                top_list, max_sold = inv.get_top_sellers()
                print("\nTop selling product(s) (" + str(max_sold) + " units sold):")
                for p in top_list:
                    print(p.get_id(), "-", p.get_name())

        elif choice == "8":
            inv.save_file(filename)
            print("Saved to", filename)

        elif choice == "9":
            if inv.load_file(filename):
                print("Loaded from", filename)
            else:
                print("File does not exist.")

        elif choice == "0":
            print("Goodbye.")

        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()
