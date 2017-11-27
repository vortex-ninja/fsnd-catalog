# fsnd-catalog

### Live demo
https://fsnd-catalog-pro.herokuapp.com/

### Overview
Project 'Catalog' for Udacity Fullstack Nanodegree program. Basic manager for categories and items with login functionality (Google Sign in).

### Goals
1. Implement and learn CRUD functionality.
2. Connect application to the database.
3. Implement Sign In with google.

### Setup
1. You will require a `client_secrets.json` file from https://console.developers.google.com/ for OAuth2 authentication to work. It should be placed in the directory where `app.py` is located.
2. Set environment variables with `source .env`.
3. Run `database_setup.py` to create the database.
4. Run `database_seed.py` to initially populate database (optional step).
5. Start application by running `flask run` from the directory where `app.py` file is located.

### Routes

1. logging in: `/login`.
2. logging out: `/logout`.
3. main page: `/` or `/catalog`.
4. create category: `/category/new` - only logged in users.
5. edit category: `/category/<category_id>/edit` - only logged in owner of the category.
6. delete category: `/category/<category_id>/delete` - only logged in owner of the category.
7. show category: `/category/<category_id>`.
8. new item: `/items/new` - only logged in users.
9. edit item: `/category/<category_id>/items/<item_id>/edit` - only logged in owner of the item.
10. delete item: `/category/<category_id>/items/<item_id>/delete` - only logged in owner of the item.
11. show item: `/category/<category_id>/items/<item_id>`.
12. JSON endpoint, category list: `/categories/JSON`.
13. JSON endpoint, items list: `/category/<category_id>/items/JSON`.


### How to use

You can log in/out, execute CRUD operations or get JSON responses using directly the routes listed above.
CRUD operations and logging in/out can also be done by navigating the website and using buttons provided.
