__Setup Instructions__

-Clone the repo.

-docker-compose up --build

-Create a .env file with:

  DATABASE_URL=postgresql+asyncpg://postgres:pass123@db:5432/postgres
  
  OPENAI_API_KEY=<your key>
  
-Database is automatically populated on FastAPI app start-up

-When restarting the docker containers be sure to purge existing volumes first.

__ETL__

-The ETL/ folder contains etl.py which takes two input files and produces output.csv files.

-The output files are already in the data/ folder.

-To regenerate them download https://catalog.data.gov/dataset/medicare-inpatient-hospitals-by-provider-and-service-9af02/resource/e51cf14c-615a-4efe-ba6b-3a3ef15dcfb0 as a csv, and also export https://public.opendatasoft.com/explore/dataset/georef-united-states-of-america-zc-point/table/?flg=en-us as a cvs and place them in the ETL folder and run etl.py

__Example CURL commands__

providers/ GET:

curl "http://localhost:8000/providers/?zipcode=14626&drg=knee%20replacement&radius=75"

Takes a target zipcode as _zipcode_ and search string for drg description as _drg_ and an option _radius_ parameter (default 25.)

Returns all columns for all entries within _radius_ distance of _zipcode_ sorted in descending order by how much medicare covers on average.

ask/ GET:

curl "http://localhost:8000/ask/?query=Which%20hospitals%20in%20NY%20have%20the%20highest%20rating%20for%20knee%20replacements?"

Takes a question as _query_ and returns a natural language response to the question.


__Example Prompts that Agent Can Answer:__

-Which institutions offer kidney related procedures?

-Which hospitals in NY have the highest rating for knee replacement?

-Which hospitals within 25 km of Rochester, NY (zip 14617) are the best at knee replcements?

-What kind of procedures are available to me within 15km of zip 11694?

-Which hospitals have performed the most kidney related procedures in NY?

__Architecture Decisions__

-Decided not to use Langchain/LangGraph due to time constraints. I have not written Langchain/LangGraph code in a year or more and even though it's much more efficient to use at scale, I thought it would be quicker to just write the LLM logic from scratch for this scope.

-Did not use the GIS/Geo extensions for Postgres just because sometimes things like that can eat up a lot of time to get working when you have to wrestle with different versions and dependencies etc.

-The ETL portion was kind of quick and dirty (due to time constraints.) It could have been done in a much more organized and streamlined way and could have been built into the docker image.
