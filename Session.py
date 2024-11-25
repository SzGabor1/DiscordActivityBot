from mongodb import MongoInit
from bson.objectid import ObjectId
from datetime import datetime,timedelta

class Session:
    def __init__ (self,member):
        self.id = str(ObjectId())
        self.mongo = MongoInit()
        self.server_id = member.guild.id
        self.channel = None
        self.user = member.name
        self.session_start = datetime.now()+timedelta(hours=1)

    
    def __del__(self):
        session_data = {
            "_id": self.id,
            "server_id": self.server_id,
            "channel": self.channel,
            "user": self.user,
            "start": self.session_start,
            "end": datetime.now() + timedelta(hours=1)
        }

        insert_result = self.mongo.get_collection("sessions").insert_one(session_data)

        if insert_result.inserted_id:
            print(f"{self.user} left {self.channel}")

        self._update_mic_state_end()

    def handle_mic_state(self, mic_state):
        if mic_state == "muted":
            mic_data = {
                "_id": self.id,
                "user": self.user,
                "mic_state": mic_state,
                "start": datetime.now() + timedelta(hours=1),
                "end": None
            }
            self.mongo.get_collection("mic_states").insert_one(mic_data)
            print(f"{self.user} is now muted.")
        elif mic_state == "unmuted":

            update_result = self.mongo.get_collection("mic_states").update_one(
                {
                    "id": self.id,
                    "mic_state": "muted",
                    "end": None
                }, 
                {
                    "$set":
                        {
                            "end": datetime.now() + timedelta(hours=1)
                        }
                }  
            )

            if update_result.modified_count > 0:
                print(f"{self.user} is now unmuted.")
            else:
                print(f"Failed to update mic state for {self.user}, no active mute found.")

    def _update_mic_state_end(self):
        self.mongo.get_collection("mic_states").update_one(
            {"id": self.id,
             "mic_state": "muted",
             "end": None},
            {"$set": {"end": datetime.now() + timedelta(hours=1)}}
        )
        print(f"Mic state for {self.user} has been updated to 'unmuted' as they left.")
    
            
    @staticmethod    
    def calculate_time_spent_in_session(sessions,server_id):
        times_online = {}
        for user in sessions.keys():
            user_session = sessions.get(user)
            if user_session.server_id != server_id:
                continue
            name = user
            start = user_session.session_start
            end = datetime.now()+timedelta(hours=1)
    
            time_spent = end-start
            time_spent = time_spent.total_seconds()
            
            times_online[name] = times_online.get(name, 0) + int(time_spent)
        return times_online


    @staticmethod
    def calculate_time_spent_online(sessions,server_id, username = None):
        mongo = MongoInit()
        times_online = {}
        to_return = {}
       

        if username:
            result = mongo.get_collection("sessions").find({"server_id":server_id,"user" : username})
        else:
            result = mongo.get_collection("sessions").find({"server_id" : server_id})

        for data in result:

            name = data["user"]
            start = data["start"]
            end = data["end"]

            time_spent = end-start
            
            time_spent = time_spent.total_seconds()

            times_online[name] = times_online.get(name, 0) + int(time_spent)
            
            
        session_time = Session.calculate_time_spent_in_session(sessions,server_id)
        
        for key in set(times_online) | set(session_time):
            to_return[key] = times_online.get(key,0) + session_time.get(key,0)

        return to_return
