# Pizza cheeser

The project is available at: www.pizza-cheeser.psota.pl

### How does it work?
Pizza cheeser can choose the perfect pizza for you and for your groups of friends.
You just need to set up location where you would like to have pizza delivered,
choose ingredients which you like and would like to have on your pizza,
and mark ingredients which you don't like.
Pizza cheeser will match the best pizzas for you and show you the results. 
Then you can choose the cheaper one or this which you like the most.
Bon apetit!

### How to run it
- `git clone https://github.com/Prasnal/Pizza_Cheeser.git`
- `cd src`
- `docker-compose up`

To scrape pizzerias and insert them to the database:

- `docker-compose exec web`
- `python ScraperDatabaseConnector`

Then you need to run the frontend part, you can read how to do this *here*

### API:
- `GET /api/all_ingredients`
Returns all ingredients from pizzas in JSON

- `POST /api/choosen-ingredients`
```json
{
    "must":[],
    "must_not": [],
    "post_code": ''
}
```
Returns all pizzas in particular location with `must` ingredients
and without `must_not` ingredients.

### Database structure
- keyspace locations
- keyspace pizzerias

TODO: add database structure

### How does it work
TODO: how does it work

### TODO in the future:
 - GET all_ingredients should sort ingredients via location
 - pizza -> pizzas, refactor pizzerias_id name
 - Implement Celery in scrapers (i.e scrape_locations in ScraperDatabaseConnector)
 - Argument for ScraperDatabaseConnector with the post code
 - Size should be normalized after scraping, get_price function should be changed
 - More fields in the result table, sorting by size/price
 - Grouping ingredients by type (i.e cheese, meat, vegetable etc.)
 - Better ingredients validator: ingredients ratio should be inserted the separate database keyspace,
  should be modifiable and the radio should be taken from there
 - Add more countries and english version
 - Better error handling
 - Slack integration
 - Swagger