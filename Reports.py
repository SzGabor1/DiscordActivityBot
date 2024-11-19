import matplotlib.pyplot as plt
from mongodb import MongoInit
from datetime import datetime, timedelta
import random
class Reports:
    def __init__(self):
        self.mongo = MongoInit()
    
    
    def makeReport(self, server_id, day):
        result = self.mongo.get_collection("sessions").find({"server_id": server_id, "start": {"$gte": day, "$lt": day + timedelta(days=1)}})

        fig, ax = plt.subplots(figsize=(12, 6))
        ax.set_xlim(0, 24 * 60)
        ax.set_xlabel('Hours of the Day')
        y_labels = []  
        y_positions = []
        ax.set_xticks([i * 60 for i in range(25)])
        ax.set_xticklabels([str(i) for i in range(25)])

        heights = {}
        colors = {}

        for data in result:
            name = data.get("user")
            if name not in heights:
                heights[name] = len(heights) * 10
                colors[name] = "#{:06x}".format(random.randint(0, 0xffffff))
                y_labels.append(name)
                y_positions.append(heights[name] + 5)
            session_start = data.get("start") - day
            session_end = data.get("end") - day

            start_bar = session_start.total_seconds() / 60
            bar_length = session_end.total_seconds() / 60 - start_bar

            ax.broken_barh([(start_bar, bar_length)], (heights[name], 10), facecolors=(colors[name]))
            ax.set_yticks(y_positions)
            ax.set_yticklabels(y_labels)
        filename = "./reports/gant.png"

        plt.savefig(filename)

        return filename