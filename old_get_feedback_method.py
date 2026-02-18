    # def get_feedback(self):
    #     # Stop listening audio in the thread
    #     winsound.PlaySound(None, winsound.SND_PURGE)
        
    #     # Stop committing head tracking data and destroy the figure canvas from widget
    #     self.stop_commit = True
    #     self.canvas.get_tk_widget().destroy()
    #     # Create new canvas
    #     self.canvas_bg = tkinter.Canvas(self)
    #     self.canvas_bg.pack(fill="both", expand=True)
    #     self.canvas_bg.create_image(
    #                                 self.winfo_screenwidth() // 2, 
    #                                 self.winfo_screenheight() // 2, 
    #                                 image=self.bg, 
    #                                 anchor="center",
    #                                 tag="background"
    #                                 )
    #     # Get the feedback of the user with likert scale and age entry
    #     if self.language == 'no': 
    #         label = 'Hvor mye likte du musikken?'
    #     else:
    #         label = 'How do you liked the music?'
    #     self.feedback_music      = tkinter.Scale(
    #                                              self, 
    #                                              label=label, 
    #                                              font=self.font, 
    #                                              from_=0, 
    #                                              to=10, 
    #                                              orient=tkinter.HORIZONTAL, 
    #                                              width=50, 
    #                                              length=self.winfo_screenwidth() // 1.25, 
    #                                              showvalue=0, 
    #                                              tickinterval=1, 
    #                                              resolution=1
    #                                              )
    #     if self.language == 'no': 
    #         label = 'Hvor stille stod du?'
    #     else:
    #         label = 'How still did you stand?'
    #     self.feedback_standstill = tkinter.Scale(
    #                                              self, 
    #                                              label=label, 
    #                                              font=self.font, 
    #                                              from_=0, 
    #                                              to=10, 
    #                                              orient=tkinter.HORIZONTAL, 
    #                                              width=50, 
    #                                              length=self.winfo_screenwidth() // 1.25, 
    #                                              showvalue=0, 
    #                                              tickinterval=1, 
    #                                              resolution=1
    #                                              )
    #     if not self.try_again:
    #         if self.language == 'no': 
    #             text = "Hvor gammel er du?"
    #         else:
    #             text = "How old are you?" 
    #         self.canvas_bg.create_text(
    #                                 self.winfo_screenwidth() // 2, 
    #                                 self.winfo_screenheight() // 1.5, 
    #                                 text=text, 
    #                                 width=self.winfo_screenwidth() // 1.5, 
    #                                 font=self.font,
    #                                 fill='white',
    #                                 tag="age"
    #                                 )
    #         self.age_entry = StringVar()
    #         self.age_entry_box = NumpadEntry(self,textvariable=self.age_entry)
    #         #self.age_entry = tkinter.Entry(self, font=self.font)
    #         self.age_entry_box.place(relx=0.5, rely=0.8, anchor='center',height=40)

    #     if self.language == 'no': 
    #         text = "FORTSETT"
    #     else:
    #         text = "CONTINUE"        
    #     self.fortsett            = tkinter.Button(
    #                                               self, 
    #                                               bd=5, 
    #                                               text=text, 
    #                                               font=self.font, 
    #                                               compound="center", 
    #                                               command=self.combine_funcs(self.store_data, self.gratulerer)
    #                                               )
        
    #     # Place the feedback scales and the button
    #     self.feedback_music.place(relx=0.5, rely=0.3, anchor='center')
    #     self.feedback_standstill.place(relx=0.5, rely=0.5, anchor='center')
    #     self.fortsett.place(relx=0.5, rely=0.9, anchor='center')
        
    # def store_data(self, minimum=0.0, maximum=0.1, threshold=0.001):

    #     # Ping to wake up database!
    #     self.database.ping(reconnect=True, attempts=3, delay=1)

    #     # Get music and silence standstill real-time data of the user
    #     self.mysql_execute(f"SELECT * FROM standstillRealTime WHERE standstillUserID = {self.id} AND genre != 'silence'")
    #     df_music = pd.DataFrame(self.cursor.fetchall()).iloc[1: , 4:].astype(np.float32) # remove first row and four first columns and convert to absolute values
    #     self.mysql_execute(f"SELECT * FROM standstillRealTime WHERE standstillUserID = {self.id} AND genre = 'silence'")
    #     df_silence = pd.DataFrame(self.cursor.fetchall()).iloc[: , 4:].astype(np.float32) # remove four first columns and convert to absolute values
    #     # Check if the headphones were actually put on a head
    #     if df_music.median().to_numpy().mean() > threshold or df_silence.median().to_numpy().mean() > threshold:
    #         # Filter values above maximum to normalize score
    #         df_music[df_music > maximum] = maximum
    #         df_silence[df_silence > maximum] = maximum 
    #         # Add minimum and maximum values for scaling the dataframe
    #         df_music.loc[len(df_music.index)] = [minimum] 
    #         df_music.loc[len(df_music.index)+1] = [maximum] 
    #         df_music_scaled = self.data_scaler(df_music.to_numpy())
    #         df_silence.loc[len(df_silence.index)] = [minimum] 
    #         df_silence.loc[len(df_silence.index)+1] = [maximum] 
    #         df_silence_scaled = self.data_scaler(df_silence.to_numpy())
    #         # Compute the mean of the scaled dataframe to get the score
    #         self.music_score, self.silence_score = round(df_music_scaled.mean(), 2), round(df_silence_scaled.mean(), 2)
    #     else:
    #         # This means headphones were put on the floor or something stable
    #         self.music_score, self.silence_score = 0.0, 0.0

    #     if self.try_again:
    #         sql = f"UPDATE standstillUser SET standstillUserID = {self.standstill_id}, age = {self.age}, musicScore = {self.music_score}, silenceScore = {self.silence_score}, feedbackMusic = {int(self.feedback_music.get())}, feedbackStandstill = {int(self.feedback_standstill.get())} WHERE id = {self.id}"
    #         self.mysql_write(sql)
    #         sql = f"UPDATE standstillRealTime SET standstillUserID = {self.standstill_id} WHERE standstillUserID = {self.id}"
    #         self.mysql_write(sql)
    #     else:
    #         # Update the age and the standstill scores of the user
    #         # self.mysql_check_connect()
    #         self.age = int(self.age_entry.get())
    #         sql = f"UPDATE standstillUser SET standstillUserID = {self.id}, age = {self.age}, musicScore = {self.music_score}, silenceScore = {self.silence_score}, feedbackMusic = {int(self.feedback_music.get())}, feedbackStandstill = {int(self.feedback_standstill.get())} WHERE id = {self.id}"
    #         self.mysql_write(sql)
    #     # Get the best scores
    #     self.mysql_execute("SELECT MAX(musicScore) FROM standstillUser")
    #     self.best_music_score = self.cursor.fetchall()[0][0]
    #     self.mysql_execute("SELECT MAX(silenceScore) FROM standstillUser")
    #     self.best_silence_score = self.cursor.fetchall()[0][0]