import streamlit as st
import streamlit_authenticator as stauth
import yaml, time, json
from pathlib import Path
from datetime import datetime
import pandas as pd
from pytz import timezone
import time as ttime




class App:
    
    st.set_page_config(layout='wide')


    body = ['Timesheet', 'Materials', 'Notes']
    item3 = None
    new_form = False
    p = 0
    total_hours = []



    def write_to_json(self, text):
        text = json.dumps(text, indent=4)
        with open ('./WorkSheets/jobs.json', 'w') as outfile:
            outfile.write(text)


    def read_json(self):
        if Path('./WorkSheets/jobs.json').is_file():
            with open('./WorkSheets/jobs.json', 'r') as openfile:
                jobs = json.load(openfile)
        return jobs

    
    def time_list(self):
        times = [
            '00:00','00:15','00:30','00:45',
            '01:00','01:15','01:30','01:45',
            '02:00','02:15','02:30','02:45',
            '03:00','03:15','03:30','03:45',
            '04:00','04:15','04:30','04:45',
            '05:00','05:15','05:30','05:45',
            '06:00','06:15','06:30','06:45',
            '07:00','07:15','07:30','07:45',
            '08:00','08:15','08:30','08:45',
            '09:00','09:15','09:30','09:45',
            '10:00','10:15','10:30','10:45',
            '11:00','11:15','11:30','11:45',
            '12:00','12:15','12:30','12:45',
            '13:00','13:15','13:30','13:45',
            '14:00','14:15','14:30','14:45',
            '15:00','15:15','15:30','15:45',
            '16:00','16:15','16:30','16:45',
            '17:00','17:15','17:30','17:45',
            '18:00','18:15','18:30','18:45',
            '19:00','19:15','19:30','19:45',
            '20:00','20:15','20:30','20:45',
            '21:00','21:15','21:30','21:45',
            '22:00','22:15','22:30','22:45',
            '23:00','23:15','23:30','23:45',
        ]
        
        return times[::-1]


    def update_hours_tally(self, jobs, type):
        hour_list = []
        time = jobs["Other"][1]["Employee_Variables"][f'{st.session_state["name"]}']
        if type == 1:
            for punches in time["Total_Hours"]:
                if punches["Date"] == self.get_current_date():
                    checkin = self.convert_to_int(punches["Check-in"])
                    checkout = self.convert_to_int(punches["Check-out"])
                    if punches["Break"] == 'Yes':
                        break_ = 0.5
                    else:
                        break_ = 0
                    value = checkout - checkin - break_
                    hour_list.append(value)


            try:
                checkin_ = self.convert_to_int(time["Start"])
                checkout_ = self.convert_to_int(self.get_current_time())
                value_ = checkout_ - checkin_
                hour_list.append(value_)
            except:
                pass

        if type == 2:
            checkin = self.convert_to_int(time["Start"])
            checkout = self.convert_to_int(time["End"])
            hours = checkout - checkin
            
            

        if type == 1:      
            hours = 0
            for ele in range(0, len(hour_list)):
                hours = hours + hour_list[ele]
                hours = round(hours, 1)

        try:
            if hours > 8:
                OT = hours - 8


            else:

                OT = 0
        except:
            hours = 0
            OT = 0

        return OT, hours


    def material_list(self):
        materials = [
            'Whiteboard (Full Sheet)',
            'Whiteboard (Half Sheet)',
            'Swift Drawer D=500, H=172mm',
            'Hinges',
            'Hing Plates',

        ]
        return materials

    def get_current_date(self):
        date = datetime.today()
        date = date.strftime("%d/%m/%Y")
        return date

    def convert_date(self, date):
        date = str(date).split('/')
        date = f"{date[2]}/{date[1]}/{date[0]}"
        return date


    def get_current_time(self):
        tz = timezone('Australia/Victoria')
        time = datetime.now(tz)
        time = str(time).split(' ')
        time = time[1].split(':')
        time = f'{time[0]}:{time[1]}'
        return time

    def round_hours(self, hours):
        hours = round(float(hours),1)
        return hours

    def convert_to_int(self, value):
        h, m = value.split(":")
        m = int(m) / 60
        value = int(h) + m
        
        return value

    def convert_to_time(self, value):
        h, m = str(value).split('.')
        m = f"0.{m}"
        m = float(m) * 60
        m = round(m)
        if len(str(m)) == 1:
            m = f'0{m}'
        time_ = f'{h}:{m}'
        
        return time_


    def round_time(self, time):
        h, m = time.split(":")
        m = self.myround(int(m))
        h = int(h)
        if m == 60:
            m = 0
            h += 1
        if m == 0:
            m = '00'
        else:
            m = str(m)
        time = f'{h}:{m}'
      
        return time


    def myround(self, x, base=15):
        return base * round(x/base)




    def auth_read(self):
        if Path('./WorkSheets/config.yaml').is_file():
            with open('./WorkSheets/config.yaml') as file:
                config = yaml.load(file, Loader=yaml.FullLoader)

                authenticator = stauth.Authenticate(
                    config['credentials'],
                    config['cookie']['name'],
                    config['cookie']['key'],
                    config['cookie']['expiry_days'],
                    config['preauthorized']
                )

        return authenticator

    

    def main(self):
        authenticator = self.auth_read()
        jobs = self.read_json()
        name, authentication_status, username = authenticator.login('Login', 'main')


        if authentication_status == None:
            if st.sidebar.button('Register'):
                print('hi')
            if st.sidebar.button('Forgot Password'):
                print('bye')

        if st.session_state["authentication_status"]:
            
            with st.sidebar:
                authenticator.logout('Logout', 'main')

            
            st.title('JFJ Joinery')
            st.write(f'Welcome *{st.session_state["name"]}*')
            c = st.container()
            hours = self.update_hours_tally(jobs, 1)
            tally = pd.DataFrame(data=[[self.get_current_date(), hours[1], hours[0]]], columns=["Date", "Hours Today","Overtime"])
            with c:
                col1, col2 = st.columns(2)
                with col1:
                    c.dataframe(tally, width=500)
                with col2:
                    check_in = jobs["Other"][1]["Employee_Variables"][f"{st.session_state['name']}"]
                    if check_in["Check-in"] == "False":
                        dbut = c.button('Start Day')
                        if dbut:
                            check_in["Check-in"] = "True"
                            check_in["Start"] = self.round_time(self.get_current_time())
                            self.write_to_json(jobs)
                            st.experimental_rerun()

                    elif check_in["Check-in"] == "True":
                        dbut = c.button('End Day')
                        if dbut:
                            self.new_form = True
                            time = self.get_current_time()
                            check_in["End"] = self.round_time(self.get_current_time())
                            check_in["Form"] = "Form1"
                    
                            self.write_to_json(jobs)
                            st.experimental_rerun()
            new_form = jobs["Other"][1]["Employee_Variables"][f"{st.session_state['name']}"]
            if new_form["Form"] == "Form1":
                
                with st.form("EOD", clear_on_submit=False):
                    
                    hours = self.update_hours_tally(jobs, 2)
                    total = hours[0] + hours[1]
                    st.write(f'You have worked {hours[1]} hours this shift!')
                    st.write("Did you take a Lunch Break today?")
                    submitted = st.form_submit_button('Yes')
                    submitted2 = st.form_submit_button('No')
                    
                    if submitted:
                        new_form["Form"] = "Form2"
                        new_form["Break"] = "Yes"

                        self.write_to_json(jobs)
                        st.experimental_rerun()

                    elif submitted2:
                        new_form["Form"] = "Form2"
                        new_form["Break"] = "No"

                        self.write_to_json(jobs)
                        st.experimental_rerun()


            elif new_form["Form"] == "Form2":

                with st.form("Adjust Hours"):
                    st.write("You can adjust hours here. Otherwise, please.")
                    st.write("provide a short decscription and click Finish to complete.")
                    submitted = st.form_submit_button("Finish")
                    num = st.number_input(label='p', label_visibility='collapsed', key='num')
                    desc = st.text_area(label='p', label_visibility='collapsed', key='desc')

                        
                        

                    if submitted:
                        
                        value = self.convert_to_int(new_form["End"])
                        
                        value = value + num
                        
                        value = self.convert_to_time(value)
                        


                        new = {"Date": f"{self.get_current_date()}",
                               "Check-in": f"{new_form['Start']}",
                               "Check-out": f"{value}",
                               "Break": f"{new_form['Break']}",
                               "Amend": f"{num}",
                               "Description": f"{desc}"}

                        new_form["Total_Hours"].append(new)

                        new_form["Start"] = ''
                        new_form["End"] = ''
                        new_form['Break'] = 'False'                                                   
                        new_form["Check-in"] = 'False'
                        new_form["Form"] = 'False'
                        self.write_to_json(jobs)
                        st.experimental_rerun()
                        

                    

                        
            else:
                pass
            x = 0
            current, complete = st.tabs(['Current', 'Complete'])


            with current:
                for job in jobs:
                    if job == 'Other':
                        pass
                    else:
                        if jobs[job][0] == "Current":
                            with st.expander(job):
                                t, m, n = st.tabs(self.body)

                                with t:

                                    with st.form(f"My Form {x}", clear_on_submit=False):
                                        col1, col2, col3, col0 = st.columns(4)

                                        with col1:

                                            item1 = st.text_input('Name', key=x, value=st.session_state["name"], disabled=True)
                                            
                                            x += 1

                                        with col2:
                                            item2 = st.date_input('Date', key=x)
                                            x += 1

                                        with col3:
                                            
                                            item3 = st.selectbox('Time', options=self.time_list(), key=x)
                                            x += 1


                                        with col0:
                                            pass

                                        submitted = st.form_submit_button('Submit')



                                    if submitted:
                                        y = 0
                                        
                                        
                                        test = True

                                        while test:

                                            try:
                                                if jobs[job][2]["Timesheets"] == []:
                                                    new = {"Name": f"{st.session_state['name']}",
                                                        "Date": f"{self.get_current_date()}",
                                                        "Check-in": f"{str(item3)}",
                                                        "Check-out": ""}
                                                    jobs[job][2]["Timesheets"].append(new) 
                                                    self.write_to_json(jobs)
                                                    test = False
                                        
                                                elif jobs[job][2]["Timesheets"][y]["Name"] == f"{st.session_state['name']}":
                                                    if jobs[job][2]["Timesheets"][y]["Date"] == f'{self.get_current_date()}':
                                                        if jobs[job][2]["Timesheets"][y]["Check-in"] == '':
                                                            jobs[job][2]["Timesheets"][y]["Check-in"] = str(item3)
                                                            self.write_to_json(jobs)
                                                            test = False
                                                        elif jobs[job][2]["Timesheets"][y]["Check-out"] == '':
                                                            jobs[job][2]["Timesheets"][y]["Check-out"] = str(item3)
                                                            self.write_to_json(jobs)
                                                            
                                                            print('test')
                                                            test = False
                                                        else: 
                                                            y += 1
                                                        
                                                        
                                                else:
                                                    y += 1
                                            except:
                                                new = {"Name": f"{st.session_state['name']}",
                                                    "Date": f"{self.get_current_date()}",
                                                    "Check-in": f"{str(item3)}",
                                                    "Check-out": ""}
                                                jobs[job][2]["Timesheets"].append(new) 
                                                self.write_to_json(jobs)
                                                test = False
                                                print('test2')

                                            
                                        

                                    listo = []
                                    for items, values in jobs[job][2].items():
                                        t = 0

                                        try:
                                            for thing in values:
                                                new = [thing['Name'], thing['Date'], thing['Check-in'], thing['Check-out']]
                                                listo.append(new)
                                            
                                        except:
                                            pass
                                    if listo != []:
                                        df = pd.DataFrame(data=listo, columns=['Name', 'Date', 'Check-in', 'Check-out'])
                                        st.dataframe(df, width=1000)
                                    


                                with n:
                                    y = 1
                                    z = 0


                                    while jobs[job][z] == "Current":

                                        try:
                                            for keys, values in jobs[job][y]["Notes"].items():

                                                st.text_area(label=keys, key=x, value=values, disabled=True)
                                                x += 1

                                            y += 1

                                        except:
                                            z += 1


                                            
                                    with st.form(f'my_form{x}', clear_on_submit=True):
                                        text = st.text_area(label='Test', label_visibility='collapsed')
                                        submitted = st.form_submit_button("Submit")
                                        x += 1

                                    if submitted:
                                        now = datetime.now()
                                        dt = now.strftime("%d/%m/%Y - %H:%M:%S")
                                        jobs[job][1]["Notes"][f'{st.session_state["name"]} - {dt}'] = text 
                                        self.write_to_json(jobs)
                                        st.text_area(label=f'{st.session_state["name"]} {dt}', value=text, key=x)
                                        x += 1
                                        st.experimental_rerun()

                                with m:
                                    y = 3
                                    z = 0

                                    array = []

                                    while jobs[job][z] == "Current":
                                        
                                        try:
                                            if jobs[job][y]["Materials"] != []:
                                                for selection in jobs[job][y]["Materials"]:
                                                    array.append([selection["Material"], int(selection["Quantity"])])
                                                    
                                                   
                                                
                                                y += 1
                                            else:
                                                y += 1
                                        except:
                                            z += 1
                                            
                                            
                                    

                                    with st.form(f'My_form{x}'):
                                        material = st.selectbox('Material', options=self.material_list(), key=x)
                                        x += 1
                                        quantity = st.number_input('Quantity', key=x)
                                        x += 1

                                        submitted = st.form_submit_button("Submit")
                                    
                                    if submitted:
                                        if jobs[job][3]["Materials"] == []:
                                            if quantity == 0:
                                                pass
                                            else:
                                                new = {
                                                            "Material": f"{material}",
                                                            "Quantity": quantity
                                                        }

                                                jobs[job][3]["Materials"].append(new)
                                                self.write_to_json(jobs)
                                                st.experimental_rerun()
                                        item_list = []
                                        for items in jobs[job][3]["Materials"]:
                                            if material in items["Material"]:
                                                                        
                                                q = float(items["Quantity"])
                                                q += quantity
                                                items["Quantity"] = q
                                                item_list.append(str(items["Material"]))
                                                self.write_to_json(jobs)
                                                st.experimental_rerun()
                                            
                                        if material not in item_list:
                                            

                                            if quantity == 0:
                                                pass
                                            else:
                                                new = {
                                                    "Material": f"{material}",
                                                    "Quantity": quantity
                                                }
                                                jobs[job][3]["Materials"].append(new)
                                                self.write_to_json(jobs)
                                                st.experimental_rerun()
                                            


                                    if array != []:
                                        df = pd.DataFrame(data=array, columns=["Material", "Quantity"])
                                        st.dataframe(df, width=500)

                                

                                

            




            with complete:
                for job in jobs:
                    if jobs[job][0] == "Complete":
                        with st.expander(job):
                            t, p, n = st.tabs(self.body)
                            with t:
                                col0, col1, col2, col3, col4 = st.columns(5)

                                with col0:

                                    try:
                                        y=2
                                        z=0

                                        while jobs[job][z] == "Complete":

                                            try: 
                                                st.text_input('p', key=x, value=jobs[job][y][3], disabled= True, label_visibility='collapsed')
                                                x += 1
                                                y += 1

                                            except:
                                                z += 1

                                    except:
                                        pass

                                with col1:

                                    try:
                                        y = 2
                                        z = 0

                                        while jobs[job][z] == "Complete":

                                            try: 
                                                st.text_input('p', key=x, value=jobs[job][y][0], disabled=True, label_visibility='collapsed')
                                                x += 1
                                                y += 1

                                            except:
                                                z += 1

                                    except:
                                        pass
                                    
                                with col2:

                                    try:
                                        y = 2
                                        z = 0

                                        while jobs[job][z] == "Complete":

                                            try: 
                                                st.text_input('p', key=x, value=jobs[job][y][1], disabled=True, label_visibility='collapsed')
                                                x += 1
                                                y += 1

                                            except:
                                                z += 1

                                    except:
                                        pass
                                    

                                with col3:

                                    try:
                                        y = 2
                                        z = 0

                                        while jobs[job][z] == "Complete":

                                            try: 
                                                st.text_input('p', key=x, value=jobs[job][y][2], disabled=True, label_visibility='collapsed')
                                                x += 1
                                                y += 1

                                            except:
                                                z += 1

                                    except:
                                        pass

                                with col4:

                                    y = 2
                                    z = 0 

                                    while jobs[job][z] == "Complete":

                                        try:
                                            if jobs[job][1][y][2]:
                                                pass
                                            with st.container():
                                                st.button('Edit')
                        
                                            x += 1
                                            y += 1
                                        except:
                                            z += 1


                                listo = []
                                for items, values in jobs[job][2].items():
                                    t = 0

                                    try:
                                        for thing in values:
                                            new = [thing['Name'], thing['Date'], thing['Check-in'], thing['Check-out']]
                                            listo.append(new)
                                        
                                    except:
                                        pass
                                if listo != []:
                                    df = pd.DataFrame(data=listo, columns=['Name', 'Date', 'Check-in', 'Check-out'])
                                    st.dataframe(df, width=1000)
                            with n:
                                            
                                y = 1
                                z = 0
                                a = 0

                                while jobs[job][z] == "Complete":


                                    try:
                                        for keys, values in jobs[job][y]["Notes"].items():


                                            st.text_area(label=keys, key=x, value=values, disabled=True)
                                            x += 1

                                        y += 1

                                    except:
                                        z += 1


                                        
                                with st.form(f'my_form{x}', clear_on_submit=True):
                                    text = st.text_area(label='Test', label_visibility='collapsed')
                                    submitted = st.form_submit_button("Submit")
                                    x += 1

                                if submitted:
                                    now = datetime.now()
                                    dt = now.strftime("%d/%m/%Y %H:%M:%S")
                                    jobs[job][1]["Notes"][f'{st.session_state["name"]} - {dt}'] = text 
                                    self.write_to_json(jobs)
                                    st.experimental_rerun()


        elif st.session_state["authentication_status"] is False:
            st.error('Username/password is incorrect')
            st.warning('Reset Password?')
        elif st.session_state["authentication_status"] is None:
            st.warning('Please enter your username and password')


        if authentication_status is False:
            try:
                if authenticator.reset_password(username, 'Reset password', 'main'):
                    st.success('Passord successfully changed!')
            except Exception as e:
                st.error(e)



App().main()