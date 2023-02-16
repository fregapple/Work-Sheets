import streamlit as st
import streamlit_authenticator as stauth
import yaml, time, json
from pathlib import Path
from datetime import datetime


class App:
    
    st.set_page_config(layout='wide')


    body = ['Timesheet', 'Materials', 'Notes']
    item3 = None
    p = 0



    def write_to_json(self, text):
        text = json.dumps(text, indent=4)
        with open ('./jobs.json', 'w') as outfile:
            outfile.write(text)


    def read_json(self):
        if Path('./jobs.json').is_file():
            with open('./jobs.json', 'r') as openfile:
                jobs = json.load(openfile)
        return jobs




    def get_current_date(self):
        date = datetime.today()
        date = date.strftime("%d/%m/%Y")
        return date


    def auth_read(self):
        if Path('./config.yaml').is_file():
            with open('./config.yaml') as file:
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

            st.write(f'Welcome *{st.session_state["name"]}*')
            st.title('JFJ Joinery Work Sheets')
            x = 0
            current, complete = st.tabs(['Current', 'Complete'])


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
                                
                                for items, values in jobs[job][2].items():
                                    for thing in values:
                                        
                                        with st.form(f'my_form{self.p}'):
                                            col0, col1, col2, col3 = st.columns(4)

                                            with col0:
                                                st.write('Name')
                                                st.text_input('p', key=x, value=thing["Name"], label_visibility='collapsed')
                                                x += 1
                                            with col1:
                                                st.write('Date')
                                                st.text_input('p', key=x, value=thing["Date"], label_visibility='collapsed')
                                                x += 1
                                            with col2:
                                                st.write('Check-in')
                                                st.text_input('p', key=x, value=thing["Check-in"], label_visibility='collapsed')
                                                x += 1
                                            with col3:
                                                st.write('Check-out')
                                                st.text_input('p', key=x, value=thing["Check-out"], label_visibility='collapsed')
                                            x += 1
                                        self.p += 1


                                col0, col1, col2, col3 = st.columns(4)

                                with col0:

                                    try:
                                        y=2
                                        z=0

                                        while jobs[job][z] == 'Current':

                                            try: 
                                                st.write('Name')
                                                                                
                                                for items, values in jobs[job][2].items():
                                                    for thing in values:
                                                        st.text_input('p', key=x, value=thing["Name"], label_visibility="collapsed", disabled=True)
                                                        x += 1
                                                        
                                                z += 1

                                            except:
                                                z += 1


                                    except:
                                        pass

                                with col1:


                                    try:
                                        y=2
                                        z=0

                                        while jobs[job][z] == 'Current':

                                            try: 
                                                st.write('Date')
                                                                                
                                                for items, values in jobs[job][2].items():
                                                    for thing in values:
                                                        st.text_input('p', key=x, value=thing["Date"], label_visibility="collapsed", disabled=True)
                                                        x += 1
                                                        
                                                z += 1

                                            except:
                                                z += 1
                                                

                                    except:
                                        pass
                                    
                                with col2:

                                    try:
                                        y=2
                                        z=0

                                        while jobs[job][z] == 'Current':

                                            try: 
                                                st.write('Start')
                                                                                
                                                for items, values in jobs[job][2].items():
                                                    for thing in values:
                                                        st.text_input('p', key=x, value=thing["Check-in"], label_visibility="collapsed", disabled=True)
                                                        x += 1
                                                        
                                                z += 1

                                            except:
                                                z += 1
                                                

                                    except:
                                        pass
                                    

                                with col3:

                                    try:
                                        y=2
                                        z=0

                                        while jobs[job][z] == 'Current':

                                            try: 
                                                st.write('End')
                                                                                
                                                for items, values in jobs[job][2].items():
                                                    for thing in values:
                                                        st.text_input('p', key=x, value=thing["Check-out"], label_visibility="collapsed", disabled=True)
                                                        x += 1
                                                        
                                                z += 1

                                            except:
                                                z += 1
                                                

                                    except:
                                        pass



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
