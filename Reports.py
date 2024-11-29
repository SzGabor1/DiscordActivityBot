import matplotlib.pyplot as plt
from mongodb import MongoInit
from datetime import datetime, timedelta
import random
class Reports:
    def __init__(self):
        self.mongo = MongoInit()
    

    def makeReport(self, server_id, day, sessions):
        next_day = day + timedelta(days=1)
        result = self.mongo.get_collection("sessions").find({
            "server_id": server_id,
            "$or": [
                {"start": {"$lt": next_day, "$gte": day}},
                {"end": {"$gt": day, "$lt": next_day}},
                {"start": {"$lte": day}, "end": {"$gte": next_day}}
            ]
        })
        result = list(result)
        
        for user, session in sessions.items():
            start = session.session_start
            end = datetime.now() + timedelta(hours=1)
            result.append({
                "user": user,
                "start": start,
                "end": end,
            })

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
                colors[name] = "#{:06x}".format(random.randint(0, 0xFFFFFF))
                y_labels.append(name)
                y_positions.append(heights[name] + 5)

            session_start = max(data.get("start"), day)
            session_end = min(data.get("end"), next_day)

            if data.get("start") < day:
                session_start = day
            if data.get("end") > next_day:
                session_end = next_day

            start_bar = (session_start - day).total_seconds() / 60
            bar_length = (session_end - session_start).total_seconds() / 60

            ax.broken_barh([(start_bar, bar_length)], (heights[name], 10), facecolors=(colors[name]))

        ax.set_yticks(y_positions)
        ax.set_yticklabels(y_labels)

        filename = "./reports/gantt.png"
        plt.savefig(filename)
        return filename





    def generateGanttReportMic(self, server_id, day, sessions):
        result = self.mongo.get_collection("sessions").find({
            "server_id": server_id, 
            "start": {"$gte": day, "$lt": day + timedelta(days=1)}
        })
        result = list(result)
        
        mute_data = self.mongo.get_collection("mic_states").find({
            "server_id": server_id, 
            "start": {"$gte": day, "$lt": day + timedelta(days=1)}
        })
        mute_data = list(mute_data)

        for user, session in sessions.items():
            start = session.session_start
            end = datetime.now() + timedelta(hours=1)
            result.append({
                "user": user,
                "start": start,
                "end": end,
                "mic_state": "unmuted"
            })

        fig, ax = plt.subplots(figsize=(12, 6))
        ax.set_xlim(0, 24 * 60)
        ax.set_xlabel('Hours of the Day')

        ax.set_xticks([i * 60 for i in range(25)])
        ax.set_xticklabels([str(i) for i in range(25)])

        heights = {}
        colors = {}
        y_labels = []  
        y_positions = []


        for data in result:
            name = data.get("user")
            if name not in heights:
                heights[name] = len(heights) * 10
                colors[name] = "#{:06x}".format(random.randint(0, 0xffffff))
                y_labels.append(name)
                y_positions.append(heights[name] + 5)
            
            session_start = data.get("start") - day
            session_end = data.get("end") or datetime.now()
            session_end = session_end - day

            start_bar = session_start.total_seconds() / 60
            bar_length = session_end.total_seconds() / 60 - start_bar


            muted = False
            for mute in mute_data:
                if mute.get("user") == name and mute.get("mic_state") == "muted":
                    mute_start = mute.get("start") - day
                    mute_end = mute.get("end") or datetime.now()
                    mute_end = mute_end - day

                    if (session_start < mute_end and session_end > mute_start):
                        muted = True
                        break
            
    
            if muted:
                ax.broken_barh([(start_bar, bar_length)], (heights[name], 10), facecolors='red')
            else:
                ax.broken_barh([(start_bar, bar_length)], (heights[name], 10), facecolors=colors[name])

            ax.set_yticks(y_positions)
            ax.set_yticklabels(y_labels)

        filename = "./reports/gantmic.png"
        plt.savefig(filename)

        return filename