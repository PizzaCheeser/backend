# Pizza cheeser

The project is available at: https://pizza-cheeser.psota.pl/.
The frontend part is not fully done yet. Although it doesn't look good - it works!
You can also use slack app. 
Use the command to find the pizza:
`/pizza post-code;wanted ingredient 1,wanted ingredient 2,...;not wanted ingredient1, not wanted ingredient 2, ...`

### How does it work?
Pizza cheeser can choose the perfect pizza for you and for your group of friends.
You just need to set up location where you would like to have pizza delivered,
choose ingredients which you would like to have on your pizza,
and mark ingredients which you don't like.
Pizza cheeser will match the best pizzas for you and show you the results. 
Then you can choose the cheaper one or this which you like the most.
Bon appetit!

### How to run it
- `git clone https://github.com/Prasnal/Pizza_Cheeser.git`
- `cd src`
- `docker-compose build`
- `docker-compose up`

To scrape pizzerias and insert them to the database:

- `docker-compose exec web bash`
- `python db/migrate.py --help`
- then run `python init_dabase` with the correct parameters
- `python ScraperDatabaseConnector.py --help`
- then run `python ScraperDatabaseConnector.py` with the correct parameters

Then you need to run the frontend part, you can read how to do this here: https://github.com/Prasnal/Pizza-frontend

### API:
- `GET /api/all-ingredients/<postcode>`
Returns all ingredients (in JSON) from pizzas available in the particular location

- `POST /api/get-pizzas`
```json
{
    "must":[],
    "must_not": [],
    "post_code": ''
}
```
Returns all pizzas available in particular location with `must` ingredients
and without `must_not` ingredients.

- `POST /slack/get-pizzas`
used for slack integration

### Database structure
- keyspaces: locations, pizzerias


### How to integrate with slack app:
- Go to your slack app website in: `https://api.slack.com/apps/`
- Add slash command
- Create new command i.e `/pizza`
- Set up a correct request URL (should be ended ) - you can use ngrok.io to expose the port 5000
then copy forwarding URL and add `/slack/get-pizzas` at the end


### TODO in the future:
 - Finish all TODOs in the code
 - Implement Celery in scrapers (i.e scrape_locations in ScraperDatabaseConnector)
 - Size should be normalized after scraping, get_price function should be changed
 - Grouping ingredients by type (i.e cheese, meat, vegetable etc.)
 - Better ingredients validator: ingredients ratio should be inserted the separate database keyspace,
  should be modifiable and the radio should be taken from there
 - Add more countries and english version
 - Swagger