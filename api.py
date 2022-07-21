from random import sample
import re
import flask
import json 
from flask import jsonify,request,render_template
from namedlist import namedlist
app = flask.Flask(__name__)
app.config["DEBUG"] = True
import sqlite3
from datetime import datetime


f = open('sample.json')
  

data = json.load(f)

def string_to_datetime(date_time_str):
    # date_time_str = '18-09-19'
    date_time_obj = datetime.strptime(date_time_str,'%d-%m-%Y')
    # print("the date is actually !!!!!!!!!!!!!!!",date_time_obj)
    return date_time_obj
def change_format(input):
    #print(input,type(input))
    return datetime.strftime(input, "%d-%m-%Y")

# print ("The type of the date is now",  type(date_time_obj))
# print ("The date is", date_time_obj)





def check_for_validity(string_email):
            for user_data_key in data.keys():
                if user_data_key == string_email:
                    return True
            return False

# def data_to_list(data):
#     emp_list=[]
#     for emp in data:
#         emp_list.append(data.keys())

#     print(emp_list)







# data_to_list(data)

@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')
@app.route('/sample', methods=['GET','POST'])
def sample():
    sample_json={
        "email":"sample@example.com",
        "from":"17-08-2018",
        "to":"20-09-2019",
        "profile":"lorem_ipsum",
    }
    return jsonify(sample_json)

@app.route('/api/all', methods=['GET'])
def api_all():
    return jsonify(data)


@app.route('/api/employee', methods=['GET','POST','DELETE','PUT','PATCH'])
def api_id():
    def Helper_Function(employee_data, req_data):
        Range = namedlist('Range', ['start', 'end','profile'])
        dates = []
        lis= []
        for user in employee_data:
            temp = [string_to_datetime(user['from']),string_to_datetime(user['to']) , user['profile']]
            dates.append(temp)
        
        query_2 = Range(start=req_data[0], end=req_data[1], profile = req_data[2])
        user = 0

        while user <  len(dates):

            query_1 = Range(start=dates[user][0], end=dates[user][1],profile = dates[user][2])
            
            if overlap(query_1,query_2)  == 0 and query_2.end<query_1.start:
                lis.append([query_2.start, query_2.end, query_2.profile])
                break
            elif overlap(query_1,query_2) == 0:
                
                lis.append([query_1.start, query_1.end, query_1.profile])
                user=user+1
                if user == len(dates):
                    lis.append([query_2.start,query_2.end,query_2.profile])
                    break
                continue

            if min(query_2.start, query_1.start) == query_2.start:
                lis.append([query_2.start, query_1.start, query_2.profile])
                query_2.start = query_1.start
            else:
                lis.append([query_1.start, query_2.start, query_1.profile])
                query_1.start = query_2.start


            if min(query_2.end, query_1.end) == query_2.end:
                lis.append([query_2.start, query_2.end, query_2.profile])
                query_2.start = query_2.end
                query_1.start =query_2.end
                lis.append([query_1.start, query_1.end, query_1.profile])
                query_1.start = query_1.end
                user=user+1
                break
                
            else:
                lis.append([query_2.start, query_1.end, query_2.profile])
                query_2.start = query_1.end
                query_1.start = query_1.end
                if user == len(dates)-1:
                    lis.append([query_2.start, query_2.end, query_2.profile])
                    query_2.start = query_2.end
                    user=user+1
                    break
                else:
                    user = user+1
        while user<len(dates):
            temp = dates[user]
            lis.append(temp)
            user = user+1


        count = 1
        prev_date_from = lis[0][0]
        prev_date_to = lis[0][1]
        prev_policy = lis[0][2]
        while count<len(lis):
            curr_date_from = lis[count][0]
            curr_date_to = lis[count][1]
            curr_policy = lis[count][2]
            if curr_date_from == curr_date_to:
                lis.remove(lis[count])
                continue
            if curr_policy == prev_policy and prev_date_to == curr_date_from:
                lis.remove(lis[count])
                lis.remove(lis[count-1])
                temp = [prev_date_from ,curr_date_to , curr_policy]
                lis.insert(count-1, temp)
                prev_date_from = prev_date_from
                prev_date_to = curr_date_to
                prev_policy = curr_policy
                continue
            
            prev_date_from =curr_date_from
            prev_date_to = curr_date_to
            prev_policy = curr_policy
            count=count+1
        
        return_dict  = []
        for date_from, date_to, profile in lis:
            dict = {'from':change_format(date_from) ,'to':change_format(date_to), 'profile':profile}
            return_dict.append(dict)
        
        return return_dict

    def overlap(query_1, query_2):
        latest_start = max(query_1.start, query_2.start)
        earliest_end = min(query_1.end, query_2.end)
        max_param = (earliest_end - latest_start).days + 1
        overlap = max(0, max_param)
        return overlap


    if request.method =='GET':
        # print(request.args)   
        

        if 'email' in request.args and check_for_validity(str(request.args['email']))==False:
            return "user does not exist"


        elif 'email' in request.args and 'date_of_query' not in request.args:
            email = str(request.args['email'])


    # Create an empty list for our results
            results = []
            # print(data,'this is data')
            # Loop through the data and match results that fit the requested ID.
            # IDs are unique, but other fields might return many results
            for user_data_key in data.keys():
                if user_data_key == email:
                    results.append(data[user_data_key])
            return jsonify(results)

        elif 'email' in request.args and 'date_of_query' in request.args:
            # print("recieved email and date")   this works !!
            string_date=request.args['date_of_query']
            # print(string_date)
            email = str(request.args['email'])
            # print(string_date)

            date_of_query_obj= string_to_datetime(string_date)
            
            print(date_of_query_obj,"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            # print(data)
            for user_data_key in data.keys():
                if user_data_key==email:
                    for temp_data in data[user_data_key]:
                        from_date_obj=string_to_datetime(temp_data['from'])
                        to_date_obj=string_to_datetime(temp_data['to'])
                        
                        if date_of_query_obj <to_date_obj and date_of_query_obj>from_date_obj:
                            return temp_data['profile']
                    return "no profiles assigned to user for this date"
                        
                        # print(temp_data['from'])
                    # print(data[user_data_key])
        elif 'email' not in request.args:
            print("no user id given ")
            return 'no user id provided'

                    

            # return "date and email"
        

    elif request.method =='POST':
        return 'post request recieved'

    elif request.method =='PUT':
        print('update request recieved')


        put_data=request.get_json()
        # print(put_data)

        employee_email=put_data['email']
        from_date_obj= string_to_datetime(put_data['from'])
        to_date_obj=string_to_datetime(put_data['to'])
        employee_profile=put_data['profile']


        if to_date_obj<from_date_obj:
            return "invalid date responses"
        if check_for_validity(str(employee_email)) is False:
            print('user does not exist insisde this json file')
            # data.append()
            temp_dict={
                "from": put_data['from'],
                "to": put_data['to'],
                "profile": put_data['profile']
            }
            data[employee_email]=[temp_dict]
            # print(data)
            with open("sample.json", "w") as outfile:
                        json.dump(data, outfile)
            
            return "new employee added"

        employee_data = data[employee_email]   
        updated_json = Helper_Function(employee_data, [from_date_obj,to_date_obj,employee_profile])
        data[employee_email] = updated_json
        print(data)
        json_object = json.dumps(data, indent=4)
        with open("sample.json", "w") as outfile:
            outfile.write(json_object)
        return jsonify(data)

app.run()