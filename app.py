import streamlit as st
import os
import time
import pandas as pd
from datetime import datetime
import plotly.express as px
import PIL.Image
from docx2pdf import convert
import platform

#os.chdir(r'E:\projects\smartscan2_1')

import utilities

st.set_page_config(layout="wide")

system = platform.system()

import os

def list_files_and_directories(path="."):
    # List all files and directories in the specified path
    for entry in os.listdir(path):
        # Join the path with the entry name to get the full path
        full_path = os.path.join(path, entry)
        if os.path.isdir(full_path):
            print("Directory:", full_path)
            # Recursively list files and directories within the directory
            list_files_and_directories(full_path)
        else:
            print("File:", full_path)


#input_image_path = 'uploaded_image.jpg'

# State management -----------------------------------------------------------

state = st.session_state

def init_state(key, value):
  if key not in state:
    state[key] = value

# generic callback to set state
def _set_state_cb(**kwargs):
    for state_key, widget_key in kwargs.items():
        val = state.get(widget_key, None)
        if val is not None or val == "":
            setattr(state, state_key, state[widget_key])

def _set_login_cb(username, password):
    state.login_successful, state.role = utilities.login(username, password)
    
def _reset_login_cb():
    state.login_successful = False
    state.username = ""
    state.password = "" 

init_state('login_successful', False)
init_state('username', '')
init_state('password', '')




