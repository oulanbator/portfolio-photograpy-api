# Portfolio-photograpy-api

My first Flask API, designed to serve my other project (portfolio-photography), which is a React web portfolio.
This Flask app serves JSON answers for a full featured portfolio website.

* SQLite database managed with SQLAlchemy ORM
* Many endpoints for information request, and upload/update information
* Only two Models implemented in the DB : "Image" and "Gallery" connected in a many-to-many relationship

# Heroku Demo
The API is currently running on Heroku. You can check it at the different endpoints, for example :
> https://portfolio-photographie-api.herokuapp.com/api/medias
> 
> https://portfolio-photographie-api.herokuapp.com/api/galleries

Check the api/routes.py for a better view on the different endpoints

# Minimal Setup Example

To build some examples locally, clone this repository :
> git clone https://github.com/oulanbator/portfolio-photograpy-api/

Then install requirements.txt and run the app
> python app.py

Your API should be running on localhost:5000

That's it !
