# Run a test server.
from autopay import app
from autopay.business.db_business import EventBO, UserBO
import json 


@app.route('/')
def api_base():
	return 'hello'


event_bo = EventBO()
user_bo = UserBO()

print event_bo.search_open_event(1, "123123123")
