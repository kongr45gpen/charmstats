from xml.dom import minidom
import coloredlogs, logging
import dateutil.parser
import datetime
import matplotlib
import matplotlib.pyplot as plt

coloredlogs.install()

xmldoc = minidom.parse('what.charmdatabaseexport')

timeline = {}

tasks = {}
tasklist = xmldoc.getElementsByTagName('task')
logging.info("Found {} tasks".format(len(tasklist)))
for task in tasklist:
    tasks[task.attributes['taskid'].value] = {
        "name": task.childNodes[0].data,
    }

events = []
eventlist = xmldoc.getElementsByTagName('event')
logging.info("Found {} events".format(len(eventlist)))

max_date = None
min_date = None
for event in eventlist:
    event = {
        "start": dateutil.parser.isoparse(event.attributes['start'].value),
        "end": dateutil.parser.isoparse(event.attributes['end'].value),
        "task": event.attributes['taskid'].value
    }
    event["duration"] = event["end"] - event["start"]
    events.append(event)

    date = event["start"].date()

    if date < datetime.datetime.today().date().replace(day=1):
        continue

    if max_date is None or date > max_date:
        max_date = date
    if min_date is None or date < min_date:
        min_date = date

    if "calendar" not in tasks[event["task"]]:
        tasks[event["task"]]["calendar"] = {}
    if date not in tasks[event["task"]]["calendar"]:
        tasks[event["task"]]["calendar"][date] = 0
    tasks[event["task"]]["calendar"][date] += event["duration"].seconds / 3600

for task in tasks.values():
    if "calendar" in task:
        date_iterator = min_date
        while date_iterator <= max_date:
            if date_iterator not in task["calendar"]:
                task["calendar"][date_iterator] = 0
            date_iterator += datetime.timedelta(days=1)
        task["calendar"] = dict(sorted(task["calendar"].items()))

        x = list(task["calendar"].keys())
        y = list(task["calendar"].values())
        title = task["name"]

        plt.plot(x, y, label=title)
        plt.fill_between(x, y, alpha=0.2)

plt.grid()
plt.legend()
plt.xlabel("date")
plt.ylabel("hours")
plt.show()