def main():
        
    st.title("SmartScan")
    
    # Get session state
    if "login_successful" not in st.session_state:
        st.session_state.login_successful = False
    if "username" not in st.session_state:
        st.session_state.username = ""
    if "password" not in st.session_state:
        st.session_state.password = ""
        
    # If login is successful
    if state.login_successful:
        
        if state.role == 'diagnostics':
            
            if 'patients_df' or 'credentials_df' not in st.session_state:               
                st.session_state.patients_df = pd.read_excel('patients_info.xlsx')
                st.session_state.credentials_df = pd.read_excel('credentials.xlsx')
            
            if st.button("Refresh Reports"):
                st.session_state.patients_df = pd.read_excel('patients_info.xlsx')
                st.session_state.credentials_df = pd.read_excel('credentials.xlsx')
            
            #... Read existing data ...
            patients_df = st.session_state.patients_df # pd.read_excel('patients_info.xlsx')
            
            credentials_df = st.session_state.credentials_df # pd.read_excel('credentials.xlsx')
            
            curr_diag_combination = st.session_state.username + '__' + st.session_state.password
            
            curr_diag_credits = list( credentials_df.loc[credentials_df['combination'] == curr_diag_combination, 'credits' ] )[0]
            
            st.write( 'Available Credits : ', int( curr_diag_credits ) )    
            
            st.subheader( 'Upload Image', divider='orange' )
            
            # Input fields
            col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
            with col1:
                patient_name = st.text_input("Patient Name", key = 'patient_name', max_chars = 100 )
            with col2:
                patient_age = st.number_input("Age", min_value=0, step=1, value = None )
            with col3:
                patient_gender = st.selectbox("Gender", ['Male', 'Female', 'Other'], key = 'gender', index = None )             
            with col4:
                doctor_name = st.text_input("Doctor's Name", key = 'doctor_name', max_chars = 100 )
            
                
            col5, col5_1, col5_2 = st.columns([2, 2, 2])
            
            with col5:
                uploaded_image = st.file_uploader("Upload image 1")
            
            with col5_1:
                uploaded_image_2 = st.file_uploader("Upload image 2")
                
            with col5_2:
                uploaded_image_3 = st.file_uploader("Upload image 3")
                
            # Check if all mandatory inputs are provided
            mandatory_fields_filled = patient_name and patient_age is not None and patient_gender and doctor_name and uploaded_image is not None
        
            if st.button("Submit"):
                
                if curr_diag_credits == 0:
                    st.markdown("<p style='color: red;'>Please Top Up Credits to generate reports.</p>", unsafe_allow_html=True)
                else:
                    # Highlight mandatory fields if not filled
                    if not mandatory_fields_filled:
                        st.markdown("<p style='color: red;'>Please provide all inputs.</p>", unsafe_allow_html=True)
                    else:
                        #... Updating credits ....
                        curr_diag_credits = max( 0, curr_diag_credits - 1 )
                        
                        credentials_df.loc[credentials_df['combination'] == curr_diag_combination, 'credits'] = curr_diag_credits
                        
                        credentials_df.to_excel( 'credentials.xlsx', index = False)
                        
                        #.... Patient info submission
                        
                        patient_id = 'p' + str( int( 1000*time.time() ) )
                        patient_image_filename = 'submitted_images/img_' + patient_id
                        
                        col6, col6_2, col6_3 = st.columns([1,1,1])

                        print( list_files_and_directories('.') )
                        
                        # Display the uploaded images
                        with col6:
                            st.subheader( 'Submitted Image 1', divider='orange' )
                            st.image(uploaded_image, caption="Uploaded Image", use_column_width=True)
                        
                        with open(patient_image_filename + '_1' + '.jpg', "wb") as f:
                             f.write(uploaded_image.read())

                        with col6_2:
                            st.subheader( 'Submitted Image 2', divider='orange' )
                            st.image(uploaded_image_2, caption="Uploaded Image", use_column_width=True)
                        
                        with open(patient_image_filename + '_2' + '.jpg', "wb") as f:
                             f.write(uploaded_image_2.read())

                        with col6_3:
                            st.subheader( 'Submitted Image 3', divider='orange' )
                            st.image(uploaded_image_3, caption="Uploaded Image", use_column_width=True)
                        
                        with open(patient_image_filename + '_3' + '.jpg', "wb") as f:
                             f.write(uploaded_image_3.read())
                        
                        data = {
                            'ID': patient_id,
                            'Name': [patient_name],
                            'Age': [patient_age],
                            'Gender': [patient_gender],
                            "Doctor_name": [doctor_name],
                            'diagnostics_combination': curr_diag_combination,
                            'Submission_time': datetime.now().strftime("%dth %b %Y %H:%M:%S")
                        }
                        
                        # Create a DataFrame
                        submitted_patient_df = pd.DataFrame(data)
                        
                        # Convert 'Submission_time' to datetime
                        submitted_patient_df['Submission_time'] = pd.to_datetime(submitted_patient_df['Submission_time'], format="%dth %b %Y %H:%M:%S")

                        # Extract date
                        submitted_patient_df['Date'] = submitted_patient_df['Submission_time'].dt.date

                                                                
                        report_creation_flag = utilities.analysis_docx( uploaded_image, patient_id, patient_image_filename+ '_1' + '.jpg' )
                        
                        if report_creation_flag == 'Success':
                            submitted_patient_df['Report_Status'] = 'Not Ready'
                        else:
                            submitted_patient_df['Report_Status'] = 'Report generation failed. Upload better image.'
                            
                        updated_patients_df = pd.concat([submitted_patient_df, patients_df ], ignore_index=True)
                        
                        updated_patients_df.to_excel('patients_info.xlsx', index = False)
                        
                        #... Filtering for current diagonstics combination
                        
                        curr_diag_patients_df = updated_patients_df.loc[updated_patients_df['diagnostics_combination'] == curr_diag_combination, ]
                                            
                        display_patients_df = curr_diag_patients_df[ ['ID', 'Name', 'Age', 'Gender', 'Doctor_name',                              'Submission_time', 'Report_Status'] ]
                        
                        #with col7:
                        st.subheader( 'Patient Information', divider='orange' )
                        st.table( display_patients_df )
                        
            #.... Download report logic ....
            
            st.subheader( 'Download Report', divider='orange' )
            
            report_ready_df = patients_df.loc[patients_df['Report_Status'] == 'Report Ready', ].reset_index(drop=True)
            
            if len( report_ready_df ) > 0:
                # Convert 'Submission_time' to datetime
                report_ready_df['Submission_time'] = pd.to_datetime(report_ready_df['Submission_time'], format='%dth %b %Y %H:%M:%S')          
                # Extract date from datetime
                report_ready_df['Date'] = report_ready_df['Submission_time'].dt.date
                
                report_ready_df_to_show = report_ready_df[['ID', 'Name', 'Age', 'Gender', 'Doctor_name',
                       'Submission_time', 'Report_Status']]
                
                st.table( report_ready_df_to_show )
                
                col6, col7, col8 = st.columns([1, 1, 4])
                
                with col6:
                    report_dl_date = st.selectbox("Image Submission Date", list(dict.fromkeys(report_ready_df['Date'] )), key = 'report_dl_date' )
                    
                report_ready_df_datewise = report_ready_df.loc[report_ready_df['Date'] == report_dl_date, ]
                
                with col7:
                    report_dl_id = st.selectbox("Patient ID", list( report_ready_df_datewise['ID'] ), key = 'report_dl_id' )
                report_ready_filename_path = 'generated_reports/report_' + report_dl_id + '_report.pdf'
                
                report_patient_dl_df = report_ready_df_datewise.loc[report_ready_df_datewise['ID'] == report_dl_id, ]
                                
                report_filename = 'Report_' + report_patient_dl_df['Name'].iloc[0] + '_' + report_patient_dl_df['ID'].iloc[0] + '.pdf'
                            
                with col8:
                    utilities.download_pdf( report_ready_filename_path, report_filename )
                    
                    utilities.display_pdf(report_ready_filename_path)
                    
            else:
                st.info( 'No Reports to download !' )  
                    
        elif state.role == 'radiologist':
            
            logged_in_radiologist = st.session_state.username + '__' + st.session_state.password
            
            if 'patients_df' or 'credentials_df' not in st.session_state:               
                st.session_state.patients_df = pd.read_excel('patients_info.xlsx')
                st.session_state.credentials_df = pd.read_excel('credentials.xlsx')
            
            if st.button("Refresh Radiologist"):
                st.session_state.patients_df = pd.read_excel('patients_info.xlsx')
                st.session_state.credentials_df = pd.read_excel('credentials.xlsx')
            
            #... Read existing data ...
            patients_df = st.session_state.patients_df # pd.read_excel('patients_info.xlsx')
            
            credentials_df = st.session_state.credentials_df # pd.read_excel('credentials.xlsx')
            
            assigned_diagnostics = str( list( credentials_df.loc[credentials_df['combination'] == logged_in_radiologist, 'diagnostics_to_radiologist'] )[0] )
            
            assigned_diagnostics_list = [] if assigned_diagnostics == 'nan' else assigned_diagnostics.split(',')
            
            if len( assigned_diagnostics_list ) == 0:
                report_not_ready_df_sorted = pd.DataFrame()
            else:
                assigned_patients_df = patients_df[patients_df['diagnostics_combination'].isin( assigned_diagnostics_list )]
                
                report_not_ready_df = assigned_patients_df.loc[patients_df['Report_Status'] == 'Not Ready', ]
                
                report_not_ready_df_sorted = report_not_ready_df.sort_values(by='ID', ascending=True).reset_index(drop=True)   #... Arranging to keep older reports on top
            
            if len(report_not_ready_df_sorted) > 0:
                                
                st.table( report_not_ready_df_sorted.drop('diagnostics_combination', axis=1) )
                                
                patient_selected_id = st.selectbox("Patient ID", list(report_not_ready_df_sorted.ID), key = 'gender' )
                                
                curr_patient_report_filename = 'generated_reports/report_' + patient_selected_id
                
                curr_patient_report_filename_docx = curr_patient_report_filename + '.docx'
                
                curr_patient_report_filename_docx_report = curr_patient_report_filename + '_report.docx'
                
                curr_patient_report_filename_pdf = curr_patient_report_filename + '.pdf'
                
                original_content = utilities.read_docx(curr_patient_report_filename_docx)
                
                curr_patient_image_filepath = 'submitted_images/img_' + patient_selected_id
                                
                curr_patient_image_1 = PIL.Image.open(curr_patient_image_filepath + '_1' + '.jpg')
                
                st.image(curr_patient_image_1, caption="", use_column_width=True)

                curr_patient_image_2 = PIL.Image.open(curr_patient_image_filepath + '_2' + '.jpg')
                
                st.image(curr_patient_image_2, caption="", use_column_width=True)

                curr_patient_image_3 = PIL.Image.open(curr_patient_image_filepath + '_3' + '.jpg')
                
                st.image(curr_patient_image_3, caption="", use_column_width=True)
                
                edited_content = st.text_area("Report", value=original_content, height=400)
                                    
                if st.button("Approve Report"):
                    
                    curr_patient_info_df = patients_df.loc[patients_df['ID'] == patient_selected_id, ['ID', 'Name', 'Age', 'Gender', 'Doctor_name', 'Submission_time'] ]
                    
                    curr_patient_info_df['Modality'] = 'XR'
                    
                                        
                    #.... Save edited docx report
                    #utilities.write_docx(curr_patient_report_filename_docx, edited_content )
                    
                    curr_patient_report_filename_pdf = curr_patient_report_filename + '_report.pdf'
                    
                    curr_patient_image_path = 'submitted_images/img_' + patient_selected_id + '.jpg'
                    
                    sign_path = 'radiologist_sign/' + logged_in_radiologist + '_sign.jpg'
                    
                                        
                    logged_in_radiologist_details_df = credentials_df.loc[credentials_df['combination'] == logged_in_radiologist]
                    
                    utilities.write_docx(edited_content, curr_patient_image_path, curr_patient_info_df, curr_patient_report_filename_docx_report, sign_path, logged_in_radiologist_details_df )
                    
                    if system == 'Windows':
                        
                        import pythoncom
                        
                        # Manually initialize COM
                        pythoncom.CoInitialize()
                        
                        convert( curr_patient_report_filename_docx_report, curr_patient_report_filename_pdf )
                    else:
                        utilities.convert_docx_to_pdf( curr_patient_report_filename_docx_report, 'generated_reports' )

                    #st.write( utilities.list_files( 'generated_reports' ) )

                    #st.write( utilities.list_directories( 'generated_reports' ) )
                    
                    #utilities.save_as_docx_markdown2(edited_content, curr_patient_image_path, curr_patient_info_df, curr_patient_report_filename_docx_report, sign_path, logged_in_radiologist_details_df )
                                        
                    # utilities.save_as_pdf_markdown(edited_content, curr_patient_image_path, curr_patient_info_df, curr_patient_report_filename_pdf, sign_path, logged_in_radiologist_details_df )
                    
                    #json_data = json.loads(edited_content)
                    #headings = ['Findings', 'Impressions', 'Recommendations', 'ICD-10'] # list(json_data.keys())
                    
                    #markdown_content = edited_content # utilities.json_to_markdown(edited_content)
                    
                    
                    #utilities.save_as_pdf(markdown_content, curr_patient_report_filename_pdf, headings, curr_patient_info_df)
                    
                    st.success( 'Report saved successfully.' )
                    
                    utilities.display_pdf(curr_patient_report_filename_pdf)
                    
                    patients_df.loc[patients_df['ID'] == patient_selected_id, 'Report_Status'] = 'Report Ready'
                    
                    patients_df.loc[patients_df['ID'] == patient_selected_id, 'approved_by'] = logged_in_radiologist

                    patients_df.to_excel( 'patients_info.xlsx', index=False )
                
            else:
                st.success('All reports verified. No new report to be verified as of now.')
                
            #.... Logic for how many reports radiologist approved ....
            
            # Convert 'Submission_time' to datetime
            patients_df['Submission_time'] = pd.to_datetime(patients_df['Submission_time'], format='%dth %b %Y %H:%M:%S')          
            
            # Extract date from datetime
            patients_df['Date'] = patients_df['Submission_time'].dt.date
            
            curr_radiologist_approval_df = patients_df[patients_df['approved_by'] == logged_in_radiologist ]
                       
            
            if len( curr_radiologist_approval_df ) == 0:    #.... If there are no reports approved
                st.success("No approved reports !")
            else:
                
                reports_approved_summary = curr_radiologist_approval_df.groupby([ 'Date']).size().reset_index(name='num_reports_approved')
                
                st.subheader( 'Reports Approved Summary', divider='orange' )
                
                st.table( reports_approved_summary ) 
            
        elif state.role == 'admin':
            
            if 'patients_df' or 'credentials_df' not in st.session_state:               
                st.session_state.patients_df = pd.read_excel('patients_info.xlsx')
                st.session_state.credentials_df = pd.read_excel('credentials.xlsx')
            
            if st.button("Refresh Admin"):
                st.session_state.patients_df = pd.read_excel('patients_info.xlsx')
                st.session_state.credentials_df = pd.read_excel('credentials.xlsx')
            
            #... Read existing data ...
            patients_df = st.session_state.patients_df # pd.read_excel('patients_info.xlsx')
            
            credentials_df = st.session_state.credentials_df # pd.read_excel('credentials.xlsx')
            
            # Convert 'Submission_time' to datetime
            patients_df['Submission_time'] = pd.to_datetime(patients_df['Submission_time'], format='%dth %b %Y %H:%M:%S')
            
            # Extract date from datetime
            patients_df['Date'] = patients_df['Submission_time'].dt.date
            
            # Count the number of entries on each date
            entries_per_date = patients_df['Date'].value_counts().reset_index()
            
            entries_per_date.columns = ['Date', 'Number of Entries']
            
            # Sort the DataFrame by Date
            entries_per_date = entries_per_date.sort_values(by='Date')
                        
            fig = px.line(entries_per_date, x='Date', y='Number of Entries', markers=True, text='Number of Entries',
              labels={'Number of Entries': 'Reports'})
            
            fig.update_xaxes(type='category')
            
            fig.update_layout(title='Number of Reports Over Time')
            
            st.subheader('Metrics', divider='orange')
            
            col100, col101, col102, col103, col104, col105, col105_1 = st.columns(7)
            
            with col100:
                st.metric(label="Total Reports", value = len( patients_df ) )
            with col101:
                st.metric(label="Pending Verification", value = len( patients_df[patients_df['Report_Status'] == 'Not Ready']) )
            with col102:
                st.metric(label="Report Ready", value = len( patients_df[patients_df['Report_Status'] == 'Report Ready']) )
            with col103:
                st.metric(label="Report Generation Failed", value = len( patients_df[patients_df['Report_Status'] == 'Report generation failed. Upload better image.']) )
            with col104:
                st.metric(label="Total Diagnostics", value = len( credentials_df[credentials_df['role'] == 'diagnostics']) )
            with col105:
                st.metric(label="Total Radiologists", value = len( credentials_df[credentials_df['role'] == 'radiologist']) )
            with col105_1:
                st.metric(label="Total Referrals", value = len( credentials_df[credentials_df['role'] == 'referral']) )
                
            st.plotly_chart(fig)
            
            #.... User creation .....
            
            st.subheader('User Creation', divider='orange')
            
            col120, col121, col122, col123, col123_1 = st.columns([2, 2, 2, 1, 1])
            
            with col120:
                new_name = st.text_input("Name", key = 'new_name', max_chars = 100 )            
            with col121:
                new_username = st.text_input("Username", key = 'new_username', max_chars = 100 )
            with col122:
                new_password = st.text_input("Password", key = 'new_password', max_chars = 100 )
            with col123:
                new_role = st.selectbox("Role", ['diagnostics', 'radiologist', 'referral'], key = 'new_role', index = None )
            with col123_1:
                if st.button("Create New User"):
                    if not ( new_name and new_username and new_password and new_role ):
                        st.markdown("<p style='color: red;'>Please provide all inputs.</p>", unsafe_allow_html=True)
                    else:
                        data_new_user = {
                            'name': [new_name],
                            'username': [new_username],
                            'password': [new_password],
                            'role': [new_role],
                            'credits': 20
                        }
                    
                        # Create a DataFrame
                        new_user_df = pd.DataFrame(data_new_user)
                        
                        new_user_combination = new_user_df.username + '__' + new_user_df.password
                        
                        new_user_df['combination'] = new_user_combination
                                                                                        
                        if any( credentials_df['combination'].isin([new_user_combination[0]]) ):
                            st.error('This username and password combination already exists.')
                        else:
                            updated_credentials_df = pd.concat([new_user_df, credentials_df ], ignore_index=True)
                            
                            updated_credentials_df.to_excel( 'credentials.xlsx', index=False )
                            
                            st.success( 'New user created successfully !' )
            
            #.... Radiologist Details .....
            
            st.subheader('Radiologist Onboarding', divider='orange')
            
            col123_2, col123_3, col123_4, col123_5, col123_6, col123_7 = st.columns([1, 2, 1, 2, 2, 1])
            
            with col123_2:
                radiologist_combination = st.selectbox("Radiologist", list( credentials_df[credentials_df['role'] == 'radiologist']['combination'] ), key = 'radiologist_combination', index = None )           
            with col123_3:
                radiologist_designation = st.text_input("Designation", key = 'radiologist_designation', max_chars = 100 )
            with col123_4:
                radiologist_degree = st.text_input("Degree", key = 'radiologist_degree', max_chars = 100 )
            with col123_5:
                radiologist_registration_num = st.text_input("Registration Number", key = 'radiologist_registration_num', max_chars = 100 )
            with col123_6:
                radiologist_sign = st.file_uploader("Signature")
            with col123_7:
                if st.button('Onboard'):
                    if not ( radiologist_combination and radiologist_designation and radiologist_degree and radiologist_registration_num and radiologist_sign ):
                        st.markdown("<p style='color: red;'>Please provide all inputs.</p>", unsafe_allow_html=True)
                    else:
                        radiologist_sign_filepath = 'radiologist_sign/' + radiologist_combination + '_sign.jpg'
                        radiologist_details = {
                            'combination': [radiologist_combination],
                            'radiologist_designation': [radiologist_designation],
                            'radiologist_degree': [radiologist_degree],
                            'radiologist_registration_num': [radiologist_registration_num],
                            'radiologist_sign_filepath': [radiologist_sign_filepath]
                        }
                        
                        with open(radiologist_sign_filepath, "wb") as f:
                             f.write(radiologist_sign.read())
                    
                        # Create a DataFrame
                        radiologist_details_df = pd.DataFrame(radiologist_details)
                        
                        selected_columns_credentials = [ col for col in credentials_df.columns if col not in ['radiologist_designation', 'radiologist_degree', 'radiologist_registration_num', 'radiologist_sign_filepath' ] ]
                        
                        credentials_df = pd.merge( credentials_df[ selected_columns_credentials ], radiologist_details_df, on='combination', how='left' )
                        
                        credentials_df.to_excel('credentials.xlsx', index=False)
                        
                        st.success('Radiologist onboard successful!')
            
            #... Assign credits to diagnostics centre ...
            
            # credentials_df = pd.read_excel('credentials.xlsx')
            
            st.subheader('Assign credits to diagnostics centre', divider='orange')
            
            col124, col125, col125_1 = st.columns([2,2,1])
            
            with col124:
                assign_credits_user = st.selectbox("User", list( credentials_df[credentials_df['role'] == 'diagnostics']['combination'] ), key = 'assign_credits_user', index = None )
            with col125:
                num_credits_given = st.number_input("Number of Credits", min_value=1, step=1, value = None )    
            
            with col125_1:
                if st.button('Assign Credits'):
                    
                    if not ( assign_credits_user and num_credits_given is not None ):
                        st.markdown("<p style='color: red;'>Please provide all inputs.</p>", unsafe_allow_html=True)
                    else:
                        credentials_df.loc[credentials_df['combination'] == assign_credits_user, 'credits'] = list( credentials_df.loc[credentials_df['combination'] == assign_credits_user, 'credits'] )[0] + num_credits_given   #.... adding new credits to previous credits
                    
                        credentials_df.to_excel( 'credentials.xlsx', index = False)
                    
            #... Assign diagnostics centres to referral ...
                        
            st.subheader('Assign diagnostics centres to referral', divider='orange')
            
            col126, col127, col128 = st.columns([2,2,1])
            
            with col126:
                referral_user = st.selectbox("Referral", list( credentials_df[credentials_df['role'] == 'referral']['combination'] ), key = 'referral_user', index = None )
                
            with col127:
                assigned_diagnostics_centre = st.selectbox("Diagnostics Centre", list( credentials_df[credentials_df['role'] == 'diagnostics']['combination'] ), key = 'assigned_diagnostics_centre', index = None )
            
            with col128:
                
                if st.button('Assign Diagnostics Centre to Referral'):
                    
                    if not ( referral_user and assigned_diagnostics_centre is not None ):
                        st.markdown("<p style='color: red;'>Please provide all inputs.</p>", unsafe_allow_html=True)
                    else:
                        curr_diagnostics = str( list( credentials_df.loc[credentials_df['combination'] == referral_user, 'referred_diagnostics'] )[0] ).split(',')
                        
                        if assigned_diagnostics_centre not in curr_diagnostics:   #... if already assigned to referral don't reassign
                        
                            updated_diagnostics_list = ( [] if curr_diagnostics == 'nan' else curr_diagnostics ) + [ assigned_diagnostics_centre ]
                            
                            credentials_df.loc[credentials_df['combination'] == referral_user, 'referred_diagnostics'] = ",".join( updated_diagnostics_list )
                            
                            credentials_df.to_excel( 'credentials.xlsx', index=False )
            
            #... Assign diagnostics centres to radiologists ...
                        
            st.subheader('Assign diagnostics centres to radiologists', divider='orange')
            
            col129, col130, col131 = st.columns([2,2,1])
            
            with col129:
                radiologist_user = st.selectbox("Radiologist", list( credentials_df[credentials_df['role'] == 'radiologist']['combination'] ), key = 'radiologist_user', index = None )
                
            with col130:
                assigned_diagnostics_centre_rad = st.selectbox("Diagnostics Centre", list( credentials_df[credentials_df['role'] == 'diagnostics']['combination'] ), key = 'assigned_diagnostics_centre_rad', index = None )
            
            with col131:
                
                if st.button('Assign Diagnostics to Radiologist'):
                    
                    if not ( radiologist_user and assigned_diagnostics_centre_rad is not None ):
                        st.markdown("<p style='color: red;'>Please provide all inputs.</p>", unsafe_allow_html=True)
                    else:
                        curr_diagnostics_rad = str( list( credentials_df.loc[credentials_df['combination'] == radiologist_user, 'diagnostics_to_radiologist'] )[0] ).split(',')
                        
                        if assigned_diagnostics_centre_rad not in curr_diagnostics_rad:   #... if already assigned to radiologist don't reassign
                        
                            updated_diagnostics_list_rad = ( [] if curr_diagnostics_rad == 'nan' else curr_diagnostics_rad ) + [ assigned_diagnostics_centre_rad ]
                            
                            credentials_df.loc[credentials_df['combination'] == radiologist_user, 'diagnostics_to_radiologist'] = ",".join( updated_diagnostics_list_rad )
                            
                            credentials_df.to_excel( 'credentials.xlsx', index=False )
                        
            st.table( credentials_df )
        elif state.role == 'referral':
            
            if 'patients_df' or 'credentials_df' not in st.session_state:               
                st.session_state.patients_df = pd.read_excel('patients_info.xlsx')
                st.session_state.credentials_df = pd.read_excel('credentials.xlsx')
            
            if st.button("Refresh Referral"):
                st.session_state.patients_df = pd.read_excel('patients_info.xlsx')
                st.session_state.credentials_df = pd.read_excel('credentials.xlsx')
            
            #... Read existing data ...
            patients_df = st.session_state.patients_df # pd.read_excel('patients_info.xlsx')
            
            credentials_df = st.session_state.credentials_df # pd.read_excel('credentials.xlsx')
                                    
            # Convert 'Submission_time' to datetime
            patients_df['Submission_time'] = pd.to_datetime(patients_df['Submission_time'], format='%dth %b %Y %H:%M:%S')          
            
            # Extract date from datetime
            patients_df['Date'] = patients_df['Submission_time'].dt.date
            
            curr_referral_combination = st.session_state.username + '__' + st.session_state.password
            
            referred_diagnostics = str( list( credentials_df.loc[credentials_df['combination'] == curr_referral_combination, 'referred_diagnostics'] )[0] )
            
            referred_diagnostics_list = [] if referred_diagnostics == 'nan' else referred_diagnostics.split(',')
            
            if len( referred_diagnostics_list ) == 0:    #.... If there are no referrals to show
                st.success("No referrals to show !")
            else:
                
                referred_diag_stats_df = patients_df[patients_df['diagnostics_combination'].isin( referred_diagnostics_list )]
                
                referred_diag_stats_df_with_name = pd.merge(referred_diag_stats_df, credentials_df[['name', 'combination']] , left_on='diagnostics_combination', right_on='combination', how='left')
                
                diag_stats_summary = referred_diag_stats_df_with_name.groupby(['Name', 'Date']).size().reset_index(name='num_reports_uploaded')
                
                st.subheader( 'Diagnostics Centre Stats', divider='orange' )
                
                st.table( diag_stats_summary )
                    
    else:
        st.subheader("Login")
        # Display login form
        st.text_input(
            "Username:", value=state.username, key='username_input',
            on_change=_set_state_cb, kwargs={'username': 'username_input'}
        )
        st.text_input(
            "Password:", type="password", value=state.password, key='password_input',
            on_change=_set_state_cb, kwargs={'password': 'password_input'}
        )
        
        # Check login credentials
        if not state.login_successful and st.button("Login", on_click=_set_login_cb, args=(state.username, state.password)):
            st.warning("Wrong username or password.")



if __name__ == "__main__":
    main()
