from naukri import Naukri
import asyncio

naukri = Naukri()

urls = ['data-science', 'data-analyst', 'data-engineer']
asyncio.get_event_loop().run_until_complete(naukri.run(urls))
