import requests,json
from flask import Flask,render_template,flash,request
import redis,time
from flask import jsonify
from elasticsearch import Elasticsearch
import continuous_threading as ct
from flask_cors import CORS


app=Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
CORS(app)

es=Elasticsearch(['http://3.7.248.72:9200'])

    
app.config.update(
    result_backend='redis://localhost:6379',
    CELERY_BROKER_URL='redis://localhost:6379'
)


    
class guddi_conn(object):
    def __init__(self,flock_url,minute_url,red_url) -> None:
        self.redis_url=red_url
        self.scrape_interval=300
        self.flock=flock_url
        self.minute=minute_url
        self.red_conn=redis.StrictRedis("localhost",6379,charset="UTF-8",decode_responses=True)
    def redis_pub(self):
        gc=guddi_conn("https://api.flock.com/hooks/sendMessage/f6606da6-0e49-4d5b-a6d8-50a7a64ac2e9","https://api.minut.com/v7/devices/63d8fc1723b3757850e4df21/sound_level?time_resolution=300","http://127.0.0.1:8082/")
        resp=str(gc.get_minute())
        resp=json.loads(resp)
        ##print(resp)
        for val in resp["values"]:
            ##print(f"pub-red-val:     {val}")
            if val["value"]>60:
                ##print("Published")
                db_val=val["value"]
                gc.flock_update(f"Noise more than 50db detected : {db_val}")
    def redis_sub(self):
        ##print("Subscribed")
        sub=self.red_conn.pubsub().subscribe("db_high")
        for msg in sub.listen():
            if msg is not None and isinstance(msg,dict):
                db_val=msg.get('data')
                ##print(f"Sub:        {db_val}")
                self.flock_update(f"Noise more than 50db detected : {db_val}")
    def oper_thread(self):
        while 1:
            self.redis_pub()
            time.sleep(1)
    def oper_thread_sub(self):
        while 1:
            self.redis_sub()   
            time.sleep(1)    
    def daemon_thread(self):
        th=ct.Thread(target=self.oper_thread)
        th.start()
        time.sleep(5)
        th1=ct.Thread(target=self.redis_pub)
        th1.start()
        time.sleep(5)
        ct.shutdown(0)
    def flock_update(self,update):
        url = self.flock
        payload = json.dumps({
            "text": update
        })
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        ##print(response.text)
    def get_minute(self):
        url=self.minute
        payload={}
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiI2Mzk5OWNlMWU5NzcxYzhlYmI2ZGU0NDAiLCJjbGllbnRJZCI6IjQyZDlhYTQ2ZTFlYTI4NDQiLCJyb2xlcyI6WyJvcmdhbml6YXRpb24tbWlncmF0ZWQiXSwicmVmcmVzaFRva2VuSWQiOiI2NDZjNzI2YmUwNzQxMzNlYTU2ZWFjMmYiLCJtaW5pbXVtQXBpVmVyc2lvbiI6OCwiaWF0IjoxNjg0ODI4Nzc5LCJleHAiOjE2ODQ4MzIzNzksImlzcyI6Ik1pbnV0LCBJbmMuIn0.Fh-fC--004x0tAdYDgxGBGvMb48_3-6O-WV7lpjbveo'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        ###print(response.text)
        return response.text



@app.route("/",methods=["POST"])
def index():
    gc=guddi_conn("https://api.flock.com/hooks/sendMessage/f6606da6-0e49-4d5b-a6d8-50a7a64ac2e9","https://api.minut.com/v7/devices/63d8fc1723b3757850e4df21/sound_level?time_resolution=300","http://127.0.0.1:8082/")
    gc.daemon_thread()
    return "done"


@app.route("/analysis",methods=["GET"])
def analysis():
    st=request.args.get("st")
    et=request.args.get("et")
    gc=guddi_conn("https://api.flock.com/hooks/sendMessage/f6606da6-0e49-4d5b-a6d8-50a7a64ac2e9","https://api.minut.com/v7/devices/63d8fc1723b3757850e4df21/sound_level?time_resolution=300","http://127.0.0.1:8082/")
    resp=str(gc.get_minute())
    ###print(resp)
    resp=json.loads(resp)
    print(resp["time_resolution"])
    data=resp["values"]
    mx=0
    sum_d,avg_d,med_d=0,0.0,0.0
    data_req=[]
    flag=False
    for x in range(len(data)):
      #  mx=max(mx,round(data[x]['value'],2))
        data[x]['value']=round(data[x]['value'],2)
        data[x]['datetime']=str(data[x]['datetime']).split("-")[2]+"."+str(data[x]['datetime']).split("-")[1]
        if(data[x]['datetime']==st):
            flag=True
        if flag==True:
            mx=max(mx,round(data[x]['value'],2))
            sum_d+=round(data[x]['value'],2)
            data_req.append(round(data[x]['value'],2))
        if(data[x]['datetime']==et):
            break
    t_d_req=data_req
    data_req.sort()
    if len(data_req)%2==1:
        med_d=data_req[int(len(data_req)/2)]
    else:
        med_d=round((data_req[int(len(data_req)/2)]+data_req[int(len(data_req)/2)-1])/2,2)
    data_req=t_d_req
    avg_d=sum_d/len(data_req)
    return jsonify({"mxdata":mx,"meand":avg_d,"datar":data_req,"med_data":med_d})
    

@app.route("/dashboard",methods=["GET"])
def dashboard():
    gc=guddi_conn("https://api.flock.com/hooks/sendMessage/f6606da6-0e49-4d5b-a6d8-50a7a64ac2e9","https://api.minut.com/v7/devices/63d8fc1723b3757850e4df21/sound_level?time_resolution=300","http://127.0.0.1:8082/")
    resp=str(gc.get_minute())
    resp=json.loads(resp)
    ###print(resp)
    data=resp["values"]
    ##print(type(data[0]))
    mx=0
    for x in range(len(data)):
        mx=max(mx,round(data[x]['value'],2))
        data[x]['value']=round(data[x]['value'],2)
        data[x]['datetime']=str(data[x]['datetime']).split("-")[2]+"."+str(data[x]['datetime']).split("-")[1]
    flash(f"The maximum decible till now reached is {mx}")
    return render_template("dashboard.html",data_d=[x for x in data],lend=len(data))

@app.route("/update",methods=["GET"])
def update():
    gc=guddi_conn("https://api.flock.com/hooks/sendMessage/f6606da6-0e49-4d5b-a6d8-50a7a64ac2e9","https://api.minut.com/v7/devices/63d8fc1723b3757850e4df21/sound_level?time_resolution=300","http://127.0.0.1:8082/")
    gc.redis_pub()
    time.sleep(1000)
    gc.redis_sub()

if __name__=="__main__":
    ###print(es.info())
    app.run("0.0.0.0",8088,debug=False)
   # res.wait()