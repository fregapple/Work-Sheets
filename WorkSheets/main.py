import streamlit as st
import streamlit_authenticator as stauth
import yaml, time, json
from pathlib import Path
from datetime import datetime
import pandas as pd

class App:
    
    st.set_page_config(layout='wide')


    body = ['Timesheet', 'Materials', 'Notes']
    item3 = None
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


    def get_total_hours(self, jobs):
        hours_list = []
        for job in jobs:
            for item in jobs[job][2]["Timesheets"]:
                if item["Date"] == self.get_current_date():
                    if item["Check-out"] == '':
                        b = '0'
                    else:
                        a = item["Check-in"].split(':')
                        b = item["Check-out"].split(':')
                        hours = (int(b[0]) + (int(b[1]) / 60)) - (int(a[0]) + (int(a[1]) / 60)) - 0.5
                        hours_list.append(hours)
        total = 0
        for ele in range(0, len(hours_list)):
            total = total + hours_list[ele]

        if total > 8:
            OT = total - 8
            base = 8
        else:
            OT = 0
            base = total

        return OT, base

    def get_current_date(self):
        date = datetime.today()
        date = date.strftime("%d/%m/%Y")
        return date


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
            hours = self.get_total_hours(jobs)
            tally = pd.DataFrame(data=[[self.get_current_date(), hours[1], hours[0]]], columns=["Date", "Hours Today","Overtime"])
            with c:
                col1, col2 = st.columns(2)
                with col1:
                    c.dataframe(tally, width=500)
                with col2:
                    c.button('End of Day')
            x = 0
            current, complete = st.tabs(['Current', 'Complete'])

            font_ = """
            <style>
            button[data-baseweb="tab"] > div[data-testid="stMarkdownContainer"] > p {
                font-size: 24px;
            }
            </style>
            """
            with current:
                for job in jobs:
                    if jobs[job][0] == "Current":
                        with st.expander(job):
                            t, m, n = st.tabs(self.body)

                            with t:

                                with st.form(f"My Form {x}", clear_on_submit=False):
                                    col1, col2, col3, col0 = st.columns(4)

                                    with col1:
                                        try:
                                            
                                            if jobs[job][2]["Timesheets"][f'{st.session_state["name"]} - {self.get_current_date()}']:
                                                item1 = st.text_input('Name', key=x, value=st.session_state["name"], disabled=True)
                                        except:
                                            item1 = st.text_input('Name', key=x, value=st.session_state["name"], disabled=True)
                                        
                                        x += 1

                                    with col2:
                                        item2 = st.date_input('Date', key=x)
                                        x += 1

                                    with col3:
                                        if jobs[job][2]["Timesheets"] == []:
                                            
                                            self.item3 = st.time_input('Started', key=x)
                                            x += 1
                                        else: 
                                            y=0
                                            z = 0
                                            test = True
                                            while test:
                                                try:
                                                    if jobs[job][2]["Timesheets"][y]["Name"] == f"{st.session_state['name']}":
                                                        if jobs[job][2]["Timesheets"][y]["Date"] == f'{self.get_current_date()}':
                                                            if jobs[job][2]["Timesheets"][y]["Check-in"] == '':
                                                                self.item3 = st.time_input('Starti', key=x)
                                                                x += 1
                                                                y += 1
                                                                test = False
                                                                
                                                            elif jobs[job][2]["Timesheets"][y]["Check-out"] == '':
                                                                self.item3 = st.time_input('Endi', key=x)
                                                                x += 1
                                                                y += 1
                                                                test = False
                                                                

                                                            else:
                                                                y += 1
                                                                
                                                        
                                                        else:
                                                            y += 1

                                                    else:
                                                        y += 1
                                                except:
                                                    self.item3 = st.time_input('Started', key=x)
                                                    x += 1
                                                    test = False


                                    with col0:
                                        pass

                                    submitted = st.form_submit_button('Submit')
                                
                                if submitted:
                                    y = 0
                                    value = self.item3


                                    test = True

                                    while test:

                                        try:
                                            if jobs[job][2]["Timesheets"] == []:
                                                new = {"Name": f"{st.session_state['name']}",
                                                    "Date": f"{self.get_current_date()}",
                                                    "Check-in": f"{str(value)}",
                                                    "Check-out": ""}
                                                jobs[job][2]["Timesheets"].append(new) 
                                                self.write_to_json(jobs)
                                                test = False
                                    
                                            elif jobs[job][2]["Timesheets"][y]["Name"] == f"{st.session_state['name']}":
                                                if jobs[job][2]["Timesheets"][y]["Date"] == f'{self.get_current_date()}':
                                                    if jobs[job][2]["Timesheets"][y]["Check-in"] == '':
                                                        jobs[job][2]["Timesheets"][y]["Check-in"] = str(value)
                                                        self.write_to_json(jobs)
                                                        test = False
                                                    elif jobs[job][2]["Timesheets"][y]["Check-out"] == '':
                                                        jobs[job][2]["Timesheets"][y]["Check-out"] = str(value)
                                                        self.write_to_json(jobs)
                                                        st.warning(body='Hi')
                                                        test = False
                                                    else: 
                                                        y += 1
                                                    
                                                    
                                            else:
                                                y += 1
                                        except:
                                            new = {"Name": f"{st.session_state['name']}",
                                                "Date": f"{self.get_current_date()}",
                                                "Check-in": f"{str(value)}",
                                                "Check-out": ""}
                                            jobs[job][2]["Timesheets"].append(new) 
                                            self.write_to_json(jobs)
                                            test = False

                                        
                                    st.experimental_rerun()

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

                            # with m:
                            #     y = 3
                            #     z = 0

                            #     while jobs[job][z] == "Current":

                            #         try:
                            #             for keys, values in jobs[job][y]["Materials"].items():
                            #                 pass
                            #         except:
                            #             pass

                            

                                

            




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



if __name__ == '__main__':
    App().main()
