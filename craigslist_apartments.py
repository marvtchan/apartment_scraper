# craigslist_apartments.py

from craigslist import CraigslistHousing
from connector_class import connection, session, Listing
from dateutil.parser import parse
class Craigslist_Scraper:

	def scrape_apt(params):
		cl = CraigslistHousing(site=params['site'], area=params['area'], category=params['category'], filters={'max_price': params['max_price'], 'min_price': params['min_price']})

		results = []
		iterations = 0
		post = cl.get_results(sort_by='newest', geotagged=True, limit=120)
		while True:
			try:
				result = next(post)
			except StopIteration:
				break
			except Exception:
				continue
			listing = session.query(Listing).filter_by(cl_id=result["id"]).first()

			if listing is None:
				if result["where"] is None:
					continue

				lat = 0
				lon = 0
				if result["geotag"] is not None:
					lat = result["geotag"][0]
					lon = result["geotag"][1]



				price = 0
				try:
					price = float(result["price"].replace("$", ""))
				except Exception:
					pass

				listing = Listing(
					link=result["url"],
	                created=parse(result["datetime"]),
	                lat=lat,
	                lon=lon,
	                name=result["name"],
	                price=price,
	                location=result["where"],
	                cl_id=result["id"]
	            )
				
				session.add(listing)
				session.commit()

			iterations += 1
			print("Post " + str(iterations) + " scraped successfully!")


		return results


params = {"site": "sfbay", "area": ["eby"], "category": "apa", "max_price": 3000, "min_price": 1000}

Craigslist_Scraper.scrape_apt(params)



