import streamlit as st
import streamlit_authenticator as stauth
import yaml, json
from pathlib import Path
from datetime import datetime
import pandas as pd
from pytz import timezone
import time as ttime
from google.cloud import firestore
from google.oauth2 import service_account





class App:
    

    st.set_page_config(layout='wide')

    key_dict = json.loads(st.secrets["cool_secret"]["textkey"])
    creds = service_account.Credentials.from_service_account_info(key_dict)
    db = firestore.Client(credentials=creds)

   

    body = ['Timesheet', 'Materials', 'Notes']
    item3 = None
    new_form = False
    p = 0
    total_hours = []
    
    

    

    def read_firestore(self):
        
        
        doc_ref = self.db.collection("JFJ Joinery")
        doc_ref = doc_ref.stream()

    
        jobs = {doc.id:doc.to_dict() for doc in doc_ref}
        return jobs



    def write_to_json(self, text, job):
        
        doc_ref = self.db.collection("JFJ Joinery").document(job)
        

        doc_ref.set(text[job])


    
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
        time = jobs["Other"]["Employee_Variables"][f'{st.session_state["name"]}']
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




    def auth_read(self, config):


        authenticator = stauth.Authenticate(
                    config['credentials'],
                    config['cookie']['name'],
                    config['cookie']['key'],
                    config['cookie']['expiry_days'],
                    config['preauthorized']
                )

        return authenticator

    @st.cache_data
    def convert_df(self, df):
        return df.to_csv().encode('utf-8')

    
    def get_employee_list(self, jobs, job):
        employees = []
        for keys, items in jobs[job]["Employee_Variables"].items():
            employees.append(keys)
        employees.sort()
        return employees

    def update_credentials(self, first, last, email, passw, jobs):
        hashed_password = stauth.Hasher([passw]).generate()
        new = {
                                "email": email,
                                "name": f'{first} {last}',
                                "password": hashed_password[0]
        }
        jobs['config']['credentials']['usernames'][first.lower()] = new
        self.write_to_json(jobs, 'config')

    def shift_search(self, jobs, employee, date_):
        date_ = str(date_).split('-')
        date_ = f'{date_[2]}/{date_[1]}/{date_[0]}'
        total_hours = []
        job_hours = []
        for job in jobs:
            if job == 'Other':
                
                if len(employee) == 1:
                    for shift in jobs[job]['Employee_Variables'][employee[0]]["Total_Hours"]:
                        if shift['Date'] == date_:
                            total_hours.append([[shift['Date'],shift['Check-in'],shift['Check-out'],8]])
                    



    

    def main(self):
        
        jobs = self.read_firestore()
        authenticator = self.auth_read(jobs['config'])
        
        name, authentication_status, username = authenticator.login('Login', 'main')
        


        if authentication_status == None:
            if st.sidebar.button('Register'):
                print('hi')
            if st.sidebar.button('Forgot Password'):
                print('bye')

        if st.session_state["authentication_status"]:
            
            with st.sidebar:
                authenticator.logout('Logout', 'main')
                try:
                    if jobs["Other"]["Employee_Variables"][f"{st.session_state['name']}"]["Auth"] == "Super":
                        
                        with st.sidebar.expander('Create New User', expanded=False):
                            with st.form(key='test9', clear_on_submit=True):
                                
                                fname_ = st.text_input('First Name', key='new_name', value='')
                                lname_ = st.text_input('Last Name', key='new_last', value='')
                                email_ = st.text_input('Email', key='email', value='@')
                                passw_ = st.text_input('Temp Pass', key='pass', value='')
                                autho_ = st.selectbox('User Type', ['Admin','Standard'])


                                submitted1 = st.form_submit_button('Submit')

                                if submitted1:
                                    
                                    new = {"Auth": autho_,
                                            "Break": "False",
                                            "Check-in": "False",
                                            "End": "",
                                            "First_Login": True,
                                            "Start": "",
                                            "Total_Hours": [],
                                            "Shed_Hours": [],
                                            "Form": "False"}
                                    jobs["Other"]["Employee_Variables"][f'{fname_} {lname_}'] = new

                                    self.update_credentials(fname_, lname_, email_, passw_, jobs)                                
                                    self.write_to_json(jobs, "Other")
                        with st.sidebar.expander('Search Timesheets', expanded=False):
                            with st.form(key='test10', clear_on_submit=True):
                                date_s = st.date_input('Date Start',key='date_s')
                                date_e = st.date_input('Date End', key='date_e')
                                emplo_ = st.multiselect('Employee', self.get_employee_list(jobs, 'Other'))
                                search_ = st.form_submit_button(label='Search Timesheet')
                                
                                if search_:
                                    self.shift_search(jobs, emplo_, date_s)
                except:
                    pass
                    
                

            
            st.title(':blue[JFJ Joinery]')
            st.write(f'Welcome *{st.session_state["name"]}*')
            c = st.container()
            hours = self.update_hours_tally(jobs, 1)
            tally = pd.DataFrame(data=[[self.get_current_date(), hours[1], hours[0]]], columns=["Date", "Hours Today","Overtime"])
            with c:
                col1, col2 = st.columns(2)
                with col1:
                    c.dataframe(tally, width=500)
                with col2:
                    check_in = jobs["Other"]["Employee_Variables"][f"{st.session_state['name']}"]
                    if check_in["Check-in"] == "False":
                        dbut = c.button('Start Day')
                        if dbut:
                            check_in["Check-in"] = "True"
                            check_in["Start"] = self.round_time(self.get_current_time())
                            self.write_to_json(jobs, "Other")
                            
                            st.experimental_rerun()

                    elif check_in["Check-in"] == "True":
                        dbut = c.button('End Day')
                        if dbut:
                            for job in jobs:
                                if job == "Other":
                                    pass
                                elif job == 'config':
                                    pass
                                else:
                                    for shift in jobs[job]["Timesheets"]:
                                        if shift["Check-out"] == '':
                                            shift["Check-out"] = self.round_time(self.get_current_time())
                                            self.write_to_json(jobs, job)
                            self.new_form = True
                            time = self.get_current_time()
                            check_in["End"] = self.round_time(self.get_current_time())
                            check_in["Form"] = "Form1"
                    
                            self.write_to_json(jobs, "Other")
                            
                            st.experimental_rerun()
            new_form = jobs["Other"]["Employee_Variables"][f"{st.session_state['name']}"]
            if new_form["Form"] == "Form1":
                
                with st.form("EOD", clear_on_submit=False):
                    
                    hours = self.update_hours_tally(jobs, 2)
                    total = hours[0] + hours[1]
                    st.header(':blue[Break Review]')
                    st.write(f':blue[You have worked] {hours[1]} :blue[hours this shift!]')
                    st.write(":blue[Did you take a Lunch Break today?]")
                    submitted = st.form_submit_button('Yes')
                    submitted2 = st.form_submit_button('No')
                    
                    if submitted:
                        new_form["Form"] = "Form2"
                        new_form["Break"] = "Yes"

                        self.write_to_json(jobs, "Other")
                        
                        st.experimental_rerun()

                    elif submitted2:
                        new_form["Form"] = "Form2"
                        new_form["Break"] = "No"

                        self.write_to_json(jobs, "Other")
                        
                        st.experimental_rerun()


            elif new_form["Form"] == "Form2":
                time_list = self.time_list()
                x = 0

                with st.form("Confirm Hours"):
                    st.header(':blue[Review Job Hours]')
                    st.markdown(':blue[Please review your submitted hours below. Edit as required.]')
                    for job in jobs:
                        if job == 'Other':
                            pass
                        elif job == "config":
                            pass
                        else:
                            for shift in jobs[job]["Timesheets"]:
                                if shift['Date'] == self.get_current_date():
                                    with st.expander(job, expanded=True):
                                        s_ = time_list.index(shift['Check-in'])
                                        try:
                                            e_ = time_list.index(shift['Check-out'])
                                        except:
                                            e_ = time_list.index("00:00")
                                        
                                        st.selectbox('Start Time', options=time_list, index=s_, key=f'form2{x}')
                                        x += 1
                                        st.selectbox('End Time', options=time_list, index=e_,key=f'form2{x}')
                                        x += 1
                                        delete = st.checkbox('Delete', key=f"form2{x}")
                                        x += 1
                                        st.caption('Having the box checked when submitting, will delete your hours from this job')
                                        x += 1
                                        if delete:
                                            st.warning('Are you sure you want to delete?')
                                            choice = st.selectbox(label='a', options=['','Yes', 'No'], index=0, label_visibility='collapsed', key=x)
                                            if choice == 'Yes':
                                                print('asdfasdfasdf')
                                        
                                            

                                        

                    submitted3 = st.form_submit_button('Submit')
                if submitted3:
                    new_form["Form"] = 'Form3'
                    self.write_to_json(jobs, 'Other')
                    st.experimental_rerun()
                    
                        
                            
            elif new_form["Form"] == "Form3":
                with st.form("Adjust Hours"):
                    st.header(":blue[Adjust Total Hours]")
                    st.write(":blue[You can adjust hours here. Otherwise, please]")
                    st.write(":blue[provide a short decscription and click Finish to complete.]")
                    
                    num = st.number_input(label='p', label_visibility='collapsed', key='num')
                    desc = st.text_area(label='p', label_visibility='collapsed', key='desc')
                    submitted = st.form_submit_button("Finish")

                        
                        

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
                        self.write_to_json(jobs, "Other")
                        
                        st.experimental_rerun()
                        

                    

                        
            else:
                pass
            x = 0
            st.header("")
            st.header("")
            current, complete = st.tabs(['Current', 'Complete'])


            with current:
                for job in jobs:
                    if job == 'Other':
                        pass
                    if job == 'config':
                        pass
                    else:
                        
                        try:
                            if jobs[job]["Status"] == "Current":
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
                                                    if jobs[job]["Timesheets"] == []:
                                                        new = {"Name": f"{st.session_state['name']}",
                                                            "Date": f"{self.get_current_date()}",
                                                            "Check-in": f"{str(item3)}",
                                                            "Check-out": ""}
                                                        jobs[job]["Timesheets"].append(new) 
                                                        self.write_to_json(jobs, job)
                                                        test = False
                                            
                                                    elif jobs[job]["Timesheets"][y]["Name"] == f"{st.session_state['name']}":
                                                        if jobs[job]["Timesheets"][y]["Date"] == f'{self.get_current_date()}':
                                                            if jobs[job]["Timesheets"][y]["Check-in"] == '':
                                                                jobs[job]["Timesheets"][y]["Check-in"] = str(item3)
                                                                self.write_to_json(jobs, job)
                                                                test = False
                                                            elif jobs[job]["Timesheets"][y]["Check-out"] == '':
                                                                jobs[job]["Timesheets"][y]["Check-out"] = str(item3)
                                                                self.write_to_json(jobs, job)
                                                                
                                                                
                                                                test = False
                                                            else: 
                                                                y += 1
                                                        else:
                                                            y += 1
     
                                                    else:
                                                        y += 1
                                                    
                                                except:
                                                    new = {"Name": f"{st.session_state['name']}",
                                                        "Date": f"{self.get_current_date()}",
                                                        "Check-in": f"{str(item3)}",
                                                        "Check-out": ""}
                                                    jobs[job]["Timesheets"].append(new) 
                                                    self.write_to_json(jobs, job)
                                                    test = False
                                                    

                                                
                                            

                                        listo = []
                                        for items, values in jobs[job].items():
                                            t = 0

                                            try:
                                                for thing in values:
                                                    new = [thing['Name'], thing['Date'], thing['Check-in'], thing['Check-out']]
                                                    listo.append(new)
                                                
                                            except:
                                                pass
                                        print(listo)
                                        if listo != []:
                                            df = pd.DataFrame(data=listo, columns=['Name', 'Date', 'Check-in', 'Check-out'])
                                            st.dataframe(df, width=1000)
                                        


                                    with n:
                                                
                                        with st.form(f'my_form{x}', clear_on_submit=True):
                                            text = st.text_area(label='Test', label_visibility='collapsed')
                                            submitted = st.form_submit_button("Submit")
                                            x += 1

                                        if submitted:
                                            now = datetime.now()
                                            dt = now.strftime("%d/%m/%Y - %H:%M:%S")
                                            jobs[job]["Notes"][f'{dt} - {st.session_state["name"]}'] = text 
                                            self.write_to_json(jobs, job)
                                            x += 1

                                        notes = []
                                        for keys, values in jobs[job]["Notes"].items():
                                            notes.append(keys)
                                        
                                        notes.sort()
                                        notes.reverse()

                                        for note in notes:

                                            st.text_area(label=note, key=x, value=jobs[job]["Notes"][note], disabled=True)
                                            x += 1
                                            

                                    with m:
    
                                        array = []
                                        
                                        with st.form(f'My_form{x}'):
                                            material = st.selectbox('Material', options=self.material_list(), key=x)
                                            x += 1
                                            quantity = st.number_input('Quantity', key=x)
                                            x += 1

                                            submitted = st.form_submit_button("Submit")
                                        
                                        if submitted:                                                   


                                            item_list = []
                                            for items in jobs[job]["Materials"]:
                                                if material in items["Material"]:
                                                    
                            
                                                    q = float(items["Quantity"])
                                                    
                                                    q += quantity
                                                    
                                                    items["Quantity"] = q
                                                    item_list.append((items["Material"]))
                                                    
                                                    self.write_to_json(jobs, job)
                                                    
                                                
                                            if material not in item_list:
                                                

                                                if quantity == 0:
                                                    pass
                                                else:
                                                    
                                                    new = {
                                                        "Material": f"{material}",
                                                        "Quantity": quantity
                                                    }
                                                    jobs[job]["Materials"].append(new)
                                                    self.write_to_json(jobs, job)
                                            
                                                        
        
                                        for selection in jobs[job]["Materials"]:
                                            
                                            
                                            array.append([selection["Material"], selection["Quantity"]])
                                            

                                            testu = False
                                        if array != []:
                                            df = pd.DataFrame(data=array, columns=["Material", "Quantity"])
                                            hide = """
                                            <style>
                                            .row_heading.level0 {display:none}
                                            .blank {display:none}
                                            </style>"""
                                            st.markdown(hide, unsafe_allow_html=True)
                                            st.dataframe(df, width=500)



                        except:
                            pass




            with complete:
                for job in jobs:

                    if job == 'config':
                        pass
                    if job == 'Other':
                        pass

                    try:
                        if jobs[job]["Status"] == "Complete":
                            with st.expander(job):
                                t, p, n = st.tabs(self.body)
                                with t:
                                    listo = []
                                    for items, values in jobs[job].items():
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


                                                
                                        with st.form(f'my_form{x}', clear_on_submit=True):
                                            text = st.text_area(label='Test', label_visibility='collapsed')
                                            submitted = st.form_submit_button("Submit")
                                            x += 1

                                        if submitted:
                                            now = datetime.now()
                                            dt = now.strftime("%d/%m/%Y - %H:%M:%S")
                                            jobs[job]["Notes"][f'{dt} - {st.session_state["name"]}'] = text 
                                            self.write_to_json(jobs, job)
                                            x += 1

                                        notes = []
                                        for keys, values in jobs[job]["Notes"].items():
                                            notes.append(keys)
                                        
                                        notes.sort()
                                        notes.reverse()

                                        for note in notes:

                                            st.text_area(label=note, key=x, value=jobs[job]["Notes"][note], disabled=True)
                                            x += 1
                                        
                    except:
                        pass



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