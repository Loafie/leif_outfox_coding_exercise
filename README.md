_Setup Instructions_

-Clone the repo.

-docker-compose up --build

-Database is automatically populated on FastAPI app start-up

-When restarting the docker containers be sure to purge existing volumes first.

_ETL_

-The ETL/ folder contains etl.py which takes two input files and produces output.csv files.

-The output files are already in the data/ folder.

-To regenerate them download https://catalog.data.gov/dataset/medicare-inpatient-hospitals-by-provider-and-service-9af02/resource/e51cf14c-615a-4efe-ba6b-3a3ef15dcfb0 as a csv, and also export https://public.opendatasoft.com/explore/dataset/georef-united-states-of-america-zc-point/table/?flg=en-us as a cvs and place them in the ETL folder and run etl.py

_Example CURL commands_

providers/ GET:

curl "http://localhost:8000/providers/?zipcode=14626&drg=knee%20replacement&radius=75"

Takes a target zipcode as __zipcode__ and search string for drg description as __drg__ and an option __radius__ parameter (default 25.)

Returns all columns for all entries within __radius__ distance of __zipcode__ sorted in descending order by how much medicare covers on average.

ask/ GET:

curl "http://localhost:8000/ask/?query=Which%20hospitals%20in%20NY%20have%20the%20highest%20rating%20for%20knee%20replacements?"

Takes a question as __query__ and returns a natural language response to the question.

