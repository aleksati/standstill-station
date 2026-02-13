import os, random, subprocess
import numpy as np
import pandas as pd
from scipy.stats import norm
import winsound
import tkinter
from tkinter import ttk
from tkinter import *
from tkinter import simpledialog
from typing import List, Any
from threading import Timer
from datetime import datetime
import time
import yaml

from PIL import Image, ImageTk
import mysql.connector

from pythonosc.osc_server import BlockingOSCUDPServer
from pythonosc.dispatcher import Dispatcher
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

class Standstill(tkinter.Tk):
    def __init__(self, database, cursor, audio_folder='audio', *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Display widget in fullscreen
        # self.attributes('-fullscreen', True)
        self.overrideredirect(True)
        self.state('zoomed')

        self.database          = database
        self.cursor            = cursor
        self.counter           = 6 # seconds
        self.audio_folder      = audio_folder
        self.stop_commit       = False
        self.try_again         = False

        # Load general text font and style
        self.font              = ('Oslo Sans Office', 20)
        plt.style.use('fivethirtyeight') 
        # Stop playing potential sounds
        winsound.PlaySound(None, winsound.SND_PURGE)

        # Create the tkinter images 
        self.norsk             = tkinter.PhotoImage(file="images/norsk.png")
        self.english           = tkinter.PhotoImage(file="images/english.png")
        # Resize background images with PIL
        image                  = Image.open("images/bg.png")
        image                  = image.resize((self.winfo_screenwidth(), self.winfo_screenheight()))
        self.bg                = ImageTk.PhotoImage(image)
        image                  = Image.open("images/gratulerer.png")
        image                  = image.resize((self.winfo_screenwidth(), self.winfo_screenheight()))
        self.bg_gratulerer     = ImageTk.PhotoImage(image)

        # Create Canvas
        self.canvas_bg         = tkinter.Canvas(self)
        self.canvas_bg.pack(fill="both", expand=True)
        # Display background image and title
        self.canvas_bg.create_image(
                                    self.winfo_screenwidth() // 2, 
                                    self.winfo_screenheight() // 2, 
                                    image=self.bg, 
                                    anchor="center",
                                    tag="background"
                                    )
        # Create text for the presentation and the countdown
        self.canvas_bg.create_text(
                                   self.winfo_screenwidth() // 2, 
                                   self.winfo_screenheight() // 3.5, 
                                   text='Norwegian Championship of Standstill', 
                                   width=self.winfo_screenwidth() // 1.5, 
                                   font=('Oslo Sans Office', 45),
                                   fill='white',
                                   tag="presentation"
                                   )
        self.counter_text = self.canvas_bg.create_text(
                                                       self.winfo_screenwidth() // 2, 
                                                       self.winfo_screenheight() // 2, 
                                                       width=self.winfo_screenwidth() // 1.5, 
                                                       font=('Oslo Sans Office', 150),
                                                       fill='white',
                                                       tag="countdown"
                                                       )

        # Create the tkinter buttons 
        self.start_button      = tkinter.Button(self, 
                                               text='START', 
                                               bd=5,  
                                               font=self.font,
                                               height=2, 
                                               width=10,
                                               command=self.tkinter_countdown
                                               )
        self.norsk_button      = tkinter.Button(self, 
                                               image=self.norsk, 
                                               bd=5,
                                               text="Velg ditt språk",
                                               fg='white',
                                               compound="center",  
                                               command=self.norsk_documentation
                                               )
        self.english_button    = tkinter.Button(self, 
                                               image=self.english, 
                                               bd=5,  
                                               text='Choose your language',
                                               fg='white',
                                               compound="center",
                                               command=self.english_documentation
                                               )
        
        # Display buttons 
        self.norsk_button.place(relx=0.4, rely=0.55, anchor='center')
        self.english_button.place(relx=0.6, rely=0.55, anchor='center')
        # Run the Tkinter event loop
        self.mainloop()

    def norsk_documentation(self):
        self.after(0, self.combine_funcs(self.norsk_button.destroy, self.english_button.destroy))
        self.canvas_bg.delete("presentation")
        
        # Add title and text documentation
        self.canvas_bg.create_text(
                                   self.winfo_screenwidth() // 2, 
                                   self.winfo_screenheight() // 4, 
                                   text="Norgesmesterskap i Stillstand", 
                                   width=self.winfo_screenwidth() // 1.5, 
                                   font=('Oslo Sans Office', 40),
                                   fill='white',
                                   tag="title"
                                   )
        self.canvas_bg.create_text(
                                   self.winfo_screenwidth() // 2, 
                                   self.winfo_screenheight() // 2,
                                   text="\nKlarer du å stå stille til musikk - eller kjenner du at kroppen vil bevege seg til rytmene?\n\nEr noen typer musikk vanskeligere å stå stille til enn andre? ​\n\nDet skal du få teste nå!​\n\nRITMO ved UiO forsker på hvordan musikk påvirker kroppsbevegelser. Å se hvordan folk står stille – både med og uten musikk – hjelp forskerne å lære mer om dette.\n\nHer handler det med andre ord om å stå så stille du kan.\nEr du klar for å prøve å slå den gjeldende rekorden?\n\nTA PÅ HODETELEFONENE OG TRYKK PÅ START",
                                   #text="Klarer du å stå stille til musikk — eller kjenner du at kroppen vil bevege seg til rytmene? Er noen typer musikk vanskeligere å stå stille til enn andre? Det skal du få teste nå!\n\nVed UiO forskes det på hvordan musikk påvirker kroppsbevegelser. Å se hvordan folk står stille hjelper forskerne å lære mer om musikkopplevelser.\n\nEr du klar for å slå den gjeldende stillstandsrekorden?\n\nTA PÅ HODETELEFONENE OG TRYKK PÅ START!", 
                                   width=self.winfo_screenwidth() // 1.5, 
                                   font=self.font,
                                   fill='white',
                                   tag="text"
                                   )
        # Define user id and language in mysql database
        # self.mysql_check_connect()
        self.language = 'no'
        sql = f"INSERT INTO standstillUser (language) VALUES ('{self.language}')"
        self.mysql_write(sql)
        self.cursor.execute("SELECT LAST_INSERT_ID()")
        self.id = self.cursor.fetchall()[0][0]
        # Display start button
        self.start_button.place(relx=0.5, rely=0.85, anchor='center')

    def english_documentation(self):
        self.after(0, self.combine_funcs(self.norsk_button.destroy, self.english_button.destroy))
        self.canvas_bg.delete("presentation")
        # Add title and text documentation
        self.canvas_bg.create_text(
                                   self.winfo_screenwidth() // 2, 
                                   self.winfo_screenheight() // 4, 
                                   text="Norwegian Championship of Standstill", 
                                   width=self.winfo_screenwidth() // 1.5, 
                                   font=('Oslo Sans Office', 40),
                                   fill='white',
                                   tag="title"
                                   )
        self.canvas_bg.create_text(
                                   self.winfo_screenwidth() // 2, 
                                   self.winfo_screenheight() // 2, 
                                   text="\nAre you able to stay still while music plays? Or do you feel the need to move to the rhythm?\n\nAre there some types of music that are harder to stand still to than others?\n\nThat is what you can find out now!\n\nRITMO at UiO researches how music influences bodily movement. In order to explore how\npeople stand still – with and without music – help the researchers learn more about this topic.\n\nIn other words, this is about standing as still as you can.\nAre you ready to beat the current high score?\n\nPUT ON THE HEADPHONES AND PRESS START!",
                                   #text="Can you stand still to music — or do you feel your body will move to the rhythms? Are some types of music harder to stand still than others? You should get to test that now!\n\nUiO researchers study how music affects body movements. Looking at how people stand still helps the researchers learn more about music experiences.\n\nAre you ready to beat the current record?\n\nPUT ON THE HEADPHONES AND PRESS START!", 
                                   width=self.winfo_screenwidth() // 1.5, 
                                   font=self.font,
                                   fill='white',
                                   tag="text"
                                   )
        # Define user id and language in mysql database
        # self.mysql_check_connect()
        self.language = 'en'
        sql = f"INSERT INTO standstillUser (language) VALUES ('{self.language}')"
        self.mysql_write(sql)
        self.cursor.execute("SELECT LAST_INSERT_ID()")
        self.id = self.cursor.fetchall()[0][0]
        # Display start button
        self.start_button.place(relx=0.5, rely=0.85, anchor='center')

    def tkinter_countdown(self):
        if not self.try_again:
            if self.canvas_bg.winfo_exists():
                self.start_button.destroy()
                self.canvas_bg.delete("title")
                self.canvas_bg.delete("text")

        self.counter -= 1  

        if self.counter < 0:
            self.listening_audio()
            self.canvas_bg.destroy()
            return   # IMPORTANT: stop here

        elif self.counter < 1:
            self.canvas_bg.itemconfigure(self.counter_text, text='GO!', fill='red')

        else:
            self.canvas_bg.itemconfigure(self.counter_text, text=str(self.counter))

        # Only schedule next tick if canvas still exists
        if self.canvas_bg.winfo_exists():
            self.canvas_bg.after(1000, self.tkinter_countdown)

    def listening_audio(self, duration=20):
        # Initialize quaternions and time variables
        self.xdata = []
        self.Q1 = (0.0, 0.0, 0.0, 0.0)
        self.t1 = datetime.now().timestamp()
        # Create a canvas that can be embedded in a tkinter window
        self.figure = Figure(figsize=(6, 3))
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

        # Choose random file from audio folder and get genre
        audio_file = random.choice([x for x in os.listdir(self.audio_folder) if x != 'celebration.wav']) 
        audio_path = os.path.join(self.audio_folder, audio_file)
        self.genre = os.path.splitext(audio_file)[0]

        # Create a subplot to embed in the tkinter canvas
        self.plt = self.figure.add_subplot(211)
        # Start listening to audio and plot tkinter canvas
        self.audio_canvas(audio_path)
        # Switch to silence after some time
        self.after(int(duration*1000), self.listening_silence)

    def listening_silence(self, duration=20):
        # Stop listening audio in the thread
        winsound.PlaySound(None, winsound.SND_PURGE)
        self.genre = 'silence'

        # Create a subplot to embed in a tkinter canvas
        self.plt = self.figure.add_subplot(212)
        # Empty the lists for storing new data on silence
        self.xdata = []
        # Get the user's scores and feedback
        self.after(int(duration*1000), self.get_feedback)

    def data_scaler(self, X, min=100.0, max=0.0):
        den = X.max() - X.min()
        if den == 0: #prevent divide by 0
            return np.zeros_like(X)
        X_std = (X - X.min()) / den
        X_scaled = X_std * (max - min) + min
        return X_scaled
    
    def combine_funcs(self, *funcs):
        def combined_func(*args, **kwargs):
            for f in funcs:
                f(*args, **kwargs)
        return combined_func

    def get_feedback(self):
        # Stop listening audio in the thread
        winsound.PlaySound(None, winsound.SND_PURGE)
        
        # Stop committing head tracking data and destroy the figure canvas from widget
        self.stop_commit = True
        self.canvas.get_tk_widget().destroy()
        # Create new canvas
        self.canvas_bg = tkinter.Canvas(self)
        self.canvas_bg.pack(fill="both", expand=True)
        self.canvas_bg.create_image(
                                    self.winfo_screenwidth() // 2, 
                                    self.winfo_screenheight() // 2, 
                                    image=self.bg, 
                                    anchor="center",
                                    tag="background"
                                    )
        # Get the feedback of the user with likert scale and age entry
        if self.language == 'no': 
            label = 'Hvor mye likte du musikken?'
        else:
            label = 'How do you liked the music?'
        self.feedback_music      = tkinter.Scale(
                                                 self, 
                                                 label=label, 
                                                 font=self.font, 
                                                 from_=0, 
                                                 to=10, 
                                                 orient=tkinter.HORIZONTAL, 
                                                 width=50, 
                                                 length=self.winfo_screenwidth() // 1.25, 
                                                 showvalue=0, 
                                                 tickinterval=1, 
                                                 resolution=1
                                                 )
        if self.language == 'no': 
            label = 'Hvor stille stod du?'
        else:
            label = 'How still did you stand?'
        self.feedback_standstill = tkinter.Scale(
                                                 self, 
                                                 label=label, 
                                                 font=self.font, 
                                                 from_=0, 
                                                 to=10, 
                                                 orient=tkinter.HORIZONTAL, 
                                                 width=50, 
                                                 length=self.winfo_screenwidth() // 1.25, 
                                                 showvalue=0, 
                                                 tickinterval=1, 
                                                 resolution=1
                                                 )
        if not self.try_again:
            if self.language == 'no': 
                text = "Hvor gammel er du?"
            else:
                text = "How old are you?" 
            self.canvas_bg.create_text(
                                    self.winfo_screenwidth() // 2, 
                                    self.winfo_screenheight() // 1.5, 
                                    text=text, 
                                    width=self.winfo_screenwidth() // 1.5, 
                                    font=self.font,
                                    fill='white',
                                    tag="age"
                                    )
            self.age_entry = StringVar()
            self.age_entry_box = NumpadEntry(self,textvariable=self.age_entry)
            #self.age_entry = tkinter.Entry(self, font=self.font)
            self.age_entry_box.place(relx=0.5, rely=0.8, anchor='center',height=40)

        if self.language == 'no': 
            text = "FORTSETT"
        else:
            text = "CONTINUE"        
        self.fortsett            = tkinter.Button(
                                                  self, 
                                                  bd=5, 
                                                  text=text, 
                                                  font=self.font, 
                                                  compound="center", 
                                                  command=self.combine_funcs(self.store_data, self.gratulerer)
                                                  )
        
        # Place the feedback scales and the button
        self.feedback_music.place(relx=0.5, rely=0.3, anchor='center')
        self.feedback_standstill.place(relx=0.5, rely=0.5, anchor='center')
        self.fortsett.place(relx=0.5, rely=0.9, anchor='center')
        
    def store_data(self, minimum=0.0, maximum=0.1, threshold=0.001):
        # Get music and silence standstill real-time data of the user
        self.cursor.execute(f"SELECT * FROM standstillRealTime WHERE standstillUserID = {self.id} AND genre != 'silence'")
        df_music = pd.DataFrame(self.cursor.fetchall()).iloc[1: , 4:].astype(np.float32) # remove first row and four first columns and convert to absolute values
        self.cursor.execute(f"SELECT * FROM standstillRealTime WHERE standstillUserID = {self.id} AND genre = 'silence'")
        df_silence = pd.DataFrame(self.cursor.fetchall()).iloc[: , 4:].astype(np.float32) # remove four first columns and convert to absolute values
        # Check if the headphones were actually put on a head
        if df_music.median().to_numpy().mean() > threshold or df_silence.median().to_numpy().mean() > threshold:
            # Filter values above maximum to normalize score
            df_music[df_music > maximum] = maximum
            df_silence[df_silence > maximum] = maximum 
            # Add minimum and maximum values for scaling the dataframe
            df_music.loc[len(df_music.index)] = [minimum] 
            df_music.loc[len(df_music.index)+1] = [maximum] 
            df_music_scaled = self.data_scaler(df_music.to_numpy())
            df_silence.loc[len(df_silence.index)] = [minimum] 
            df_silence.loc[len(df_silence.index)+1] = [maximum] 
            df_silence_scaled = self.data_scaler(df_silence.to_numpy())
            # Compute the mean of the scaled dataframe to get the score
            self.music_score, self.silence_score = round(df_music_scaled.mean(), 2), round(df_silence_scaled.mean(), 2)
        else:
            # This means headphones were put on the floor or something stable
            self.music_score, self.silence_score = 0.0, 0.0

        if self.try_again:
            sql = f"UPDATE standstillUser SET standstillUserID = {self.standstill_id}, age = {self.age}, musicScore = {self.music_score}, silenceScore = {self.silence_score}, feedbackMusic = {int(self.feedback_music.get())}, feedbackStandstill = {int(self.feedback_standstill.get())} WHERE id = {self.id}"
            self.mysql_write(sql)
            sql = f"UPDATE standstillRealTime SET standstillUserID = {self.standstill_id} WHERE standstillUserID = {self.id}"
            self.mysql_write(sql)
        else:
            # Update the age and the standstill scores of the user
            # self.mysql_check_connect()
            self.age = int(self.age_entry.get())
            sql = f"UPDATE standstillUser SET standstillUserID = {self.id}, age = {self.age}, musicScore = {self.music_score}, silenceScore = {self.silence_score}, feedbackMusic = {int(self.feedback_music.get())}, feedbackStandstill = {int(self.feedback_standstill.get())} WHERE id = {self.id}"
            self.mysql_write(sql)
        # Get the best scores
        self.cursor.execute("SELECT MAX(musicScore) FROM standstillUser")
        self.best_music_score = self.cursor.fetchall()[0][0]
        self.cursor.execute("SELECT MAX(silenceScore) FROM standstillUser")
        self.best_silence_score = self.cursor.fetchall()[0][0]

    def gratulerer(self):
        # Remove objects related to feedback and age
        self.after(0, self.feedback_music.destroy())
        self.after(0, self.feedback_standstill.destroy())
        self.after(0, self.age_entry_box.destroy())
        self.after(0, self.fortsett.destroy())
        self.canvas_bg.destroy()

        # Create new canvas
        self.canvas_bg = tkinter.Canvas(self)
        self.canvas_bg.pack(fill="both", expand=True)
        self.canvas_bg.create_image(
                                    self.winfo_screenwidth() // 2, 
                                    self.winfo_screenheight() // 2, 
                                    image=self.bg_gratulerer, 
                                    anchor="center",
                                    tag="background"
                                    )

        if self.language == 'no': 
            text = 'Gratulerer! Det var ganske stille!'
        else:
            text = 'Congratulations! That was quite still!'
        self.canvas_bg.create_text(
                                self.winfo_screenwidth() // 2, 
                                self.winfo_screenheight() // 2, 
                                text=text, 
                                width=self.winfo_screenwidth() // 2, 
                                font=('Oslo Sans Office', 50),
                                fill='white',
                                tag="gratulerer"
                                )
        
        # Wait 2 seconds and display scores
        self.after(2000, self.display_scores)

    def display_scores(self):
        self.canvas_bg.destroy()
        # Create new canvas
        self.canvas_bg = tkinter.Canvas(self)
        self.canvas_bg.pack(fill="both", expand=True)
        self.canvas_bg.create_image(
                                    self.winfo_screenwidth() // 2, 
                                    self.winfo_screenheight() // 2, 
                                    image=self.bg, 
                                    anchor="center",
                                    tag="background"
                                    )
        
        if self.music_score >= self.best_music_score or self.silence_score >= self.best_silence_score:
            # Play a celebration song and display a celebration image for the new best score!
            play = lambda: winsound.PlaySound('audio/celebration.wav', winsound.SND_ASYNC)
            # Start playing audio file in a thread
            th1 = Timer(0, play)
            th1.start()

            # Display congratulations tkinter label
            img = tkinter.PhotoImage(file='images/congrats.png', master=self)

            # self.congratulations = ttk.Label(self,
            #                                 image=img,
            #                                 text='',
            #                                 font=self.font,
            #                                 wraplength=self.winfo_screenwidth(), 
            #                                 compound='top'
            #                                 )
            # self.congratulations.pack()

        # Create text for displaying scores
        if self.language == 'no': 
            text = 'Gratulerer!'
        else:
            text = 'Congratulations!'
        self.canvas_bg.create_text(
                                self.winfo_screenwidth() // 2, 
                                self.winfo_screenheight() // 5.5, 
                                text=text, 
                                width=self.winfo_screenwidth() // 2, 
                                font=('Oslo Sans Office', 35),
                                fill='white',
                                tag="congrats"
                                )
        # Display the normal distributions with the scores
        self.plot_normal_distribution()

        # Delete the data from the user if the headphones were not put on a head
        if self.music_score == 0.0 or self.silence_score == 0.0:
            # self.mysql_check_connect()
            sql = f"DELETE FROM standstillUser WHERE standstillUserID = {self.id}"
            self.mysql_write(sql)
            sql = f"DELETE FROM standstillRealTime WHERE standstillUserID = {self.id}"
            self.mysql_write(sql)

        if self.language == 'no': 
            text = 'FERDIG'
        else:
            text = 'FINISH' 

        self.finish_button = tkinter.Button(self, 
                                      text=text, 
                                      bd=5,  
                                      font=self.font,
                                      height=2, 
                                      width=10,
                                      command=self.destroy_all)

        '''if self.language == 'no': 
            text = 'PRØV IGJEN'
        else:
            text = 'TRY AGAIN' 

        self.continue_button = tkinter.Button(self, 
                                      text=text, 
                                      bd=5,  
                                      font=self.font,
                                      height=2, 
                                      width=10,
                                      command=self.reset)

        # Display and place tkinter buttons
        self.continue_button.place(relx=0.6, rely=0.8, anchor='n')
        self.finish_button.place(relx=0.4, rely=0.8, anchor='n')'''
        self.finish_button.place(relx=0.5, rely=0.8, anchor='n')

    def plot_normal_distribution(self):
        # mu = 0.02 # mean of the scores
        # sigma = 1 # standard deviation of the scores
        # x1 = -1.5
        # x2 = 1.5
        # # calculate the z-transform
        # z1 = (x1 - mu) / sigma
        # z2 = (x2 - mu) / sigma

        # x = np.arange(z1, z2, 0.001) # range of x in spec
        # y = norm.pdf(x, 0, 1)
        # x_all = np.arange(-3.5, 3.5, 0.001) # entire range of x, both in and out of spec
        # y_all = norm.pdf(x_all,0,1)

        # Build the canvas
        fig, ax = plt.subplots(1,2, figsize=(10, 4)) 
        # Create the Tkinter canvas containing the Matplotlib figure
        self.canvas_score = FigureCanvasTkAgg(fig, self) 

        # Fetch all the music and silence scores
        self.cursor.execute("SELECT musicScore FROM standstillUser")
        music_scores = [i[0] for i in self.cursor.fetchall() if i[0] is not None]
        self.cursor.execute("SELECT silenceScore FROM standstillUser")
        silence_scores = [i[0] for i in self.cursor.fetchall() if i[0] is not None]
        # Plot the histograms
        ax[0].hist(music_scores, density=True, bins=15, alpha=0.6, color='lightblue')
        ax[1].hist(silence_scores, density=True, bins=15, alpha=0.6, color='lightblue')

        # Plot the Probability Density Function
        x = np.linspace(0, 100, 100) # between 0% and 100%
        
        # Fit a normal distribution to the data:
        mu_music, std_music = norm.fit(music_scores)
        mu_silence, std_silence = norm.fit(silence_scores)

        # Prevent division by zero
        if std_music == 0:
            std_music = 1e-6

        if std_silence == 0:
            std_silence = 1e-6

        pdf_music = norm.pdf(x, mu_music, std_music)
        pdf_silence = norm.pdf(x, mu_silence, std_silence)

        # Add the subplots
        ax[0].plot(x, pdf_music, linewidth=2)
        ax[0].axvline(self.music_score, color='r', label=f'Score: {self.music_score}', linewidth=1.5, linestyle='--')
        if self.language == 'no':
            ax[0].set_title(f'Du stod stille {self.music_score}% til musikk\nRekorden er {self.best_music_score}%', fontsize=15)
        else:
            ax[0].set_title(f'You stood still {self.music_score}% on music\nThe record is {self.best_music_score}%', fontsize=15)
        ax[0].legend()
        ax[0].set_axis_off()
        ax[1].plot(x, pdf_silence, linewidth=2)
        ax[1].axvline(self.silence_score, color='r', label=f'Score: {self.silence_score}', linewidth=1.5, linestyle='--')
        if self.language == 'no':
            ax[1].set_title(f'Du stod stille {self.silence_score}% til stillhet\nRekorden er {self.best_silence_score}%', fontsize=15)
        else:
            ax[1].set_title(f'You stood still {self.silence_score}% on silence\nThe record is {self.best_silence_score}%', fontsize=15)
        ax[1].legend()
        ax[1].set_axis_off()
        self.canvas_score.draw()
        self.canvas_score.get_tk_widget().place(relx=0.5, rely=0.5, anchor="center") # place the canvas on the Tkinter window

        # self.norm.plot(x_all,y_all)
        # self.norm.set_title('Du stod stille 76.5% til musikk Rekorden er 89%', fontsize=10)
        # self.norm.fill_between(x,y,0, alpha=0.3, color='b')
        # self.norm.fill_between(x_all,y_all,0, alpha=0.1)
        # self.norm.set_xlim([-3.5,3.5])
        # self.norm.set_axis_off()

    def destroy_all(self):
        self.quit()
        self.canvas_bg.destroy()
        self.destroy()

    def reset(self):
        if not self.try_again:
            self.standstill_id = self.id

        # Stop playing audio and kill audio thread
        winsound.PlaySound(None, winsound.SND_PURGE)
        self.th1.join()
        # Reset the counter
        self.counter = 6 
        self.try_again = True
        self.stop_commit = False

        # Destroy the gaussian curve from widget
        self.canvas_score.get_tk_widget().destroy()
        self.canvas_bg.delete("congrats")
        # Remove objects
        self.after(0, self.finish_button.destroy())
        # self.after(0, self.continue_button.destroy())
        # Add text for the countdown and start it
        self.counter_text = self.canvas_bg.create_text(
                                                       self.winfo_screenwidth() // 2, 
                                                       self.winfo_screenheight() // 2, 
                                                       width=self.winfo_screenwidth() // 1.5, 
                                                       font=('Oslo Sans Office', 150),
                                                       fill='white',
                                                       tag="countdown"
                                                       )
        # Start countdown
        self.after(0, self.tkinter_countdown)

        # Insert new row in the table
        # self.mysql_check_connect()
        sql = f"INSERT INTO standstillUser (language) VALUES ('{self.language}')"
        self.mysql_write(sql)
        self.cursor.execute("SELECT LAST_INSERT_ID()")
        self.id = self.cursor.fetchall()[0][0]

    def audio_canvas(self, audio_path):
        # Start threading audio
        play = lambda: winsound.PlaySound(audio_path, winsound.SND_ASYNC)
        # Call play function 
        self.th1 = Timer(0.0, play)
        self.th1.start()
        
        # Plot angular velocities in real-time
        self.update_canvas()
        
    def update_canvas(self):
        # Get head tracking data 
        self.head_tracker()

        # Required to update canvas
        self.canvas.draw()
        # Append angular velocities from head tracker to list
        self.xdata.append(self.w)
        # Throw away old signal data
        if len(self.xdata) > 50:
            self.xdata.pop(0)

        # Clear the plot so it will rescale to the new data
        self.plt.clear()
        self.plt.margins(x=0)
        self.plt.plot(self.xdata)
        self.plt.set_ylim([-0.1,1])
        if self.language == 'no':
            self.plt.set_title(f'Prøv å stå stille med {self.genre.upper()}!', fontsize=15)
        if self.language == 'en':
            self.plt.set_title(f'Try to stand still with {self.genre.upper()}!', fontsize=15)

        if self.stop_commit:
            return
        else:
            # Commit the data of the user to MySQL database
            # self.mysql_check_connect()
            data = (self.id, self.genre, float(self.w))
            sql = "INSERT INTO standstillRealTime (standstillUserID, genre, w) VALUES (%s, %s, %s)"
            self.cursor.execute(sql, data)
            self.database.commit()

        # Update plot every milliseconds
        self.after(1, self.update_canvas) 

    def head_tracker(self):
        # Run dispatcher to handle headtracking data with OSC
        dispatcher = Dispatcher()
        def default_handler(address: str, *args: List[Any]):
            self.Q2 = args
        dispatcher.set_default_handler(default_handler)

        # Listen to OSC messages from Bridgehead (OSC server)
        # 8000 is Supperware "Quaternion (composite)" profile
        # 100hz Tracking rate
        server = BlockingOSCUDPServer(("127.0.0.1", 8000), dispatcher)
        server.handle_request()

        # Define angular velocities of quaternions
        self.t2 = datetime.now().timestamp()
        self.dt = self.t2 - self.t1
        self.w = self.angular_velocities()
        # Update quaternions and time data
        self.Q1 = self.Q2 
        self.t1 = self.t2

    def angular_velocities(self):
        # Compute angular velocities of quaternions
        w = (2 / self.dt) * np.array([self.Q1[0]*self.Q2[1] - self.Q1[1]*self.Q2[0] - self.Q1[2]*self.Q2[3] + self.Q1[3]*self.Q2[2],
                                      self.Q1[0]*self.Q2[2] + self.Q1[1]*self.Q2[3] - self.Q1[2]*self.Q2[0] - self.Q1[3]*self.Q2[1],
                                      self.Q1[0]*self.Q2[3] - self.Q1[1]*self.Q2[2] + self.Q1[2]*self.Q2[1] - self.Q1[3]*self.Q2[0]])
        # Compute root mean square of angular velocities 
        # to get unique quantity of motion value
        w = np.sqrt(np.mean(w**2))
        return w

    def mysql_write(self, sql):
        try:
            self.cursor.execute(sql)
            self.database.commit()
        except:
            self.mysql_connect()
            self.cursor.execute(sql)
            self.database.commit()
        return

    def mysql_connect(self):
        self.database.close()
        time.sleep(0.5)
        print("reconnect")
        self.database = mysql.connector.connect(
                                    host="192.168.200.13",
                                    port="3306",
                                    password="i80q94PGZIPF1tyr!",
                                    #host="localhost",
                                    #password="i80q94PGZIPF1tyr",
                                    user="Joachim",
                                    database='uio'
                                    )
        self.cursor = self.database.cursor()
        return

def enumerate_row_column(iterable, num_cols):
    for idx, item in enumerate(iterable):
        row = idx // num_cols
        col = idx % num_cols
        yield row,col,item

class NumpadEntry(Entry):
    def __init__(self,parent=None,**kw):
        Entry.__init__(self,parent,**kw)
        self.bind('<FocusIn>',self.numpadEntry)
        self.bind('<FocusOut>',self.numpadExit)
        self.edited = False
    def numpadEntry(self,event):
        if self.edited == False:
            self['bg']= '#ffffcc'
            self.edited = True
            new = numPad(self)
        else:
            self.edited = False
    def numpadExit(self,event):
        self['bg']= '#ffffff'

class numPad(simpledialog.Dialog):
    def __init__(self,master=None,textVariable=None):
        self.top = Toplevel(master=master)
        self.top.protocol("WM_DELETE_WINDOW",self.ok)
        self.createWidgets()
        self.master = master
        
    def createWidgets(self):
        btn_list = ['7',  '8',  '9', '4',  '5',  '6', '1',  '2',  '3', '0',  'OK',  '<']
        # create and position all buttons with a for-loop
        btn = []
        # Use custom generator to give us row/column positions
        for r,c,label in enumerate_row_column(btn_list,3):
            # partial takes care of function and argument
            cmd = lambda x = label: self.click(x)
            # create the button
            cur = Button(self.top, text=label, width=10, height=5, command=cmd)
            # position the button
            cur.grid(row=r, column=c)                                              
            btn.append(cur)
        
    def click(self,label):
        print(label)
        if label == '<':
            currentText = self.master.get()
            self.master.delete(0, END)
            self.master.insert(0, currentText[:-1])
        elif label == 'OK':
            self.ok()
        else:
            currentText = self.master.get()
            self.master.delete(0, END)
            self.master.insert(0, currentText+label)
    def ok(self):
        self.top.destroy()
        # self.cur.destroy()
        # self.master.destroy()
        # self.top.master.focus()


if __name__ == "__main__":

    with open("config.yml", "r") as f:
        config = yaml.safe_load(f)
    
    db = mysql.connector.connect(
        host="localhost",
        user=config["sql"]["user"],
        passwd=config["sql"]["password"],
        database=config["sql"]["database"]
    )
    
    cursor = db.cursor()
    
    # This requres that the standstillUser and standstillRealTime tables are created.
    # See the sql-cheatsheet.py to see their format and how to make them.
    
    # Run the Supperware software for headtracking
    #subprocess.Popen(["bridgehead.exe"])

    # Start a dummy OSC Server that imitates the Headphones and sensor (bridgehead.exe app).
    #start sending fake OSC messages
    # import threading
    # from simulate_head_tracking_for_dev import start_osc_sender
    # sender_thread = threading.Thread(
    #     target=start_osc_sender,
    #     kwargs={"send_hz": 60},
    #     daemon=True
    # )
    # sender_thread.start()
    # print("OSC sender started!")
    # input("Press ENTER to quit\n")

    # Run the standstill competition
    while True:
        Standstill(database=db, cursor=cursor)
